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
| [`tests/`](tests/) | 六组 C++17 回归测试与正式代码块差分测试 |
| [`tools/`](tools/) | 接口、变量注释审计与差分测试运行器 |
| [`docs/版本与归档.md`](docs/版本与归档.md) | 版本、归档和发布规则 |
| [`archive/`](archive/) | 明确标注日期、提交和页数的历史快照 |

[`muban.cpp`](muban.cpp) 是复制算法卡片前使用的代码地基。
[`错题本/`](错题本/) 是独立排错资料，不是另一版算法板子。

## 编译与验证

从仓库根目录运行：

```text
python tools/audit_large_interfaces.py
python tools/audit_large_variables.py
python tools/run_differential_tests.py
g++ -std=c++17 -O2 -Wall tests/refactored_strings.cpp
g++ -std=c++17 -O2 -Wall tests/refactored_mst.cpp
g++ -std=c++17 -O2 -Wall tests/refactored_core.cpp
g++ -std=c++17 -O2 -Wall tests/refactored_graph.cpp
g++ -std=c++17 -O2 -Wall tests/refactored_dp_geometry.cpp
g++ -std=c++17 -O2 -Wall tests/refactored_advanced.cpp
xelatex -interaction=nonstopmode -output-directory banzi banzi/板子_大版本.tex
xelatex -interaction=nonstopmode -output-directory banzi banzi/板子_大版本.tex
```

修改模板后必须运行两项审计、正式代码块差分测试和六组回归测试，连续编译两遍
XeLaTeX，并目视检查受影响页面。差分测试只登记能够定义可执行语义的完整模板，
不登记纯框架。需要保留历史节点时只在 `archive/YYYY-MM-DD/` 新增快照，不在
`banzi/` 或仓库根目录创建并列版本。
