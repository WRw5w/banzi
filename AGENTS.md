# 项目协作规则

- 完整大版本的唯一入口是 `banzi/板子_大版本.tex`，唯一正式产物是
  `banzi/板子_大版本.pdf`。
- 大版本章节只从 `remake/large/*.tex` 引入；不要用 42 页现场版替代，也不要修改
  `new/`、`big-anwser/` 或 `output/pdf/` 来冒充正式源。
- `板子_大版本.pdf` 已经包含例题与测试，不在 `banzi/` 中创建“含例题”“最终版”
  等并列 PDF；历史快照统一放到 `archive/YYYY-MM-DD/`。
- 注释应解释接口、参数、字段和变量的真实用途，不为补注释增加包装函数或额外 API。
- 修改模板后运行 `tools/audit_large_interfaces.py`、`tools/audit_large_variables.py`
  和六个 `tests/refactored_*.cpp` 回归测试。
- 大版本连续编译两遍 XeLaTeX，目视检查受影响页面，再同步源文件、测试、正式 PDF
  和文档。
- 完成后提交并推送 `origin/main`；版本与归档细节见 `docs/版本与归档.md`。
