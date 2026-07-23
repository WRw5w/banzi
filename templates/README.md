# 模板使用说明

`competitive.hpp` 是按“能直接剪下来改”的方式组织的 C++17 模板库。整文件可以作为个人头文件，也可以只复制某个标记区间。

## 编译

```bash
g++ -std=c++17 -O2 -pipe -static -s main.cpp -o main
```

## 使用约定

- 下标：图和树模板默认 `1..n`；字符串默认 `0..n-1`。
- 所有距离/答案优先用 `long long`；乘法溢出时改 `__int128`。
- 模板尽量不提供 `main`，复制到题解后自行写 `solve()`。
- 代码中的 `MOD`、字符集大小、最大节点数按题目修改；静态数组容量不足是最常见的 RE 原因。
- 多测时重新构造对象或调用 `clear/reset`，不要依赖上一次数据。

## 快速检索关键词

`DSU`、`Fenwick`、`SegTree`、`Dijkstra`、`Dinic`、`MinCostMaxFlow`、`SCC`、`Bridge`、`LCA`、`HLD`、`KMP`、`ZFunction`、`Manacher`、`AhoCorasick`、`SuffixArray`、`SuffixAutomaton`、`LinearBasis`、`PersistentSegTree`、`RollbackDSU`、`FHQTreap`、`ConvexHull`、`NTT`。

## 复制前的四项检查

1. 题目是 0 下标还是 1 下标？
2. 模数是否为质数、边权是否允许负数？
3. 图是有向/无向，是否有重边、自环？
4. 最大数据量是否超过模板的节点池/递归深度/内存？
