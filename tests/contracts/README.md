# 正式代码块编译与契约测试

这里的测试直接从正式 TeX 的 `lstlisting` 提取一个或多个代码块，注入带唯一标记的
C++ harness，再进行真实编译和运行。它用于验证完整实现或可由明确调用约定补齐的
代码片段；只做摘要、关键字或括号检查的条目不能进入本清单。

一个 case 可以覆盖多个互相配合的正式代码块，但报告会把同一个 test id 映射回每个
被提取块。harness 只提供输入数据、题意依赖、暴力实现和调用包装，不复制待测实现。
当前清单包含 LCT 动态森林、Dinic、Kruskal 重构树，以及数学、数据结构、字符串、
图论、几何和基础/博弈的成组性质测试。`PASS` 只代表当次编译和已声明契约通过，不能
外推到未覆盖的题意框架。

```text
python tools/run_contract_tests.py
python tools/run_contract_tests.py --case graph.lct
```
