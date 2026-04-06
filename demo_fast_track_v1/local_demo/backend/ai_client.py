from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any
from urllib import error, request

from .models import ClassroomEvaluateResponse, ClassroomIssueItem


_CONCEPT_PROFILE: dict[str, dict[str, str]] = {
    "峰": {
        "core": "尖、较高，像尖顶",
        "sample": "这是峰，因为它尖尖高高的。",
    },
    "岭": {
        "core": "连绵起伏，像一条山脊线",
        "sample": "这是岭，因为它连成一条起伏的线。",
    },
    "崖": {
        "core": "陡直，落差大",
        "sample": "这是崖，因为它很陡、几乎直上直下。",
    },
    "谷": {
        "core": "两山之间较低处",
        "sample": "这是谷，因为它在两边山中间更低。",
    },
}


class FoursAPIError(RuntimeError):
    pass


@dataclass
class FoursAPIClient:
    base_url: str = os.getenv("FOURSAPI_BASE_URL", "https://4sapi.com/v1").rstrip("/")
    api_key: str = os.getenv("FOURSAPI_API_KEY", "").strip()
    model: str = os.getenv("FOURSAPI_MODEL", "claude-sonnet-4-5-20250929").strip()
    thinking_model: str = os.getenv(
        "FOURSAPI_THINKING_MODEL",
        "claude-sonnet-4-5-20250929-thinking",
    ).strip()
    timeout_sec: float = float(os.getenv("FOURSAPI_TIMEOUT_SEC", "25"))

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def ask_why(self, selected_concept: str) -> tuple[str, str, str]:
        fallback_question = f"你选了“{selected_concept}”，可以用“因为……”说说理由吗？"
        fallback_encouragement = "你已经做出判断了，再把理由说完整就更棒。"
        concept = _CONCEPT_PROFILE.get(selected_concept)
        if not concept or not self.enabled:
            return fallback_question, fallback_encouragement, "fallback_rules"

        prompt = (
            f"孩子在“山的不同叫法”里选择了“{selected_concept}”，核心特征是：{concept['core']}。\n"
            "请只输出两行，且每行不超过22个字：\n"
            "提问：...\n"
            "鼓励：..."
        )
        try:
            text = self._chat_text(prompt, use_thinking=False)
            question = self._extract_prefixed_line(text, "提问")
            encouragement = self._extract_prefixed_line(text, "鼓励")
            if question and encouragement:
                return question, encouragement, "4sapi"
        except Exception:
            pass
        return fallback_question, fallback_encouragement, "fallback_rules"

    def evaluate_answer(self, selected_concept: str, student_answer: str) -> ClassroomEvaluateResponse:
        if not self.enabled:
            return self._rule_evaluate(selected_concept, student_answer)

        concept = _CONCEPT_PROFILE.get(selected_concept, _CONCEPT_PROFILE["峰"])
        prompt = (
            "你是儿童课堂评估助手。请严格基于“目标词”和“孩子原话”判定，不要输出代码，不要输出XML。\n"
            f"目标词：{selected_concept}\n"
            f"目标特征：{concept['core']}\n"
            f"孩子原话：{student_answer}\n"
            "请严格输出7行，不要多余内容：\n"
            "判断：正确/部分正确/不正确\n"
            "是否正确：是/否\n"
            "做得好：一句话\n"
            "问题点：一句话（若无则写“无”）\n"
            "建议句：给出改写后的完整句\n"
            "鼓励：一句温和鼓励\n"
            "下一步：一句可执行提示"
        )

        try:
            text = self._chat_text(prompt, use_thinking=True)
            parsed = self._parse_full_model_eval(text, selected_concept, concept["sample"])
            parsed.engine = "4sapi_full_model"
            return parsed
        except Exception:
            return self._rule_evaluate(selected_concept, student_answer)

    def _parse_full_model_eval(
        self,
        text: str,
        selected_concept: str,
        fallback_sentence: str,
    ) -> ClassroomEvaluateResponse:
        cleaned = self._sanitize_text(text)
        judgement = self._extract_prefixed_line(cleaned, "判断")
        is_correct_text = self._extract_prefixed_line(cleaned, "是否正确")
        strengths_text = self._extract_prefixed_line(cleaned, "做得好")
        issues_text = self._extract_prefixed_line(cleaned, "问题点")
        corrected_sentence = self._extract_prefixed_line(cleaned, "建议句")
        feedback_to_child = self._extract_prefixed_line(cleaned, "鼓励")
        next_hint = self._extract_prefixed_line(cleaned, "下一步")

        if not judgement:
            raise FoursAPIError("missing judgement")
        if not corrected_sentence:
            corrected_sentence = fallback_sentence
        if not feedback_to_child:
            raise FoursAPIError("missing feedback")
        if not next_hint:
            raise FoursAPIError("missing next_hint")

        strengths = self._split_points(strengths_text)
        issues = self._to_issue_items(issues_text, selected_concept)

        normalized_judgement = judgement
        if normalized_judgement not in {"正确", "部分正确", "不正确"}:
            if "正确" in normalized_judgement and "部分" in normalized_judgement:
                normalized_judgement = "部分正确"
            elif "不正确" in normalized_judgement or "错误" in normalized_judgement:
                normalized_judgement = "不正确"
            elif "正确" in normalized_judgement:
                normalized_judgement = "正确"
            else:
                normalized_judgement = "部分正确"

        is_correct = False
        if is_correct_text:
            is_correct = ("是" in is_correct_text) or ("true" in is_correct_text.lower())
        else:
            is_correct = normalized_judgement == "正确"

        return ClassroomEvaluateResponse(
            is_correct=is_correct,
            overall_judgement=normalized_judgement,
            strengths=strengths,
            issues=issues,
            corrected_sentence=corrected_sentence,
            feedback_to_child=feedback_to_child,
            next_hint=next_hint,
            engine="4sapi_full_model",
        )

    @staticmethod
    def _split_points(text: str) -> list[str]:
        if not text:
            return []
        raw = re.split(r"[；;。]|\\n", text)
        points = [x.strip(" -，,。；;") for x in raw if x.strip(" -，,。；;")]
        return points[:2]

    def _to_issue_items(self, issues_text: str, selected_concept: str) -> list[ClassroomIssueItem]:
        if not issues_text:
            return []
        if any(x in issues_text for x in ["无", "没有", "无明显问题"]):
            return []

        points = self._split_points(issues_text)
        items: list[ClassroomIssueItem] = []
        for p in points[:2]:
            issue_type = "expression"
            if any(k in p for k in ["概念", "特征", selected_concept, "不对应", "判断"]):
                issue_type = "concept"
            items.append(ClassroomIssueItem(type=issue_type, message=p))
        return items

    def _rule_evaluate(self, selected_concept: str, student_answer: str) -> ClassroomEvaluateResponse:
        concept = _CONCEPT_PROFILE.get(selected_concept, _CONCEPT_PROFILE["峰"])
        answer = (student_answer or "").strip()
        has_reason = "因为" in answer

        if selected_concept == "峰":
            keyword_ok = ("尖" in answer) or ("高" in answer)
        elif selected_concept == "岭":
            keyword_ok = ("连" in answer) or ("起伏" in answer) or ("山脊" in answer)
        elif selected_concept == "崖":
            keyword_ok = ("陡" in answer) or ("直" in answer) or ("落差" in answer)
        elif selected_concept == "谷":
            keyword_ok = ("中间" in answer) or ("低" in answer) or ("两山" in answer)
        else:
            keyword_ok = False

        is_correct = keyword_ok and has_reason
        judgement = "正确" if is_correct else ("部分正确" if (keyword_ok or has_reason) else "不正确")
        issues: list[ClassroomIssueItem] = []
        if not keyword_ok:
            issues.append(
                ClassroomIssueItem(
                    type="concept",
                    message=f"你选的是“{selected_concept}”，理由要体现它的关键特征：{concept['core']}。",
                )
            )
        if not has_reason:
            issues.append(
                ClassroomIssueItem(
                    type="expression",
                    message="建议加上“因为……”，让句子更完整。",
                )
            )

        return ClassroomEvaluateResponse(
            is_correct=is_correct,
            overall_judgement=judgement,
            strengths=["你已经在尝试解释理由。"] if has_reason else [],
            issues=issues,
            corrected_sentence=concept["sample"],
            feedback_to_child="你已经有思路了，我们再把关键点说准确一点。",
            next_hint=f"请按这个句式再说一遍：{concept['sample']}",
            engine="fallback_rules",
        )

    def _chat_text(self, prompt: str, use_thinking: bool) -> str:
        if not self.enabled:
            raise FoursAPIError("FOURSAPI_API_KEY is not set")

        model = self.thinking_model if use_thinking and self.thinking_model else self.model
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "你是中文课堂助手。只回答当前任务。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 300,
            "stream": False,
        }
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = request.Request(
            url=f"{self.base_url}/chat/completions",
            data=raw,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self.timeout_sec) as resp:
                response_obj = json.loads(resp.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise FoursAPIError(f"http error {exc.code}: {detail}") from exc
        except Exception as exc:
            raise FoursAPIError(f"request failed: {exc}") from exc

        return self._extract_content(response_obj)

    @staticmethod
    def _extract_content(response_obj: dict[str, Any]) -> str:
        choices = response_obj.get("choices") or []
        if not choices:
            raise FoursAPIError("empty choices")
        message = choices[0].get("message") or {}
        content = message.get("content")
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
            joined = "\n".join(parts).strip()
            if joined:
                return joined
        raise FoursAPIError("content format unsupported")

    @staticmethod
    def _sanitize_text(text: str) -> str:
        cleaned = (text or "").strip()
        cleaned = cleaned.replace("```", "")
        cleaned = re.sub(r"<[^>]+>", "", cleaned)
        return cleaned.strip()

    @staticmethod
    def _extract_prefixed_line(text: str, prefix: str) -> str:
        pattern = re.compile(rf"^{re.escape(prefix)}\s*[：:]\s*(.+)$")
        for line in text.splitlines():
            one = line.strip()
            match = pattern.match(one)
            if match:
                return match.group(1).strip()
        return ""
