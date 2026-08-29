# 正式代码块编译与契约测试

这里的测试直接从正式 TeX 的 `lstlisting` 提取一个或多个代码块，注入带唯一标记的
C++ harness，再进行真实编译和运行。它用于验证完整实现或可由明确调用约定补齐的
代码片段；只做摘要、关键字或括号检查的条目不能进入本清单。

一个 case 可以覆盖多个互相配合的正式代码块，但报告会把同一个 test id 映射回每个
被提取块。harness 只提供输入数据、题意依赖、暴力实现和调用包装，不复制待测实现。
当前 17 个 case 包含 LCT 动态森林、Dinic、Kruskal 重构树，以及数学、数据结构、
字符串、图论、几何、基础与博弈的成组性质测试。新增的基础批次直接覆盖 bitset/SOS、
枚举与搜索、筛法与组合、常见图算法、线性 DP/背包、仿射与 Beats、字符串哈希、
整数方向归一化、点分治和 DSU on Tree。`PASS` 只代表当次编译和已声明契约通过，
不能外推到未覆盖的题意框架。

整数域审计分两类处理：方向归一化、最大子段和、窗口 DP、差分约束和 Beats 使用
`__int128` 保存精确中间量；LCM、二分答案和扫描面积在最终结果超出 `long long` 时
返回 `nullopt`。仍使用定宽返回值的 bitset/SOS、前缀差分、三分、整除分块、
Dijkstra/TSP、仿射标记和 CHT 块，都在正式接口旁写明输入范围、哨兵上界或乘积
可表示条件。边界契约覆盖 0、负数、`LLONG_MIN`、`LLONG_MAX`、恰好可表示与溢出。

```text
python tools/run_contract_tests.py
python tools/run_contract_tests.py --case graph.lct
```
