# DSA 趋势研究 Agent 规格（v1）

更新时间：2026-03-25

## 目标

这个 Agent 负责“按学校、按年份”追踪 DSA 变化，并输出老师和家长能直接使用的结论。  
重点不是堆链接，而是回答三件事：

1. 今年比去年改了什么？  
2. 要求是变严还是变松？  
3. 孩子的作品集和申请策略要怎么改？

## 结构化字段

每条学校年度记录至少包含：

- `cycle_year`
- `admission_year`
- `school_name`
- `school_type`
- `talent_area`
- `application_window`
- `selection_stages`
- `portfolio_requirement`
- `eligibility_notes`
- `commitment_requirement`
- `source_url`
- `source_last_updated`
- `captured_at`

## 年度变化检测

针对同校 `Y vs Y-1` 自动标记：

- 时间变化：窗口是否提前/延后  
- 门槛变化：作品要求、轮次、任务难度是否变化  
- 流程变化：是否新增面试/测试/短名单活动  
- 入口变化：MOE Portal 或学校独立申请

## 输出给老师和家长

- 学校一页卡：今年要求、去年对比、关键风险  
- 作品改进建议：本学期该增加/删减哪些类型  
- 申请建议：冲刺校/匹配校/保底校（老师最终确认）

## 首批跟踪范围

第一批优先抓艺术方向学校：

- 专门艺术导向学校（如 SOTA）  
- 明确 Visual Arts DSA 标准的学校  
- 一般中学但有艺术方向 DSA 通道的学校
