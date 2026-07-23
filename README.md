# 区域赛银牌 / Codeforces ≤ 2200 算法手册

当前仓库以“现场可复制、可接入、可验证”为优先，不再把旧版合订本继续拼接扩展。

## 文件导航

| 文件 | 内容 |
| --- | --- |
| [muban.cpp](muban.cpp) | 唯一代码地基；所有卡片从此文件复制后追加 |
| [banzi/板子.pdf](banzi/板子.pdf) | 区域赛现场速查版，七个稳定章节，含压缩错题附录 |
| [banzi/板子_详细验证.pdf](banzi/板子_详细验证.pdf) | 详细解释与验证协议，共享同一套主模板 |
| [banzi/板子_大版本.pdf](banzi/板子_大版本.pdf) | 原 269 页大版本的去重重排版，保留完整专题覆盖 |
| [banzi/板子_大版本_含例题测试.pdf](banzi/板子_大版本_含例题测试.pdf) | 大版本当前验证稿，补入接口注释、完整题例和可执行测试矩阵 |
| [banzi/板子.tex](banzi/板子.tex) | 现场版入口；章节源在 [remake/chapters](remake/chapters) |
| [banzi/板子_大版本.tex](banzi/板子_大版本.tex) | 完整大版本入口；章节源在 [remake/large](remake/large) |
| [remake/chapters/03_字符串.tex](remake/chapters/03_字符串.tex) | KMP、AC（总计数/逐模式计数）、SAM、后缀数组、PAM |
| [tests/refactored_strings.cpp](tests/refactored_strings.cpp) | 高风险字符串模板的 C++17 回归测试 |
| [tests/refactored_mst.cpp](tests/refactored_mst.cpp) | Kruskal 与 Kruskal 重构树的 C++17 回归测试 |
| [tests/refactored_core.cpp](tests/refactored_core.cpp) | 基础、数学与常用数据结构的 C++17 回归测试 |
| [tests/refactored_graph.cpp](tests/refactored_graph.cpp) | 图论与树上接口的 C++17 回归测试 |
| [tests/refactored_dp_geometry.cpp](tests/refactored_dp_geometry.cpp) | 动态规划与几何接口的 C++17 回归测试 |
| [tests/refactored_advanced.cpp](tests/refactored_advanced.cpp) | 线性基、扩展 CRT、矩阵、消元、主席树与李超树回归测试 |
| [remake/large/13_例题与测试.tex](remake/large/13_例题与测试.tex) | 大版本的接口注释、正式题例与测试矩阵 |
| [修改意见.md](修改意见.md) | 本次重构验收标准与取舍边界 |

## 重构后的目录

1. 总览、代码地基与关键词索引；
2. 基础算法与数据结构；
3. 图论与树；
4. 字符串；
5. 数学与动态规划；
6. 银牌档高频模板；
7. 错题附录。

同一算法只保留一份主模板；需要变体时在同一张卡片中说明差异，不再跨章节复制代码。

`banzi/板子.tex` 是 42 页现场速查版，`banzi/板子_大版本.tex` 是完整大版本；
两者用途不同，修改大版本时不要用现场版替代。

## 编译与验证

```text
g++ -std=c++17 -O2 -Wall muban.cpp
g++ -std=c++17 -O2 -Wall tests/refactored_strings.cpp
g++ -std=c++17 -O2 -Wall tests/refactored_mst.cpp
g++ -std=c++17 -O2 -Wall tests/refactored_core.cpp
g++ -std=c++17 -O2 -Wall tests/refactored_graph.cpp
g++ -std=c++17 -O2 -Wall tests/refactored_dp_geometry.cpp
g++ -std=c++17 -O2 -Wall tests/refactored_advanced.cpp
xelatex -interaction=nonstopmode banzi/板子.tex
xelatex -interaction=nonstopmode banzi/板子_详细验证.tex
xelatex -interaction=nonstopmode -output-directory banzi banzi/板子_大版本.tex
```

高风险模板的卡片统一说明：适用条件、不能使用的情况、节点/数组含义、初始化、多测清空、复杂度、内存、完整样例和四组边界测试。

## 备份

首次重构前的完整目录副本位于 `D:\02_Projects\Algorithms\banzi_fork_20260723`，用于回退和差异对照。
