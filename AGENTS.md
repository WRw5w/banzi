# 项目协作规则

- 算法板子的唯一入口是 `banzi/板子_大版本.tex`，唯一正式产物是
  `banzi/板子_大版本.pdf`。
- 章节只从 `remake/large/*.tex` 引入；不要创建第二套入口、章节源或备用模板库。
- `板子_大版本.pdf` 已经包含例题与测试，不在 `banzi/` 中创建“含例题”“最终版”
  等并列 PDF；`banzi/` 中只保留正式 TeX 和 PDF，历史快照统一放到
  `archive/YYYY-MM-DD/`。
- 注释应解释接口、参数、字段和变量的真实用途，不为补注释增加包装函数或额外 API。
- 修改模板后运行 `tools/audit_large_interfaces.py`、`tools/audit_large_variables.py`、
  `tools/audit_listing_coverage.py`、`tools/run_framework_checks.py`、
  `tools/run_contract_tests.py`、`tools/run_differential_tests.py`、两组 Python 门禁单测和
  六个 `tests/refactored_*.cpp` 回归测试；仅结构契约不称为算法验证，验证状态不写入
  正式板子。
- 使用 `tools/build_formal_pdf.py` 在隔离目录持续编译 XeLaTeX，直到目录、书签和
  交叉引用状态稳定且没有 rerun warning；目视检查受影响页面后再同步源文件、测试、
  正式 PDF 和文档。
- 完成后提交并推送 `origin/main`；版本与归档细节见 `docs/版本与归档.md`。
