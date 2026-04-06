# 共享数据契约（三条 Demo 共用）

## 必须统一的对象

### LessonSession
- session_id
- class_id
- lesson_pack_id
- teacher_id
- state
- started_at / ended_at

### ArtworkSnapshot
- artwork_id
- student_id
- session_id
- project_cycle_id
- media_uri
- stage

### EvidenceItem
- evidence_id
- student_id
- session_id
- source_type
- source_ref_id
- review_status
- visibility_scope

### GrowthScroll
- scroll_id
- student_id
- session_id
- hero_artwork_id
- proud_speech
- teacher_note
- next_preview

### ChildRoleProfile
- role_id
- student_id
- role_name
- personality
- catchphrase
- system_review_status
- teacher_review_status

### RoleProgressCard
- card_id
- session_id
- role_id
- completion_summary
- upgraded_sentence
- vocabulary_loot
- next_mission

## 统一原则
进入家长端的内容必须可追溯到 session_id 和 student_id。
未经审核内容不能进入班级可见流。
