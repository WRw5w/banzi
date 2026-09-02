# 区域赛银牌 / Codeforces ≤ 2200 算法手册

本仓库只维护一份算法板子：[`banzi/板子_大版本.pdf`](banzi/板子_大版本.pdf)。
它包含专题模板、接口注释、例题、边界说明和测试矩阵；不存在现场版、详细版、
“含例题版”或“最终版”等并列版本。

## 唯一正式链路

| 位置 | 用途 |
| --- | --- |
| [`banzi/板子_大版本.tex`](banzi/板子_大版本.tex) | 唯一编译入口 |
| [`remake/large/`](remake/large/) | 唯一章节源目录 |
| [`banzi/板子_大版本.pdf`](banzi/板子_大版本.pdf) | 唯一正式 PDF |
| [`tests/`](tests/) | 六组 C++17 回归、直接提取差分/契约测试与逐块分类数据 |
| [`tools/`](tools/) | 接口、变量、代码块门禁、测试和稳定 PDF 构建工具 |
| [`docs/代码块检验清单.md`](docs/代码块检验清单.md) | 正式渲染树中全部代码块的覆盖状态 |
| [`docs/版本与归档.md`](docs/版本与归档.md) | 版本、归档和发布规则 |
| [`archive/`](archive/) | 明确标注日期、提交和页数的历史快照 |

[`muban.cpp`](muban.cpp) 是复制算法卡片前使用的代码地基。
[`错题本/`](错题本/) 是独立排错资料，不是另一版算法板子。

## 训练时快速复制

只想用 `Ctrl+F` 搜索纯文本时，双击仓库根目录的
[`打开板子文本.cmd`](打开板子文本.cmd)。它会从当前唯一 TeX 源重新生成并打开
仓库最外层的 `板子代码集合.txt`；该文件是已忽略的临时复制视图，不需要也不允许
手工维护。

需要章节筛选和一键复制按钮时，双击
[`打开板子复制器.cmd`](打开板子复制器.cmd)；也可以在仓库根目录运行：

```text
python tools/serve_snippet_picker.py
```

浏览器会打开本地“算法板子复制器”，可以按章节或关键词搜索，并用按钮复制完整代码块。
页面实时读取 `banzi/板子_大版本.tex` 的正式渲染树及 `remake/large/*.tex` 唯一章节源，
不会生成或维护第二份模板库。服务器默认只监听 `127.0.0.1:8765`；不希望自动打开浏览器
时使用 `python tools/serve_snippet_picker.py --no-open`，按 `Ctrl+C` 停止。

## 编译与验证

从仓库根目录运行：

```text
python tools/audit_large_interfaces.py
python tools/audit_large_variables.py
python tools/audit_listing_coverage.py
python tools/run_framework_checks.py
python -m unittest tests.test_listing_coverage tests.test_framework_checks tests.test_snippet_picker tests.test_comment_semantics
python tools/run_contract_tests.py
python tools/run_differential_tests.py
python tools/run_refactored_tests.py
python tools/build_formal_pdf.py
```

修改模板后必须运行接口、变量和代码块覆盖审计、框架结构契约、门禁反例单测、正式
代码块的契约/差分测试及六组回归测试。PDF 构建必须持续到交叉引用状态稳定且没有
rerun warning，并目视检查受影响页面。只有直接提取、真实编译/运行的测试才算执行
证据；框架结构检查不冒充算法验证，也不在正式板子中标记验证状态。需要
保留历史节点时只在 `archive/YYYY-MM-DD/` 新增快照，不在 `banzi/` 或仓库根目录
创建并列版本。
