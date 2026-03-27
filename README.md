# Moyuan Culture AI 系统需求记录（V0.4）

> 更新时间：2026-03-25
> 状态：关键信息已收口，可进入投资人方案输出

## 1. 项目背景

本项目由外包团队为 Moyuan Culture 设计并落地数字化系统，目标覆盖：

- 教学与教务后端管理（老师/教务/管理者）
- 家长客户端体验提升
- AI 能力引入（自动排课、智能签到、家长沟通自动化）

当前机构尚未使用成熟 SaaS 系统，流程依赖纸质、Excel、微信/WhatsApp 等工具，存在明显的效率和管理可视化问题。

## 2. 系统总体划分（已确认）

### 2.1 后端管理系统（老师/教务/管理者）

核心目标：减少老师行政时间，并让管理层可视化掌握教学执行。

当前痛点：

- 排课主要依赖纸质或 Excel，手工成本高、易出错
- 签到和出勤记录分散
- 教学执行情况（备课、上课过程）缺乏结构化记录

预期能力（第一阶段方向）：

- 自动化排课
- 智能签到与学生出勤记录打通
- 教学过程记录（备课情况、上课情况）
- 管理者查看老师教学执行与学生参与情况
- 分角色权限控制（老师 / 教务 / 管理者）

### 2.2 家长客户端（家长侧）

核心目标：显著提升家长体验与满意度。

已确认重点：

- 家长端第一形态：APP（移动端优先）
- 日程/课程信息可视化，接近日历式一眼可读
- 排课与签到结果自动联动到家长沟通
- 保留作品集与课后反馈能力（重要模块）

## 3. 机构当前业务规模（已确认）

- 校区数：3 个
- 课程类型：中国文化/国画方向为主
- 学生年龄段：7-9 岁
- 学生规模：每校区约 50 人（总计约 150 人）
- 师资规模：总计约 9-12 位老师

## 4. 当前系统与工具现状（已确认）

- 尚无 SaaS 管理系统
- 依赖工具：纸质记录、Excel、微信/WhatsApp
- 暂无重点外部系统对接需求，先完成内部流程数字化替代

## 5. AI 优先场景（已确认 Top 3）

1. 智能排课编排助手（最高优先）
- 根据老师时间、班级容量、校区资源自动生成排课
- 自动检测冲突并给出修正建议

2. 智能签到体系（低龄友好）
- 不依赖学生手机，不以二维码作为唯一入口
- 优先老师端快速点名/勾选，后续可扩展实体卡/设备辅助

3. 家长沟通助手（与排课/签到联动）
- 排课和签到完成后自动生成家长通知草稿
- 移动端可视化展示（课程时间、出勤、教学摘要）
- 非敏感内容自动化，必要时老师审核后发送

当前低优先级：作品集自动编排、缺勤关怀提醒、学习参与度预警。

## 6. 边界与约束（已确认）

- 合规框架：采用简化 PDPA 逻辑
- 发送边界：敏感或不应自动发送的信息一律不自动发送
- 对接边界：当前不依赖复杂外部对接
- 时间预算：当前不作为主要约束，Idea 优先
- 外包边界：仅产品与技术（暂不含运营和培训）

## 7. 投资人导向主线（已确认）

主线不是“先做最小 MVP”，而是：

- Idea 要足够新颖
- 能显著提升用户体验（尤其家长端）
- 能被老板/投资人快速感知其差异化价值

建议表达：

- 第一层：体验创新（家长端更直观、更安心）
- 第二层：运营提效（老师从行政事务中释放）
- 第三层：数据资产沉淀（后续形成壁垒）

## 8. 一体化价值主链（用于演示）

排课自动化 -> 签到自动化 -> 家长 APP 可视化沟通 -> 管理层看板

## 9. 下一步输出（可立即开始）

- 投资人版本方案（Problem-Solution-Demo-Moat）
- APP 关键页面说明（课程日历、出勤、课后反馈）
- 功能优先级清单（Must / Should / Could）
- AI 落地路径（立即可做 / 需要额外数据 / 后续增强）

## 10. 第一部分已实现（孩子共创角色中文陪练）

- 实施方案：[第一部分-孩子共创角色中文陪练-实施方案.md](./第一部分-孩子共创角色中文陪练-实施方案.md)
- 数据对象样例：[第一部分-数据对象样例.json](./第一部分-数据对象样例.json)
- 测试与验收：[第一部分-测试与验收清单.md](./第一部分-测试与验收清单.md)

## 11. 第二部分规划中（数字角色升级）

- 数字角色升级方案：[第二部分-数字角色升级方案.md](./第二部分-数字角色升级方案.md)

## 12. 创意待办（后续继续讨论）

- 课堂图片互动化创意（方向正确，暂不强行落地）：[创意待办清单.md](./创意待办清单.md)

## 13. 第二部分已改向实施（图片互动课 AI 引擎）

- 实施方案（主文档）：[phase2_interactive_lesson/IMPLEMENTATION_PLAN.md](./phase2_interactive_lesson/IMPLEMENTATION_PLAN.md)
- 接口与类型定义（OpenAPI）：[phase2_interactive_lesson/API_SPEC.yaml](./phase2_interactive_lesson/API_SPEC.yaml)
- 山的叫法样板课包：[phase2_interactive_lesson/SAMPLE_LESSON_PACK_MOUNTAIN.json](./phase2_interactive_lesson/SAMPLE_LESSON_PACK_MOUNTAIN.json)
- 测试与验收清单：[phase2_interactive_lesson/TEST_ACCEPTANCE.md](./phase2_interactive_lesson/TEST_ACCEPTANCE.md)
- 六周执行路线图：[phase2_interactive_lesson/ROADMAP_6W.md](./phase2_interactive_lesson/ROADMAP_6W.md)

## 14. 第二部分真正实施（应试：PSLE + DSA）

- 总实施方案：[phase2_exam_psle_dsa/IMPLEMENTATION_PLAN.md](./phase2_exam_psle_dsa/IMPLEMENTATION_PLAN.md)
- 接口定义（PSLE+DSA）：[phase2_exam_psle_dsa/API_SPEC.yaml](./phase2_exam_psle_dsa/API_SPEC.yaml)
- PSLE 严格评分规格：[phase2_exam_psle_dsa/PSLE_STRICT_SCORING_SPEC.md](./phase2_exam_psle_dsa/PSLE_STRICT_SCORING_SPEC.md)
- PSLE 评分规则 JSON：[phase2_exam_psle_dsa/PSLE_SCORING_RUBRIC_V1.json](./phase2_exam_psle_dsa/PSLE_SCORING_RUBRIC_V1.json)
- DSA 研究 Agent 规格：[phase2_exam_psle_dsa/DSA_RESEARCH_ENGINE_SPEC.md](./phase2_exam_psle_dsa/DSA_RESEARCH_ENGINE_SPEC.md)
- DSA 趋势基线（含官方来源）：[phase2_exam_psle_dsa/DSA_TREND_BASELINE_2026-03-25.md](./phase2_exam_psle_dsa/DSA_TREND_BASELINE_2026-03-25.md)
- DSA 学校年度追踪模板：[phase2_exam_psle_dsa/DSA_SCHOOL_TRACKER_TEMPLATE.csv](./phase2_exam_psle_dsa/DSA_SCHOOL_TRACKER_TEMPLATE.csv)

## 15. 第三部分已实施（汉字声像行动课）

- 总实施方案：[phase3_hanzi_action_lesson/IMPLEMENTATION_PLAN.md](./phase3_hanzi_action_lesson/IMPLEMENTATION_PLAN.md)
- 接口定义：[phase3_hanzi_action_lesson/API_SPEC.yaml](./phase3_hanzi_action_lesson/API_SPEC.yaml)
- 12字样板包：[phase3_hanzi_action_lesson/HANZI_12_CHAR_PACK.json](./phase3_hanzi_action_lesson/HANZI_12_CHAR_PACK.json)
- 动画提示词库：[phase3_hanzi_action_lesson/ANIMATION_PROMPT_LIBRARY.md](./phase3_hanzi_action_lesson/ANIMATION_PROMPT_LIBRARY.md)
- 测试与验收清单：[phase3_hanzi_action_lesson/TEST_ACCEPTANCE.md](./phase3_hanzi_action_lesson/TEST_ACCEPTANCE.md)
- 4周路线图：[phase3_hanzi_action_lesson/ROADMAP_4W.md](./phase3_hanzi_action_lesson/ROADMAP_4W.md)
