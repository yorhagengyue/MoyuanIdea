from __future__ import annotations

from difflib import SequenceMatcher
import re

from .models import ErrorItem, ScoreBundle, ScoreResponse, WordTimestamp


_PUNCT_RE = re.compile(r"[，。！？；：、“”‘’（）()\[\]【】,.!?;:\-_\s]+")


def normalize_text(text: str) -> str:
    cleaned = _PUNCT_RE.sub("", text or "")
    return cleaned.strip()


def tokenize_zh(text: str) -> list[str]:
    return list(normalize_text(text))


def timing_char_slots(timing: list[WordTimestamp], fallback_count: int) -> list[tuple[float, float]]:
    slots: list[tuple[float, float]] = []
    for item in timing:
        chars = list(normalize_text(item.word))
        if not chars:
            continue
        duration = max(item.end - item.start, 0.001)
        step = duration / len(chars)
        for idx, _ in enumerate(chars):
            start = item.start + idx * step
            end = start + step
            slots.append((round(start, 3), round(end, 3)))

    if slots:
        return slots

    # No timing provided: synthesize slots so UI still has stable ranges.
    synth: list[tuple[float, float]] = []
    cursor = 0.0
    total = max(fallback_count, 1)
    for _ in range(total):
        synth.append((round(cursor, 3), round(cursor + 0.24, 3)))
        cursor += 0.24
    return synth


def pause_errors(timing: list[WordTimestamp], threshold: float = 0.6) -> list[ErrorItem]:
    items: list[ErrorItem] = []
    if len(timing) < 2:
        return items
    sorted_timing = sorted(timing, key=lambda x: x.start)
    for i in range(1, len(sorted_timing)):
        gap = sorted_timing[i].start - sorted_timing[i - 1].end
        if gap > threshold:
            items.append(
                ErrorItem(
                    type="pause",
                    start=round(sorted_timing[i - 1].end, 3),
                    end=round(sorted_timing[i].start, 3),
                    reason=f"出现{gap:.2f}s停顿，影响流利度。",
                )
            )
    return items


def score_with_reference(
    transcript: str,
    reference_text: str,
    timing: list[WordTimestamp],
) -> ScoreResponse:
    rec_tokens = tokenize_zh(transcript)
    ref_tokens = tokenize_zh(reference_text)
    slots = timing_char_slots(timing, len(rec_tokens))

    matcher = SequenceMatcher(a=ref_tokens, b=rec_tokens)
    errors: list[ErrorItem] = []
    sub_count = 0
    del_count = 0
    ins_count = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue

        if tag == "replace":
            pair_count = min(i2 - i1, j2 - j1)
            for offset in range(pair_count):
                b_idx = j1 + offset
                start, end = slots[min(b_idx, len(slots) - 1)]
                errors.append(
                    ErrorItem(
                        type="substitution",
                        expected=ref_tokens[i1 + offset],
                        recognized=rec_tokens[b_idx],
                        start=start,
                        end=end,
                        reason=f"“{ref_tokens[i1 + offset]}”被读成“{rec_tokens[b_idx]}”。",
                    )
                )
                sub_count += 1

            if (i2 - i1) > pair_count:
                for ref_idx in range(i1 + pair_count, i2):
                    errors.append(
                        ErrorItem(
                            type="omission",
                            expected=ref_tokens[ref_idx],
                            recognized=None,
                            reason=f"漏读“{ref_tokens[ref_idx]}”。",
                        )
                    )
                    del_count += 1

            if (j2 - j1) > pair_count:
                for b_idx in range(j1 + pair_count, j2):
                    start, end = slots[min(b_idx, len(slots) - 1)]
                    errors.append(
                        ErrorItem(
                            type="insertion",
                            expected=None,
                            recognized=rec_tokens[b_idx],
                            start=start,
                            end=end,
                            reason=f"多读“{rec_tokens[b_idx]}”。",
                        )
                    )
                    ins_count += 1

        elif tag == "delete":
            for ref_idx in range(i1, i2):
                errors.append(
                    ErrorItem(
                        type="omission",
                        expected=ref_tokens[ref_idx],
                        recognized=None,
                        reason=f"漏读“{ref_tokens[ref_idx]}”。",
                    )
                )
                del_count += 1

        elif tag == "insert":
            for b_idx in range(j1, j2):
                start, end = slots[min(b_idx, len(slots) - 1)]
                errors.append(
                    ErrorItem(
                        type="insertion",
                        expected=None,
                        recognized=rec_tokens[b_idx],
                        start=start,
                        end=end,
                        reason=f"多读“{rec_tokens[b_idx]}”。",
                    )
                )
                ins_count += 1

    pause_items = pause_errors(timing)
    errors.extend(pause_items)

    ref_len = max(len(ref_tokens), 1)
    total_err = sub_count + del_count + ins_count
    accuracy = max(0.0, 100.0 * (1 - total_err / ref_len))
    completeness = max(0.0, 100.0 * (1 - del_count / ref_len))
    pause_penalty = min(35.0, len(pause_items) * 8.0)
    fluency = max(0.0, 100.0 - pause_penalty)
    overall = round(accuracy * 0.5 + fluency * 0.3 + completeness * 0.2, 1)

    if total_err == 0 and not pause_items:
        feedback = "这次读得很稳，继续保持完整表达。"
    else:
        major = errors[0].reason if errors else "表达可以更完整。"
        feedback = f"建议先修正：{major} 再进行一轮完整句复述。"

    scores = ScoreBundle(
        accuracy=round(accuracy, 1),
        fluency=round(fluency, 1),
        completeness=round(completeness, 1),
        overall=overall,
    )
    return ScoreResponse(errors=errors, scores=scores, feedback=feedback)


def score_without_reference(transcript: str, timing: list[WordTimestamp]) -> ScoreResponse:
    tokens = tokenize_zh(transcript)
    pause_items = pause_errors(timing)

    # Heuristic scoring for free speaking in demo mode.
    completeness = 100.0 if len(tokens) >= 10 else 70.0 if len(tokens) >= 6 else 45.0
    accuracy = 90.0 if len(tokens) >= 6 else 78.0
    fluency = max(0.0, 100.0 - min(40.0, len(pause_items) * 10.0))
    overall = round(accuracy * 0.4 + fluency * 0.35 + completeness * 0.25, 1)

    feedback = (
        "表达意图清楚，建议再补一句“因为……所以……”让句子更完整。"
        if len(tokens) < 10
        else "表达已较完整，可继续提升流畅度和细节描述。"
    )

    scores = ScoreBundle(
        accuracy=round(accuracy, 1),
        fluency=round(fluency, 1),
        completeness=round(completeness, 1),
        overall=overall,
    )
    return ScoreResponse(errors=pause_items, scores=scores, feedback=feedback)


def score_transcript(
    transcript: str,
    reference_text: str | None,
    timing: list[WordTimestamp],
) -> ScoreResponse:
    if reference_text and normalize_text(reference_text):
        return score_with_reference(transcript, reference_text, timing)
    return score_without_reference(transcript, timing)
