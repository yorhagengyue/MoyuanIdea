# Moyuan 本地课堂 Demo（山主题）

## 这是什么 Demo

这是 **Moyuan「课堂受控 AI」功能的本地演示版**，主题固定为“山的不同叫法”。
它不是完整产品，也不是家长端/角色端总集，而是专门用来证明课堂核心链路是否真实可用：

1. 老师导入讲解（今天学什么）
2. 孩子在四张真实山形图中做选择（峰 / 岭 / 崖 / 谷）
3. 孩子说出“为什么”
4. AI 给出即时反馈（判断 + 问题点 + 建议句 + 下一步引导）

一句话定位：**这是“课堂里 AI 真能用”的功能 Demo。**

---

## Demo 目标（给老板/团队看的价值）

- 证明“课堂第一，AI第二”：流程可控，不会把课堂带跑。
- 证明“不是玩具交互”：孩子回答后，AI 能指出哪里对、哪里错、怎么改。
- 证明“低龄儿童可用”：页面指令简单、反馈可理解、按钮少、路径短。

---

## 当前实现范围

### 已覆盖

- 单页课堂主舞台（不跳页）
- 导入 -> 选图 -> 说理由 -> 即时反馈 完整闭环
- 选项图片统一由 `gemini-3.1-flash-image-preview` 生成并本地缓存
- 课堂问答与判定使用真实 AI 接口（带失败兜底）
- 语音输入 + 手动输入双通道

### 不在本 Demo 范围

- 家长成长卷轴页面
- 孩子角色课后延续页面
- 机构后台管理、权限、多班级运营能力

---

## 关键接口

- `GET /api/lesson-pack`
- `GET /api/classroom/option-images`（可带 `?refresh=true` 强制重生图）
- `POST /api/classroom/ask-why`
- `POST /api/classroom/evaluate`

---

## 本地运行

在 `demo_fast_track_v1/local_demo` 目录执行：

```powershell
python -m pip install -r .\backend\requirements.txt
```

设置环境变量：

```powershell
$env:FOURSAPI_API_KEY = "你的课堂对话 key"
$env:FOURSAPI_MODEL = "claude-sonnet-4-5-20250929"
$env:FOURSAPI_THINKING_MODEL = "claude-sonnet-4-5-20250929-thinking"

$env:FOURSAPI_GEMINI_API_KEY = "你的图片生成 key"
$env:GEMINI_IMAGE_MODEL = "gemini-3.1-flash-image-preview"
```

启动：

```powershell
.\start_demo.ps1
```

浏览器打开：`http://127.0.0.1:8000`

---

## 演示验收标准（最小）

- 能跑通 1 次正确回答流程
- 能跑通 1 次错误回答流程
- 四个选项必须是真实生成图，不得回退廉价 icon
- AI 反馈必须同时包含：
  - 判断
  - 问题点
  - 建议句
  - 下一步引导

---

## 备注

图片缓存目录：`frontend/generated_options/`
