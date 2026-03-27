# Phase 2 实施总方案：应试（PSLE + DSA）

更新时间：2026-03-25

## 总目标

第二部分正式定义为“应试系统”，分成两条独立业务线：

1. `PSLE 口语冲刺 Agent`：3-4 天内完成 3 节高强度训练，目标是口语表现提升一个档次。  
2. `DSA 趋势研究 Agent`：持续追踪各学校 DSA 年度变化，帮助老师和家长把“今年作品该怎么改”讲清楚。

## 为什么要拆成两条线

这两条线的目标完全不同。PSLE 线追求“严格出分”，核心是扣分机制和短期提分。DSA 线追求“信息优势”，核心是年度变化跟踪和申请策略建议。放在一个模块里会互相干扰，所以在接口、数据和报告层全部拆开。

## PSLE 线的落地重点

- 评分必须严格，不达标就扣分。  
- 分数默认仅老师可见（`teacher_only`），支持切换学生可见（`student_visible`）。  
- 三节课固定节奏：基线诊断 -> 定向强化 -> 全真模拟。  
- 每节课输出扣分明细，第三节课输出“是否达成一个档次提升”。

## DSA 线的落地重点

- 按“学校 x 年份”持续采集官方和校方页面。  
- 自动识别变化：时间窗、门槛、流程、作品要求。  
- 生成老师可讲解版本：今年变化、风险点、作品调整建议。  
- 优先跟踪艺术方向（Visual Arts / AEP / Portfolio）。

## 本轮交付清单

- `API_SPEC.yaml`：PSLE + DSA 统一 API 草案  
- `PSLE_STRICT_SCORING_SPEC.md`：PSLE 严格评分规则  
- `PSLE_SCORING_RUBRIC_V1.json`：可被系统直接读取的评分模板  
- `DSA_RESEARCH_ENGINE_SPEC.md`：DSA 研究 Agent 规格  
- `DSA_TREND_BASELINE_2026-03-25.md`：已抓取官方来源基线  
- `DSA_SCHOOL_TRACKER_TEMPLATE.csv`：学校年度追踪模板
