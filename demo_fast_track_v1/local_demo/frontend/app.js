const state = {
  lessonPack: null,
  classroomStage: "intro",
  selectedConcept: "",
  lastTranscript: "",
  busy: false,
  optionImageTask: null,
};

const el = {
  lessonStageLabel: document.getElementById("lessonStageLabel"),
  lessonIntroTitle: document.getElementById("lessonIntroTitle"),
  lessonImage: document.getElementById("lessonImage"),
  nodePrompt: document.getElementById("nodePrompt"),
  beginInteractionBtn: document.getElementById("beginInteractionBtn"),
  restartBtn: document.getElementById("restartBtn"),
  optionGrid: document.getElementById("optionGrid"),
  whyPrompt: document.getElementById("whyPrompt"),
  answerArea: document.getElementById("answerArea"),
  speechBtn: document.getElementById("speechBtn"),
  manualText: document.getElementById("manualText"),
  submitTextBtn: document.getElementById("submitTextBtn"),
  recognizedText: document.getElementById("recognizedText"),
  feedbackPanel: document.getElementById("feedbackPanel"),
  feedbackJudgement: document.getElementById("feedbackJudgement"),
  feedbackStrengths: document.getElementById("feedbackStrengths"),
  feedbackIssues: document.getElementById("feedbackIssues"),
  feedbackCorrection: document.getElementById("feedbackCorrection"),
  feedbackNext: document.getElementById("feedbackNext"),
  feedbackEncourage: document.getElementById("feedbackEncourage"),
};

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

const conceptOptions = [
  { key: "峰", subtitle: "尖尖高高", imageUrl: "" },
  { key: "岭", subtitle: "连绵起伏", imageUrl: "" },
  { key: "崖", subtitle: "陡直落差", imageUrl: "" },
  { key: "谷", subtitle: "两山低地", imageUrl: "" },
];

function setBusy(busy) {
  state.busy = busy;
  const disabled = Boolean(busy);
  el.beginInteractionBtn.disabled = disabled;
  el.restartBtn.disabled = disabled;
  el.speechBtn.disabled = disabled;
  el.submitTextBtn.disabled = disabled;
  el.optionGrid.querySelectorAll("button").forEach((button) => {
    button.disabled = disabled;
  });
}

function setStage(stage) {
  state.classroomStage = stage;
  const labels = {
    intro: "课前导入",
    choice: "选图判断",
    reason: "说出理由",
    feedback: "即时反馈",
  };
  el.lessonStageLabel.textContent = labels[stage] || stage;
}

function normalizeSentence(text) {
  const value = (text || "").trim();
  if (!value) return "";
  return /[。！？.!?]$/.test(value) ? value : `${value}。`;
}

function markSelectedCard(selectedKey) {
  el.optionGrid.querySelectorAll(".option-card").forEach((card) => {
    card.classList.toggle("is-selected", card.dataset.key === selectedKey);
  });
}

function setPrompt(message) {
  el.nodePrompt.textContent = message;
}

function clearFeedbackPanel() {
  el.feedbackJudgement.textContent = "-";
  el.feedbackStrengths.textContent = "-";
  el.feedbackIssues.textContent = "-";
  el.feedbackCorrection.textContent = "-";
  el.feedbackNext.textContent = "-";
  el.feedbackEncourage.textContent = "-";

  el.feedbackPanel.classList.remove("feedback-ok", "feedback-warn", "feedback-error", "is-updated");
}

function resetFlow() {
  setStage("intro");
  state.selectedConcept = "";
  state.lastTranscript = "";

  el.beginInteractionBtn.classList.remove("hidden");
  el.optionGrid.classList.add("hidden");
  el.whyPrompt.classList.add("hidden");
  el.answerArea.classList.add("hidden");
  el.manualText.value = "";
  el.recognizedText.textContent = "-";

  setPrompt("先看图，老师做简短介绍：今天会认识峰、岭、崖、谷。");
  clearFeedbackPanel();
}

async function fetchJson(url, init) {
  const response = await fetch(url, init);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

async function postJson(url, body) {
  return fetchJson(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

async function ensureOptionImages(force = false) {
  if (state.optionImageTask && !force) return state.optionImageTask;

  const query = force ? "?refresh=true" : "";
  state.optionImageTask = fetchJson(`/api/classroom/option-images${query}`)
    .then((payload) => {
      const mapped = {};
      (payload.items || []).forEach((item) => {
        mapped[item.key] = item;
      });
      conceptOptions.forEach((option) => {
        if (mapped[option.key]) {
          option.subtitle = mapped[option.key].subtitle || option.subtitle;
          option.imageUrl = mapped[option.key].image_url || "";
        }
      });
      return payload;
    })
    .finally(() => {
      state.optionImageTask = null;
    });

  return state.optionImageTask;
}

function renderOptions() {
  el.optionGrid.innerHTML = "";

  conceptOptions.forEach((option, index) => {
    const card = document.createElement("button");
    card.className = "option-card";
    card.type = "button";
    card.dataset.key = option.key;
    card.style.setProperty("--i", String(index));

    const mediaHtml = option.imageUrl
      ? `<img class="option-image" src="${option.imageUrl}" alt="${option.key}示意图" loading="lazy" />`
      : '<div class="option-image option-image-fallback">图片生成中...</div>';

    card.innerHTML = `
      ${mediaHtml}
      <span class="option-title">${option.key}</span>
      <span class="option-subtitle">${option.subtitle}</span>
    `;

    card.addEventListener("click", async () => {
      if (state.busy) return;
      state.selectedConcept = option.key;
      markSelectedCard(option.key);

      setStage("reason");
      el.whyPrompt.classList.remove("hidden");
      el.answerArea.classList.remove("hidden");
      el.whyPrompt.textContent = `你选择了“${option.key}”，正在生成追问...`;
      el.manualText.focus();
      await fetchAskWhyPrompt(option.key);
    });

    el.optionGrid.appendChild(card);
  });
}

function applyFeedbackTone(result) {
  el.feedbackPanel.classList.remove("feedback-ok", "feedback-warn", "feedback-error");
  if (result.is_correct === true) {
    el.feedbackPanel.classList.add("feedback-ok");
    return;
  }

  if (result.overall_judgement === "不正确") {
    el.feedbackPanel.classList.add("feedback-error");
    return;
  }

  el.feedbackPanel.classList.add("feedback-warn");
}

function renderFeedback(result) {
  const strengths = (result.strengths || []).filter(Boolean);
  const issues = (result.issues || []).map((item) => item.message).filter(Boolean);

  el.feedbackJudgement.textContent = result.overall_judgement || "部分正确";
  el.feedbackStrengths.textContent = strengths.length ? strengths.join("；") : "你很愿意表达，这非常好。";
  el.feedbackIssues.textContent = issues.length ? issues.join("；") : "目前没有明显问题。";
  el.feedbackCorrection.textContent = result.corrected_sentence || "请再说一遍完整句。";
  el.feedbackNext.textContent = result.next_hint || "再试一次，用“因为……”说完整理由。";
  el.feedbackEncourage.textContent = result.feedback_to_child || "你已经做得很好，继续加油。";

  applyFeedbackTone(result);
  el.feedbackPanel.classList.remove("is-updated");
  requestAnimationFrame(() => {
    el.feedbackPanel.classList.add("is-updated");
  });
}

async function beginInteraction() {
  setStage("choice");
  el.beginInteractionBtn.classList.add("hidden");
  el.optionGrid.classList.remove("hidden");
  setPrompt("正在加载AI生成的选项图片...");

  try {
    setBusy(true);
    await ensureOptionImages(false);
    renderOptions();
    setPrompt("请从下面四个选项里，选你觉得最像这张图里重点山形的一个。");
  } catch {
    renderOptions();
    setPrompt("选项图片加载失败，请点击“重新开始”后再试一次。");
  } finally {
    setBusy(false);
  }
}

async function fetchAskWhyPrompt(selectedConcept) {
  try {
    setBusy(true);
    const result = await postJson("/api/classroom/ask-why", { selected_concept: selectedConcept });
    const question = result.question || `你选了“${selectedConcept}”，为什么这么选？`;
    const encouragement = result.encouragement || "把理由说完整一点会更好。";
    el.whyPrompt.textContent = `${question} ${encouragement}`;
  } catch {
    el.whyPrompt.textContent = `你选了“${selectedConcept}”，为什么这么选？请用“因为……”说完整句。`;
  } finally {
    setBusy(false);
  }
}

async function submitAnswer(text) {
  if (state.busy) return;

  if (!state.selectedConcept) {
    el.feedbackIssues.textContent = "请先选一个图片选项，再回答为什么。";
    return;
  }

  const answer = normalizeSentence(text);
  if (!answer) {
    el.feedbackIssues.textContent = "请先说出你的理由。";
    return;
  }

  setStage("feedback");
  state.lastTranscript = answer;
  el.recognizedText.textContent = answer;
  el.feedbackJudgement.textContent = "AI分析中";
  el.feedbackIssues.textContent = "正在分析你的回答...";

  try {
    setBusy(true);
    const result = await postJson("/api/classroom/evaluate", {
      selected_concept: state.selectedConcept,
      student_answer: answer,
    });
    renderFeedback(result);
  } catch {
    el.feedbackJudgement.textContent = "暂时不可用";
    el.feedbackIssues.textContent = "当前分析失败，请再试一次。";
  } finally {
    setBusy(false);
  }
}

function setupSpeech() {
  if (!SpeechRecognition) {
    el.speechBtn.disabled = true;
    el.speechBtn.textContent = "当前浏览器不支持语音";
    return;
  }

  const recognizer = new SpeechRecognition();
  recognizer.lang = "zh-CN";
  recognizer.interimResults = false;
  recognizer.maxAlternatives = 1;

  recognizer.onresult = async (event) => {
    const transcript = event.results?.[0]?.[0]?.transcript || "";
    await submitAnswer(transcript);
  };

  recognizer.onerror = () => {
    el.feedbackIssues.textContent = "语音录入失败，请改用手动输入。";
  };

  el.speechBtn.addEventListener("click", () => {
    if (state.busy) return;
    if (!state.selectedConcept) {
      el.feedbackIssues.textContent = "请先选择图片，再开始语音。";
      return;
    }
    recognizer.start();
  });
}

async function init() {
  try {
    const lessonPack = await fetchJson("/api/lesson-pack");
    state.lessonPack = lessonPack;
    el.lessonIntroTitle.textContent = `今天我们来学习：${lessonPack.theme || "山的不同叫法"}`;
    el.lessonImage.src = "/assets/mountain";
  } catch {
    setPrompt("课包加载失败，请检查服务状态。");
  }

  resetFlow();
  setupSpeech();

  // Pre-warm generated cards so children see real imagery immediately.
  ensureOptionImages(false).catch(() => {});

  el.beginInteractionBtn.addEventListener("click", beginInteraction);
  el.restartBtn.addEventListener("click", resetFlow);
  el.submitTextBtn.addEventListener("click", async () => {
    await submitAnswer(el.manualText.value);
    el.manualText.value = "";
  });
}

init();
