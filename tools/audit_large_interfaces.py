#!/usr/bin/env python3
"""Audit and (optionally) annotate C++ interfaces in the large handbook.

The rendered order is taken from banzi/板子_大版本.tex.  Only lstlisting
blocks are inspected, so TeX commands and prose examples are not mistaken for
C++ interfaces.
"""

from __future__ import annotations

import argparse
import ast
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "banzi" / "板子_大版本.tex"

LISTING_RE = re.compile(
    r"(?P<open>\\begin\{lstlisting\}(?:\[[^\]]*\])?)(?P<body>.*?)(?P<close>\\end\{lstlisting\})",
    re.S,
)
HEADING_RE = re.compile(r"\\(?:chapter|section|subsection|subsubsection)\{([^{}]*)\}")
FUNCTION_RE = re.compile(
    r"^(?P<indent>[ \t]*)"
    r"(?P<template>template\s*<[^;{}]+>\s*\n[ \t]*)?"
    r"(?P<prefix>(?:(?:static|inline|virtual|constexpr|consteval|friend|explicit)\s+)*)"
    r"(?P<return>[\w:<>,&*\[\] \t]+?)\s+"
    r"(?P<name>operator\s*[^\s(]+|[A-Za-z_]\w*)"
    r"\s*\((?P<params>[^;{}]*)\)"
    r"\s*(?:const\s*)?(?:noexcept\s*)?(?:->\s*[^\{]+)?\s*\{[^\n]*$",
    re.M,
)
LAMBDA_RE = re.compile(
    r"^(?P<indent>[ \t]*)(?P<line>[^\n]*?"
    r"(?P<capture>\[[^\]\n]*\])\s*\((?P<params>[^()]*)\)"
    r"\s*(?:mutable\s*)?(?:->\s*[^\{]+)?\s*\{[^\n]*)$",
    re.M,
)

CONTROL_NAMES = {"if", "for", "while", "switch", "catch", "sort", "inplace_merge"}

# Function names whose bare English name is not enough at contest time.
# Repeated short method names are described further by the current section.
PURPOSE = {
    "solve": "完成本节给出的单组测试/递归区间",
    "main": "程序入口，负责 I/O 初始化并调用本节核心逻辑",
    "print_i128": "十进制输出一个 __int128",
    "lowbit": "返回 x 的二进制最低位 1 所代表的权值 x&-x",
    "is_pow2": "判断正整数 x 是否恰好是 2 的幂",
    "clear": "清空当前结构并恢复为刚构造的空状态",
    "maximum": "返回把 x 与线性基中若干向量异或后可得到的最大值",
    "can": "判断 x 是否能由当前线性基中的向量异或得到",
    "max_xor": "返回把 x 与当前集合/线性基元素组合后能得到的最大异或值",
    "gen": "枚举 a 的下标闭区间 [l,r] 的所有子集和并返回排序结果",
    "check": "判断二分答案 limit 是否可行；必须满足关于 limit 的单调性",
    "Mat": "构造 n 阶零矩阵；ident=true 时构造单位矩阵",
    "operator*": "返回两个矩阵/几何量按本节定义相乘的结果",
    "operator": "返回键值的 size_t 哈希值，供 unordered_map/unordered_set 去重",
    "mpow": "返回矩阵 a 的 e 次幂",
    "fib": "返回 (F_n,F_{n+1})",
    "multiply": "返回两个多项式的卷积并按本节模数取模",
    "DSU": "构造管理点 1..n 的并查集，每个点初始自成集合",
    "find": "返回 x 当前所在并查集的代表元",
    "unite": "合并两个元素所在集合；原本同集合时返回 false",
    "BIT": "构造管理 1..n 下标的空树状数组",
    "Fenwick": "构造管理 1..n 下标的空树状数组",
    "sum": "返回闭前缀 [1,x] 的累计和/频次",
    "range": "返回 1-based 闭区间 [l,r] 的元素和",
    "SegTree": "构造管理 1..n 闭区间的空线段树",
    "apply": "把本次懒操作直接作用于节点 p，并同步节点值与标记",
    "push": "把节点 p/x 的待下传标记传给孩子并清除本节点标记",
    "pull": "由孩子信息重新计算节点 p/u 的聚合信息",
    "push_up": "由两个孩子重新计算节点 p 的全部统计量",
    "push_down": "把节点 p 的区间约束下传到两个孩子",
    "query": "返回本节数据结构在给定位置/区间上的查询结果",
    "median": "返回当前两个堆维护的中位数（奇数个元素时为正中间）",
    "update": "基于旧版本复制修改路径并返回/写入新版本根",
    "size": "返回节点 u 所代表子树的节点数，空节点 0 的大小为 0",
    "split": "按 key/路径把当前结构拆成两部分，结果写入输出参数",
    "merge": "合并两个兼容对象/同余式；返回值表示成功或新根",
    "RollbackDSU": "构造支持快照和回滚、且不做路径压缩的并查集",
    "snapshot": "返回当前撤销栈长度，供 rollback 恢复",
    "get": "返回直线在横坐标 x 处的函数值",
    "LiChao": "构造整数横坐标闭区间 [L,R] 上的李超树",
    "SegBeats": "由 1-based 数组 a 构造区间 chmin + 区间和线段树",
    "chmin": "把目标闭区间内每个值更新为 min(原值,x)",
    "build": "由当前输入/成员状态完成数据结构预处理",
    "add_pos": "把数组位置 p 加入当前莫队窗口并更新答案",
    "del_pos": "把数组位置 p 移出当前莫队窗口并更新答案",
    "apply_change": "正向应用或反向撤销一次带修改莫队更新",
    "process_query": "把莫队窗口和时间移动到查询 q，随后记录答案",
    "insert": "把参数表示的数/字符串/版本插入当前结构",
    "extend": "向当前字符串自动机加入一个字符并更新状态",
    "init": "清空成员并建立本自动机所需的初始根节点",
    "get_fail": "沿 fail 链找到能被当前字符继续扩展的节点",
    "add": "执行本节定义的单点/区间增加或加入操作",
    "operator<": "按边权升序比较两条边，供 Kruskal 排序",
    "KruskalDSU": "构造管理点 1..n 的 Kruskal 专用并查集",
    "dfs": "从当前节点/位置继续深度优先处理，并写入本节状态数组",
    "bfs": "从源点建立层次/可达信息；返回是否能到达汇点",
    "add_edge": "向残量网络/邻接表加入本节定义的一条边及其反向边",
    "add_line": "把一条候选直线插入当前李超树/单调凸包并删除失效候选",
    "init_lca": "从 u 开始填写深度及倍增祖先 up[u][k]",
    "add_path": "给树上 u-v 路径做差分标记，之后必须自底向上 collect",
    "collect": "收集当前子树的距离/差分贡献到输出容器或父节点",
    "tree_dp": "自底向上计算以 u 为根的树形 DP 状态",
    "dfs1": "计算 HLD 所需的父亲、深度、子树大小和重儿子",
    "dfs2": "沿重链优先编号并填写链顶 top",
    "divide": "对 entry 所在连通块执行一层点分治并递归子块",
    "dfs_size": "计算未删除树/子树的大小及重儿子",
    "add_subtree": "把 u 子树（排除父亲/禁用重儿子）加入或移出统计",
    "dsu_on_tree": "按 keep 参数执行 DSU on Tree；keep=false 时清除贡献",
    "dsu": "按 keep 参数执行 DSU on Tree；keep=false 时清除 u 子树贡献",
    "dfs_len": "计算 u 子树最大深度并选出最长链儿子",
    "dfs_chain": "沿最长链优先递归并填写每个点的链顶 top",
    "decompose": "以当前连通块重心为根递归建立点分治/点分树",
    "long_chain_dfs1": "计算子树最大深度并选择最长链儿子",
    "long_chain_dfs2": "沿最长链优先处理并填写链顶/数组位置",
    "LCT": "构造含 n 个 1-based 点的 Link-Cut Tree",
    "is_root": "判断 x 是否是当前 splay 辅助树的根",
    "pull_sum": "由两个 splay 儿子和自身点权重算 t[x].sum",
    "apply_rev": "交换 x 的左右儿子并翻转路径反转标记",
    "rotate": "在辅助 splay 中把 x 向上旋转一层",
    "splay": "把 x 旋到其当前辅助树根，并先下传祖先标记",
    "access": "打通原树根到 x 的首选路径，结束时 x 为辅助树根",
    "reroot1": "第一次 DFS，计算每个子树的向下 DP",
    "reroot2": "第二次 DFS，把父侧贡献传给儿子并得到全树答案",
    "solve_digit": "返回给定数位 DP 状态的合法后缀方案数",
    "bad": "判断中间直线 b 是否因交点顺序而永远不会成为最优",
    "value": "返回直线 k*x+b 在横坐标 x 处的值",
    "useless": "判断中间候选直线 b 是否可从凸包队列删除",
    "divide_conquer_dp": "计算 DP 下标闭区间 [L,R]，决策只搜索 [optL,optR]",
    "mul": "返回两个转移矩阵的乘积",
    "identity": "返回当前状态维数的单位转移矩阵",
    "merge_segment": "按从左到右的应用顺序合并两个区间转移矩阵",
    "dag_game": "返回 DAG 状态 u 的 SG 值",
    "solve_subtraction": "返回 n 堆/个石子的减法游戏 SG 值",
    "solve_win": "返回 DAG 状态 u：1 必胜，-1 必败",
    "mex_by_stamp": "用时间戳数组返回 values 的 mex，避免每次清空 seen",
    "bash_win": "判断每次可取 1..k 个时 n 个石子的局面是否先手胜",
    "misere_nim_win": "判断反常 Nim（取走最后石子者输）是否先手胜",
    "staircase_nim_win": "判断阶梯 Nim 局面是否先手胜",
    "dfs_mask": "返回状压状态 mask 是否为先手必胜态并记忆化",
    "operator+": "返回两个点/向量的坐标和",
    "operator-": "返回两个点/向量的坐标差",
    "cross": "返回二维向量 a,b 的叉积",
    "dot": "返回二维向量 a,b 的点积",
    "sgn": "按 EPS 返回 x 的符号：正为 1，负为 -1，近零为 0",
    "dist2": "返回点 a,b 的欧氏距离平方",
    "left_of": "判断 p 是否严格位于有向直线 a->b 左侧",
    "clip": "用有向直线 a->b 的左半平面裁剪凸多边形 poly",
    "half": "返回向量所在半平面编号，供无 atan2 极角排序",
    "modify": "给扫描线离散 y 闭区间增加覆盖计数 d",
    "qpow": "计算 a^e mod mod",
    "mod_pow": "计算 a^e mod p",
    "mul_mod": "计算 a*b mod mod，并避免中间乘法溢出",
    "exgcd": "求 gcd(a,b)，并通过 x,y 返回 ax+by=gcd(a,b) 的一组系数",
    "factor": "试除分解 n，返回 (质因子, 指数)",
    "Csmall": "计算当前质数模数下的小组合数 C(n,k)",
    "lucas": "用 Lucas 定理计算 C(n,k) mod p",
    "Lucas": "用 Lucas 定理计算 C(n,k) mod p",
    "merge_congruence": "合并两个同余方程，结果写入 a,m",
    "gauss": "对增广矩阵做高斯消元并返回解的状态",
    "gauss_mod": "在模 mod 意义下对增广矩阵消元",
    "gauss_real": "对实数增广矩阵消元并返回解的状态",
    "linear_sieve_mu": "线性筛出 1..n 的莫比乌斯函数 mu",
    "linear_sieve_phi": "筛出 [1,upper] 的质数、最小质因子 lp 和欧拉函数 phi",
    "linear_sieve_phi_mu": "筛出 [1,upper] 的质数、lp、phi 和莫比乌斯函数 mu",
    "bsgs": "求最小非负 x 使 a^x=b (mod mod)，无解返回 -1",
    "tonelli_shanks": "求 x^2=n (mod p) 的一个根，无解返回 -1",
    "burnside": "按 Burnside 引理计算本质不同方案数",
    "ntt": "对数组 a 做模 998244353 的 NTT；invert=true 时做逆变换",
    "fibonacci": "返回第 n 项 Fibonacci 数（按本节矩阵定义）",
    "expected_dag": "返回 DAG 上从指定状态出发的期望值",
    "xor_prefix": "返回 0 xor 1 xor ... xor n",
    "xor_range": "返回闭区间 [l,r] 内所有整数的异或和",
    "xor_n": "返回题目定义范围内的异或前缀值",
    "ways": "返回当前计数模型下的方案数",
    "prufer_encode": "把 1..n 编号树编码为长度 n-2 的 Prüfer 序列",
    "prufer_decode": "把 Prüfer 序列还原为无向树边集",
    "tree_count": "对删去一行一列的拉普拉斯矩阵求行列式，返回生成树数量",
    "legendre": "返回 Legendre 符号 (a/p)：1 为非零二次剩余，-1 为非剩余，0 表示 a=0",
    "print128": "十进制输出一个 __int128",
    "read128": "从标准输入读取并返回一个 __int128",
    "cantor": "返回排列 p 的 0-based Cantor 排名",
    "inv_cantor": "由 0-based 排名还原 1..n 的排列",
    "randint": "返回闭区间 [l,r] 内均匀随机整数",
    "randll": "返回闭区间 [l,r] 内均匀随机 long long",
    "randstr": "生成长度 n、字符来自 alphabet 的随机串",
    "rand_tree": "生成 n 个点的随机树边集",
    "rand_graph": "生成 n 点 m 边随机简单图",
    "rand_distinct": "生成范围内互不相同的随机整数",
    "rand_perm": "生成 1..n 的随机排列",
    "prefix_function": "返回 KMP 前缀函数 pi；pi[i] 是 s[0..i] 的最长真 border 长度",
    "kmp": "返回模式串 pat 在 text 中所有 0-based 起点",
    "z_function": "返回 Z 数组；z[i] 是 s 与 s[i..] 的最长公共前缀长度",
    "suffix_array": "返回 sa；sa[i] 是字典序第 i 小后缀的 0-based 起点",
    "kasai": "由 s 和 sa 返回相邻后缀 LCP 数组",
    "booth": "返回字符串字典序最小循环表示的 0-based 起点",
    "min_rotation": "返回最小循环表示的 0-based 起点",
    "scan": "扫描文本并累计自动机匹配结果",
    "dfs_fail": "沿 fail 树汇总模式串出现次数",
    "count_occurrence": "沿回文树 fail 链汇总各回文出现次数",
    "kruskal": "返回无向图最小生成森林是否连通及总权值",
    "prim": "返回图是否连通及最小生成树总权值",
    "tarjan": "从 u 开始求强连通分量的 Tarjan DFS",
    "aug": "从左部点 u 尝试寻找一条二分图增广路",
    "min_cost_flow": "发送至多 need 单位流，返回 (实际流量, 最小费用)",
    "hierholzer": "从 start 构造欧拉路径，返回顶点序列",
    "lca": "返回树上 u,v 的最近公共祖先",
    "bottleneck": "返回 u,v 路径上的瓶颈边权；不连通时返回空",
    "component_node": "返回 Kruskal 重构树中阈值 lim 对应的祖先节点",
    "component_size": "返回阈值 lim 下点 u 所在连通块大小",
    "farthest": "返回从起点出发最远的 (距离, 顶点)",
    "get_size": "统计当前未删除连通块的子树大小",
    "get_centroid": "返回当前连通块的重心",
    "find_root": "返回隐式平衡树中第 k 个位置对应的节点",
    "findroot": "返回动态树中 x 所在树的根",
    "makeroot": "把 x 设为其动态树的根",
    "link": "连接原本不连通的 x,y",
    "cut": "删除动态树中的边 (x,y)",
    "path_sum": "返回树上 u 到 v 路径的权值和",
    "prefix_sum": "返回前缀聚合值",
    "first_at_least": "返回查询范围内第一个值至少为 x 的位置，不存在返回 -1",
    "kth": "返回当前数据结构中的第 k 小值/位置",
    "rollback": "把可撤销数据结构恢复到指定快照",
    "range_add_linear": "在闭区间 [l,r] 给位置 i 加上 a*i+b",
    "point_value": "返回位置 i 的当前值",
    "query_sum": "返回闭区间查询的元素和",
    "range_chmin": "对闭区间 [ql,qr] 执行 a[i]=min(a[i],x)",
    "apply_chmin": "给当前线段树节点应用 chmin 标记",
    "push_chmin": "把父节点的 chmin 约束下传到孩子",
    "add_number": "把一个数加入当前可持久/可撤销统计结构",
    "cdq": "处理下标闭区间 [l,r] 的 CDQ 分治贡献",
    "merge_version": "合并两棵可持久化线段树版本并返回新根",
    "nim_first_win": "返回标准 Nim 当前局面是否先手必胜",
    "misere_nim_first_win": "返回反常 Nim 当前局面是否先手必胜",
    "bash_first_win": "返回 Bash 取石子局面是否先手必胜",
    "mex": "返回集合中没有出现的最小非负整数",
    "grundy": "返回状态 x/u 的 Sprague-Grundy 值",
    "first_win": "返回若干独立子游戏异或和是否非零",
    "nim_move": "返回一个必胜 Nim 操作 (堆下标, 操作后石子数)，无则 (-1,0)",
    "subtraction_sg": "返回减法游戏 0..N 的 SG 数组",
    "find_period": "在 SG 序列中寻找可验证周期并返回周期信息",
    "minimax": "返回当前博弈状态在双方最优策略下的估值",
    "alpha_beta": "返回带 alpha-beta 剪枝的极大极小估值",
    "on_segment": "判断点 p 是否在线段 ab 上（含端点）",
    "intersect": "判断闭线段 ab 与 cd 是否相交（含端点）",
    "line_circle": "返回直线与圆的全部交点（0/1/2 个）",
    "circle_circle": "返回两圆全部交点（0/1/2 个；重合圆需单独处理）",
    "area2": "返回多边形有向面积的两倍",
    "convex_hull": "返回去重后的凸包顶点（逆时针，不重复首点）",
    "diameter2": "返回凸多边形直径的平方",
    "line_inter": "返回两条非平行直线的交点",
    "half_plane_intersection": "返回半平面交得到的凸多边形",
    "closest": "返回指定点集/下标区间内最近点对距离",
    "polar_cmp": "按极角比较两个向量，供 sort 使用",
    "outside": "判断点 p 是否在有向半平面的外侧",
    "intersection": "返回两条边界直线的交点",
    "min_circle": "返回覆盖所有输入点的最小圆",
    "union_area": "返回矩形集合的并面积",
    "BigInteger": "由十进制字符串或默认值构造任意精度整数",
    "Line": "构造斜率为 k、截距为 b 的直线",
    "SparseTable": "由输入数组构造静态区间最值表",
    "abs128": "返回 long long 的非负 __int128 绝对值",
    "abs_add": "按绝对值相加两个任意精度整数",
    "abs_big": "返回任意精度整数的绝对值",
    "abs_compare": "比较两个任意精度整数的绝对值",
    "abs_sub": "在左操作数绝对值不小时做绝对值减法",
    "add_node": "把顶点 u 的颜色计数增加 delta",
    "bfs_dist": "返回从单源 s 到各顶点的无权最短距离",
    "bitset_closure": "用 bitset 原地求有向图传递闭包",
    "build_linear_values": "构造线性函数在指定横坐标上的取值序列",
    "complete_knapsack": "返回完全背包在每个容量上限下的最大价值",
    "count_prefix": "返回字典树中具有给定前缀的字符串数量",
    "count_word": "返回给定完整字符串在字典树中的插入次数",
    "difference_constraints": "求差分约束系统的一组最短路可行势函数",
    "divide_by_two": "原地把非负任意精度整数除以 2",
    "divmod": "返回任意精度整数除法的商和余数",
    "enumerate_submasks": "返回 n 的全部非零子掩码",
    "gcd128": "返回两个整数绝对值的最大公约数",
    "gcd_big": "返回两个任意精度整数的非负最大公约数",
    "geometry_bitset_closure": "用 bitset 原地求几何关系图的传递闭包",
    "inverse_coprime": "返回与模数互质元素的乘法逆元",
    "is_odd": "判断任意精度整数是否为奇数",
    "is_zero": "判断任意精度整数是否为零",
    "max_bipartite_matching": "返回给定二分图的最大匹配边数",
    "minimize_max_segment_sum": "把数组分成至多 k 段并最小化最大段和",
    "mitm_max_subset_sum": "返回不超过 limit 的最大子集和",
    "multi_source_bfs": "返回离任一给定源点最近的无权距离",
    "multiply_small": "原地乘以一个 uint32_t 非负因子",
    "normalize_direction": "把整数方向约成唯一的互质规范方向",
    "operator!=": "判断两个任意精度整数是否不相等",
    "operator%": "返回任意精度整数除法的余数",
    "operator/": "返回任意精度整数除法的商",
    "operator<<": "把任意精度整数写入输出流",
    "operator<=": "判断左操作数是否不大于右操作数",
    "operator=": "把十进制字符串解析并赋给当前任意精度整数",
    "operator==": "判断两个任意精度整数是否相等",
    "operator>": "判断左操作数是否大于右操作数",
    "operator>=": "判断左操作数是否不小于右操作数",
    "operator>>": "从输入流读取一个任意精度整数",
    "pow_mod_big": "计算任意精度指数下的模幂",
    "read": "解析十进制字符串并覆盖当前任意精度整数",
    "safe_lcm": "计算最小公倍数并报告 long long 溢出",
    "shift_base_add": "执行当前值乘 BASE 再加一个低位块",
    "storage_size": "返回李超树为给定整数横坐标域预留的节点数",
    "str": "返回任意精度整数的十进制字符串",
    "sweep_area": "按横坐标事件扫描并返回矩形并面积",
    "transitive_closure": "用 bitset 原地求有向图传递闭包",
    "trim": "删除任意精度整数的高位零块并规范零的符号",
    "window_min_dp": "计算转移窗口宽度为 k 的最小值动态规划",
    "zero_one_knapsack": "返回 0/1 背包在每个容量上限下的最大价值",
}

# These repeated method names need a signature/section rule above. Their table
# wording is documentation vocabulary only, never a safe generation fallback.
CONTEXT_SENSITIVE_PURPOSE_NAMES = {
    "solve", "main", "max_xor", "operator*", "sum", "apply", "push", "pull",
    "query", "update", "split", "merge", "build", "insert", "extend", "add",
    "dfs", "bfs", "add_edge", "add_line", "collect", "decompose",
}

PARAM_MEANING = {
    "n": "输入规模 n",
    "N": "最大状态或答案上界 N",
    "m": "输入规模 m",
    "a": "左操作数 a",
    "b": "右操作数 b",
    "x": "输入数值 x",
    "y": "输入数值 y",
    "u": "顶点编号 u",
    "v": "顶点编号 v",
    "fa": "父节点 fa",
    "p": "本次调用处理的对象 p",
    "l": "闭区间左端点 l",
    "r": "闭区间右端点 r",
    "L": "闭区间左端点 L",
    "R": "闭区间右端点 R",
    "ql": "目标闭区间左端 ql",
    "qr": "目标闭区间右端 qr",
    "pos": "0-based 位置 pos",
    "k": "整数参数 k",
    "mod": "正模数 mod",
    "e": "非负指数 e",
    "text": "主串 text",
    "pat": "模式串 pat",
    "start": "遍历起点 start",
    "lim": "允许的阈值 lim",
    "limit": "判定阈值 limit",
    "delta": "本次增量 delta",
    "value": "写入或查询的值 value",
    "tight": "前缀是否仍贴住上界 tight",
    "started": "是否已经放置非前导零数字 started",
    "rem": "当前余数状态 rem",
    "entry": "当前连通块入口 entry",
    "need": "希望发送的流量 need",
    "invert": "是否执行逆变换 invert",
    "rank": "0-based Cantor 排名 rank",
    "lo": "随机取值闭区间下界 lo",
    "hi": "随机取值闭区间上界 hi",
    "len": "目标字符串长度 len",
    "argc": "命令行参数个数 argc",
    "argv": "命令行参数数组 argv",
    "a1": "第一个同余式的余数 a1",
    "m1": "第一个同余式的正模数 m1",
    "a2": "第二个同余式的余数 a2",
    "m2": "第二个同余式的正模数 m2",
    "ident": "是否构造单位矩阵 ident",
    "A": "左矩阵 A",
    "B": "右矩阵 B",
    "MOD": "运算使用的正模数 MOD",
    "base": "幂运算的底多项式 base",
    "group": "所有群作用置换的列表 group",
    "colors": "可用颜色数 colors",
    "g": "图的邻接表 g",
    "code": "Prüfer 序列 code",
    "lap": "删去一行一列后的拉普拉斯矩阵 lap",
    "inv": "是否执行逆变换 inv",
    "sum": "当前累计值 sum",
    "fac": "阶乘数组 fac[i]=i! mod p",
    "ifac": "逆阶乘数组 ifac[i]=(i!)^{-1} mod p",
    "perm": "一个 0-based 置换 perm",
    "ans": "接收计算结果的输出引用 ans",
    "old": "旧版本根节点编号 old",
    "key": "拆分键 key",
    "snap": "此前 snapshot() 返回的撤销栈长度 snap",
    "nw": "待插入的新直线 nw",
    "i": "0-based 位置 i",
    "mul": "仿射标记乘数 mul",
    "forward": "true=应用修改，false=撤销修改",
    "q": "当前查询对象 q",
    "bit": "当前处理的二进制位 bit",
    "left_root": "区间左端前一个前缀版本根 left_root",
    "right_root": "区间右端前缀版本根 right_root",
    "val": "写入的新值 val",
    "root": "当前版本根节点编号 root",
    "c": "输入数值 c",
    "ch": "待加入字符 ch",
    "str": "待完整构建的字符串 str",
    "edges": "输入边集合 edges",
    "n_": "原图点数 n_",
    "parent_edge": "DFS 进入 u 所用的无向边编号 parent_edge",
    "cap": "边容量 cap",
    "cost": "每单位流费用 cost",
    "s": "源点编号 s",
    "t": "汇点编号 t",
    "f": "本次 DFS 允许继续发送的流量 f",
    "topf": "当前重链链顶 topf",
    "top": "当前长链/重链链顶 top",
    "keep": "是否保留 u 子树统计贡献 keep",
    "d": "距离 d",
    "ds": "收集距离的输出数组 ds",
    "optl": "真实最优决策允许范围左端 optl",
    "optr": "真实最优决策允许范围右端 optr",
    "optL": "真实最优决策允许范围左端 optL",
    "optR": "真实最优决策允许范围右端 optR",
    "line": "待插入候选直线 line",
    "left": "左区间转移矩阵 left",
    "right": "右区间转移矩阵 right",
    "values": "要求 mex 的非负整数集合 values",
    "seen": "mex 时间戳数组 seen",
    "tag": "当前 mex 时间戳引用 tag",
    "moves": "每步允许取走的石子数集合 moves",
    "mask": "当前状压状态 mask",
    "alpha": "当前已知下界 alpha",
    "beta": "当前已知上界 beta",
    "poly": "当前凸多边形顶点 poly",
    "o": "比较器的右操作数 o",
    "mid": "区间中点 mid",
    "j": "比较器收到的另一个 0-based 下标 j",
    "total": "当前连通块总大小 total",
    "sa": "后缀数组 sa；sa[i] 为第 i 小后缀起点",
    "add": "仿射标记常数项/本次增加量 add",
    "st": "题目定义或自动机节点状态 st，范围 [0,STATE)",
    "piles": "各堆石子数 piles",
    "starts": "若干独立子游戏的起始状态 starts",
    "state": "当前博弈状态 state",
    "depth": "剩余搜索深度 depth",
    "maximizing": "当前层是否轮到极大化一方 maximizing",
    "maxing": "当前层是否轮到极大化一方 maxing",
    "sg": "已计算的 SG 数列 sg",
    "min_start": "允许作为周期起点的最小下标 min_start",
    "min_len": "允许的最短周期长度 min_len",
    "h": "当前半平面 h",
}


@dataclass
class Hit:
    path: Path
    listing: int
    line: int
    name: str
    params: list[str]
    section: str
    annotated: bool


@dataclass
class FieldHit:
    path: Path
    listing: int
    line: int
    owner: str
    declaration: str
    annotated: bool


AMBIGUOUS_COMMENT_PHRASES = (
    "当前节点/模数",
    "质数、节点编号或指针",
    "待处理值或点/状态",
    "输入值/数组",
    "顶点/状态编号",
    "边数、操作数或第二维规模",
    "字符编号/边容量/候选对象",
    "源点编号或输入字符串",
    "当前输入值/查询值/坐标",
    "当前元素/顶点/状态数量",
    "当前排名、选取数量或循环层数",
    "当前字符、容量或第三个操作数",
    "当前距离、差值或覆盖增量",
    "当前质数、节点编号或指针",
    "当前输入数组/操作数",
    "当前相邻顶点/下一状态",
    "当前 0/1-based/DP 位置",
    "当前数组/字符串/DP 位置",
    "输出答案容器/引用",
    "准备返回的结果容器/结果值",
    "查询/修改闭区间",
    "规模/上界",
    "数量或模数",
    "（见本节定义）",
    "（见本节公式）",
    "（见本节类型）",
    "具体角色见所在公式",
    "本次调用处理的对象",
    "本次调用给出的数量",
    "本次调用处理的量",
    "本次调用处理的值",
    "本次算法处理的数值",
    "当前算法处理的对象数量",
    "当前算法处理的第二个数量",
    "当前步骤处理的对象",
    "当前步骤读取的第一个对象",
    "当前步骤读取的第二个对象",
    "当前步骤读取的第三个对象",
    "本接口的输入/输出量",
    "读取或写入的容器",
    "当前对象编号",
    "与 u 配对的对象编号",
    "执行“",
    "临时量",
    "值由本行初始化式确定",
    "当前步骤处理的数值",
    "当前步骤使用的数值",
    "当前步骤使用的整数",
    "当前步骤使用的增量",
    "当前步骤处理的第三个数值",
    "当前步骤使用的横坐标偏移",
    "当前处理对象的编号",
    "与 u 配对处理的对象编号",
    "与 x 配对处理的数值",
    "当前候选的数值",
    "准备由函数返回的结果",
    "当前算法维护的第二个数量",
    "当前算法处理的第二个数量",
    "当前累计数量",
    "当前长度",
    "当前累计和",
    "计数数组/当前计数",
    "当前几何点/向量/圆",
    "当前允许的阈值/上界",
    "左操作数/矩阵",
    "右操作数/矩阵",
    "输入规模",
    "输入数值",
    "输入数组 a",
    "输入数组 b",
    "第一个模数/第一部分规模",
    "第二个模数/第二部分规模",
    "当前几何点/向量/圆",
    "当前 0-based/DP 位置",
    "当前移动后的另一堆/另一状态",
    "输入点/向量",
    "当前输入字符串/源点",
    "待加入自动机的字符或字母表编号",
    "当前枚举的字符或字母表编号",
    "图/树的邻接表",
    "当前子集/博弈状态",
    "当前集合或自动机/DP 状态",
    "后缀/排列的当前排名",
    "数组容量/预处理上界",
    "当前数组或离散化下标",
    "当前增加量/仿射常数项",
    "当前树/版本的根节点",
    "当前已创建节点总数/累计数量",
    "排名/选取数量",
    "当前枚举的起点/源点",
    "测试用例数量或当前临时值",
    "当前容器迭代器/当前弧位置",
    "第二个参数方程解/临时元组",
    "当前 DFS 路径/输出路径",
    "是否已使用/选择",
    "当前搜索或自动机状态",
    "当前逆元/是否执行逆变换",
    "当前乘数/质因子贡献",
    "当前指数、质因子次数或边对象",
    "当前累计费用/边权和",
    "最短路/几何距离数组或当前距离",
    "当前累计/最终答案",
    "当前幂运算底数/基多项式",
    "当前高斯消元列/扫描列",
    "当前周长/周期",
    "图的邻接表/生成树拉普拉斯矩阵",
    "返回值含义见调用处条件",
    "回调函数的左操作数",
    "回调函数的右操作数",
    "节点 p/u",
    "当前查询对象 q",
    "当前组合数查询函数/结果矩阵",
    "当前判别式/距离量",
    "当前读入并交给字符串算法处理的字符串 s",
    "当前阶梯 Nim 的奇数层石子异或和 strip",
    "变换长度 n 在模 MOD 下的逆元 ni",
    "生成长度 n、字符来自 alphabet 的随机串",
    "返回指定点集/下标区间内最近点对距离",
    "给扫描线离散 y 闭区间增加覆盖计数 d",
    "当前步骤计算的第二个参数 t2",
    "把参数表示的数/字符串/版本插入当前结构",
    "执行本节定义的单点/区间增加或加入操作",
    "合并两个兼容对象/同余式",
    "由当前输入/成员状态完成数据结构预处理",
    "从当前节点/位置继续深度优先处理",
    "返回状态 x/u 的 Sprague-Grundy 值",
    "向残量网络/邻接表加入本节定义的一条边",
    "把一条候选直线插入当前李超树/单调凸包",
    "收集当前子树的距离/差分贡献到输出容器或父节点",
    "以当前连通块重心为根递归建立点分治/点分树",
    "把节点 p/x 的待下传标记传给孩子",
    "返回把 x 与当前集合/线性基元素组合后能得到的最大异或值",
    "左操作数",
    "右操作数",
    "矩阵/几何量",
    "下标或顶点数量",
    "给定位置/区间",
    "仿射乘数/矩阵乘积",
    "左边界/左半部分",
    "右边界/右半部分",
    "当前累计答案 ans",
    "本次写入或增加的数值 v",
    "内层循环下标 j",
    "当前循环下标 i",
    "普通顺序遍历中的当前下标 i",
    "普通 for 循环的机械索引 i",
    "纯机械遍历索引 i",
    "机械索引 i",
    "不可达/无穷大",
    "本节给出的单组测试/递归区间",
    "生成/变换 lambda",
    "随机/取值",
    "输入或生成的边",
    "线性基或字典树",
    "当前处理的二进制位/倍增层",
    "前缀和/前缀状态",
    "当前差值/差分数组",
    "当前事件/询问区间",
    "当前 BFS/单调算法",
    "当前从队列或栈",
    "累计和/频次",
    "当前查询范围高端/最高位",
    "当前可持久/可撤销",
    "返回/写入新版本根",
    "持久化节点或自动机节点",
    "第 k 小值/位置",
    "莫队/分块算法",
    "按 key/路径",
    "分支/值",
    "当前线段树/树结构",
    "按长度/拓扑顺序",
    "父侧贡献/倍增祖先",
    "自动机/DP 状态",
    "所有候选/事件",
    "流量上限/递归返回值",
    "并查集父节点数组/对象",
    "DFS/扫描使用",
    "顶点颜色/二分图染色",
    "层次/可达信息",
    "未删除树/子树",
    "排除父亲/禁用重儿子",
    "链顶/数组位置",
    "单位矩阵/恒等转移",
    "当前时间戳/懒标记",
    "当前元素/局面评估值",
    "当前总数/连通块规模",
    "n 堆/个石子",
    "凸包下链/下方候选",
    "多边形/交点集合",
    "DP 数组/答案",
    "本节条件成立/操作成功",
    "结果写入引用参数或当前结构状态",
    "题目定义或自动机节点状态",
    "最大状态或答案上界",
    "函数/对象的入口",
    "返回 true 表示上述接口描述成立",
    "本节核心逻辑",
)


# Source-level contracts tie reviewed prose to the exact formal listing that uses it.
# These catch plausible-looking comments that keyword-only lint cannot distinguish.
SOURCE_COMMENT_EXPECTATIONS = (
    (
        "banzi/板子_大版本.tex",
        "count_if(a.begin(), a.end(), [](int v){ return v > 0; });",
        ("判断当前数组元素 v 是否大于 0", "当前被 count_if 判断的数组元素 v"),
        ("右操作数", "返回值含义见调用处条件"),
    ),
    (
        "banzi/板子_大版本.tex",
        "for (int i = 0; i < k; i++) cout << a[i]",
        ("当前输出所选组合中第 i 个元素的下标 i",),
        ("二进制位/倍增层",),
    ),
    (
        "banzi/板子_大版本.tex",
        "int lb = s & (-s);",
        ("Gosper 枚举中当前掩码 s 的最低位 1 对应权值 lb",),
        ("权值/下界",),
    ),
    (
        "banzi/板子_大版本.tex",
        "// ===== 暴力做法（保证正确，不管复杂度）=====",
        ("当前从输入读取数组元素的下标 i",),
        ("二进制位/倍增层",),
    ),
    (
        "banzi/板子_大版本.tex",
        "void dfs2(int n)",
        ("枚举已排序 nums 的所有不重复全排列",),
        ("沿重链", "链顶 top"),
    ),
    (
        "banzi/板子_大版本.tex",
        "string randstr(int len)",
        ("长度为 len 的均匀随机小写字母字符串", "由 randstr 返回"),
        ("生成长度 n、字符来自 alphabet", "读入并交给字符串算法"),
    ),
    (
        "remake/large/06_图论.tex",
        "pair<bool, long long> prim(",
        ("Prim 使用的 0-based 加权无向图邻接表 g",),
        ("拉普拉斯矩阵",),
    ),
    (
        "remake/large/03_数学.tex",
        "vector<int> prufer_encode(const vector<vector<int>>& g)",
        ("1-based 标号树的无向邻接表 g", "当前删除第几个叶子的步骤下标 step"),
        ("拉普拉斯矩阵",),
    ),
    (
        "remake/large/03_数学.tex",
        "void ntt(vector<int>& a, bool inv)",
        ("位逆序置换中从最高有效位开始移动的掩码 bit", "当前蝶形位置使用的单位根幂 w"),
        ("下界 bit", "边权 w"),
    ),
    (
        "remake/large/10_几何.tex",
        "long double diameter2(const vector<Point>& p)",
        ("对踵点下标 j", "最大点对距离平方 ans", "下一个循环下标 ni"),
        ("内层循环下标 j", "累计答案 ans", "模 MOD 下的逆元"),
    ),
    (
        "remake/large/10_几何_详解.tex",
        "long double closest(int l, int r)",
        ("半开区间 [l,r)", "最近点对分治中靠近中线"),
        ("闭区间左端点", "阶梯 Nim"),
    ),
    (
        "remake/large/10_几何.tex",
        "long double closest(vector<Point>& p, int l, int r)",
        ("半开区间 [l,r)", "按 y 坐标升序排列当前最近点对半开区间"),
        ("闭区间左端点", "返回值含义见调用处条件"),
    ),
    (
        "remake/large/10_几何_详解.tex",
        "vector<Point> line_circle(Point p, Point v, Point o, long double r)",
        ("位移向量 q", "常数项 C", "判别式 D", "第二个交点对应的参数方程根 t2"),
        ("查询对象 q", "组合数查询", "判别式/距离量"),
    ),
    (
        "remake/large/10_几何_详解.tex",
        "void pull(int p, int l, int r)",
        ("重算扫描线节点 p 表示的实际覆盖长度", "半开区间 [l,r)"),
        ("节点 p/u",),
    ),
    (
        "remake/large/10_几何_详解.tex",
        "void modify(int p, int l, int r, int ql, int qr, int d)",
        ("半开区间 [ql,qr)", "覆盖计数增量 d"),
        ("离散 y 闭区间", "距离 d"),
    ),
    (
        "remake/large/10_几何.tex",
        "sort(h.begin(), h.end(), [](const HalfPlane& a, const HalfPlane& b)",
        ("按半平面边界方向角从小到大排序", "按方向维护有效边界的双端队列 q"),
        ("返回值含义见调用处条件", "左操作数", "右操作数"),
    ),
    (
        "remake/large/05_字符串_详解.tex",
        "for (char cc : text)",
        ("送入 AC 自动机的字符 cc", "当前加入 fail 树的 AC 自动机状态编号 u"),
        ("强连通分量", "二进制 Trie 根"),
    ),
    (
        "remake/large/06_图论.tex",
        "void build(int n_, vector<Edge> edges)",
        ("Kruskal 重构树为原点和合并点预留的数组容量 cap", "Kruskal 重构森林根"),
        ("当前边的剩余容量 cap", "二进制 Trie 根"),
    ),
    (
        "remake/large/10_几何.tex",
        "vector<Point> circle_circle(Circle a, Circle b)",
        ("两圆圆心之间的实际距离 dis", "两圆公共弦中点 base"),
        ("当前候选距离",),
    ),
    (
        "remake/large/09_博弈_详解.tex",
        "unsigned long long target = a[i] ^ all;",
        ("第 i 堆应剩余的石子数 target",),
        ("异或值/目标状态",),
    ),
    (
        "remake/large/04_数据结构_详解.tex",
        "int same = want ^ 1;",
        ("与查询值 x 当前二进制位相同的 Trie 分支编号 same",),
        ("两个对象是否相同/重合",),
    ),
    (
        "remake/large/10_几何.tex",
        "Point operator*(Real k) const",
        ("当前二维点向量乘实数系数 k", "向量数乘的实数系数 k"),
        ("矩阵/几何量",),
    ),
    (
        "remake/large/10_几何.tex",
        "vector<Point> line_circle(Point a, Point b, Circle c)",
        ("直线方向向量 d 的长度平方 dd",),
        (),
    ),
    (
        "remake/large/04_数据结构.tex",
        "SegTree(int n): n(n)",
        ("1-based 数组长度及最大下标 n", "目标区间内每个元素的统一增加量 v"),
        ("下标或顶点数量", "本次写入或增加的数值 v"),
    ),
    (
        "remake/large/04_数据结构.tex",
        "struct DSU {",
        ("第一个待合并元素编号 a", "第二个待合并元素编号 b"),
        ("左操作数", "右操作数"),
    ),
    (
        "remake/large/04_数据结构_详解.tex",
        "void range_add_linear(int l, int r, long long a, long long b)",
        ("一次项系数 a", "常数项 b"),
        ("左操作数", "右操作数"),
    ),
    (
        "remake/large/04_数据结构_详解.tex",
        "long long mul = 1;",
        ("全局仿射懒标记中作用于每个元素的乘法系数 mul",),
        ("仿射乘数/矩阵乘积",),
    ),
    (
        "remake/large/04_数据结构.tex",
        "int L = 1, R = 0, distinct = 0;",
        ("普通莫队当前 1-based 窗口的左端点 L", "窗口的右端点 R"),
        ("左边界/左半部分", "右边界/右半部分"),
    ),
    (
        "remake/large/04_数据结构_详解.tex",
        "int L = 1, R = 0, T = 0;",
        ("带修改莫队当前 1-based 窗口的左端点 L", "已经应用的修改次数 T"),
        ("测试用例数量 T", "左边界/左半部分"),
    ),
    (
        "remake/large/04_数据结构.tex",
        "long long query(int p, int l, int r, int ql, int qr)",
        ("返回目标闭区间 [ql,qr] 的元素和", "左右子树累加的区间和 ans"),
        ("给定位置/区间", "当前累计答案 ans"),
    ),
    (
        "remake/large/05_字符串.tex",
        "int query(const string& s)",
        ("返回全部模式串出现次数之和", "累计的全部模式匹配次数 ans"),
        ("给定位置/区间", "当前累计答案 ans"),
    ),
    (
        "remake/large/04_数据结构_详解.tex",
        "int query(int p, int l, int r, int pos)",
        ("位置 pos 保存的父节点值",),
        ("给定位置/区间",),
    ),
    (
        "remake/large/05_字符串.tex",
        "int j = pi[i - 1];",
        ("当前可回退的已匹配前缀长度 j", "正在计算 pi[i] 的字符串位置 i"),
        ("内层循环下标 j", "当前循环下标 i"),
    ),
    (
        "remake/large/03_数学.tex",
        "for (int i = 0; i < n; i += len)",
        ("蝶形块起始下标 i", "蝶形块内偏移下标 j"),
        ("当前循环下标 i", "内层循环下标 j"),
    ),
    (
        "banzi/板子_大版本.tex",
        "int cantor(vector<int>& p)",
        ("当前计算较小后继数量的排列位置 i", "统计较小元素的位置 j"),
        ("机械索引 i", "内层循环下标 j"),
    ),
    (
        "remake/large/04_数据结构_详解.tex",
        "void apply(int p, int l, int r, long long mul, long long add)",
        ("x->mul*x+add", "乘法系数 mul", "加法常数 add"),
        ("仿射乘数/矩阵乘积", "本次写入或增加的数值 v"),
    ),
    (
        "remake/large/04_数据结构_详解.tex",
        "int find_root(int root, int x)",
        ("版本 root 中沿父指针", "元素 x 当前父节点编号 f"),
        ("并查集父节点数组/对象",),
    ),
    (
        "remake/large/04_数据结构_详解.tex",
        "int merge_version(int root, int x, int y)",
        ("把 x 的代表元父指针设为 y 的代表元", "返回新版本根"),
        ("返回/写入新版本根",),
    ),
    (
        "remake/large/02_基础.tex",
        "int old = (int)res.size();",
        ("生成新子集和之前", "已有的元素数量 old"),
        ("当前修改前保存的旧值 old",),
    ),
    (
        "remake/large/05_字符串_详解.tex",
        "vector<int> sa(n), rk(n), tmp(n);",
        ("当前倍增长度", "长度 2k", "新等价类排名数组 tmp"),
        ("当前排名、选取数量或循环层数",),
    ),
    (
        "remake/large/05_字符串.tex",
        "int ri = i + k < n ? r[i + k] : -1;",
        ("偏移 k 后第二段的等价类排名 ri", "越界时为 -1"),
        ("当前第一关键字排名",),
    ),
    (
        "remake/large/05_字符串.tex",
        "int rj = j + k < n ? r[j + k] : -1;",
        ("偏移 k 后第二段的等价类排名 rj", "越界时为 -1"),
        ("当前第一关键字排名",),
    ),
    (
        "remake/large/05_字符串_详解.tex",
        "int ri = i + k < n ? rk[i+k] : -1;",
        ("偏移 k 后第二段的排名 ri", "越界时为 -1"),
        ("当前第一关键字排名",),
    ),
    (
        "remake/large/05_字符串_详解.tex",
        "int rj = j + k < n ? rk[j+k] : -1;",
        ("偏移 k 后第二段的排名 rj", "越界时为 -1"),
        ("当前第一关键字排名",),
    ),
    (
        "remake/large/08_动态规划_详解.tex",
        "int nst = ns ? go[st][d] : 0;",
        ("自动机状态 st 后放置数字 d", "前导零时保持起点 0"),
        ("自动机/DP 状态",),
    ),
    (
        "remake/large/09_博弈_详解.tex",
        "unsigned long long all = 0;",
        ("所有堆石子数的异或和 all",),
        ("当前总数/连通块规模",),
    ),
    (
        "remake/large/06_图论.tex",
        "int f = t[x].fa;",
        ("节点 x 当前辅助树父节点编号 f",),
        ("并查集父节点数组/对象",),
    ),
)


def source_files() -> list[Path]:
    text = ENTRY.read_text(encoding="utf-8")
    paths = [ENTRY]
    paths.extend(ROOT / item for item in re.findall(r"\\inputnewboard\{([^}]+)\}", text))
    return paths


def plain_heading(raw: str) -> str:
    raw = re.sub(r"\\(?:texttt|passthrough|texorpdfstring)\{([^{}]*)\}", r"\1", raw)
    raw = raw.replace(r"\_", "_")
    return re.sub(r"\\[A-Za-z]+", "", raw).strip() or "当前专题"


def section_before(text: str, offset: int) -> str:
    heading = "竞赛模板"
    for match in HEADING_RE.finditer(text, 0, offset):
        heading = plain_heading(match.group(1))
    return heading


def split_params(raw: str) -> list[str]:
    if not raw.strip() or raw.strip() == "void":
        return []
    parts: list[str] = []
    start = 0
    depth = 0
    for i, ch in enumerate(raw):
        if ch in "<([{":
            depth += 1
        elif ch in ">)]}":
            depth = max(0, depth - 1)
        elif ch == "," and depth == 0:
            parts.append(raw[start:i].strip())
            start = i + 1
    parts.append(raw[start:].strip())
    return parts


def actual_params(match: re.Match[str]) -> str:
    """Return text inside the first balanced parentheses of a function."""
    text = match.group(0)
    left = text.find("(")
    if left < 0:
        return ""
    depth = 0
    for i in range(left, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return text[left + 1:i]
    return match.group("params")


def param_name(decl: str) -> str:
    decl = decl.split("=", 1)[0].strip()
    match = re.search(r"([A-Za-z_]\w*)\s*(?:\[\s*\])?\s*$", decl)
    return match.group(1) if match else "?"


def return_type(match: re.Match[str]) -> str:
    value = " ".join((match.group("prefix") + match.group("return")).split())
    value = re.sub(r"^(?:static|inline|virtual|constexpr|consteval|friend|explicit)\s+", "", value)
    return value or "构造函数"


def has_interface_comment(body: str, start: int, name: str) -> bool:
    before = body[:start].splitlines()
    needle = f"接口：{name}("
    return any(needle in line for line in before[-16:])


def generated_comment_before(body: str, start: int, name: str) -> tuple[int, int, str] | None:
    """Return the canonical generated block immediately before an interface."""
    prefix = body[:start]
    pattern = re.compile(
        rf"(?m)(?P<block>^[ \t]*// 接口：{re.escape(name)}\([^\n]*\r?\n"
        rf"(?:^[ \t]*// 参数：[^\n]*\r?\n)?)"
        rf"(?=(?:^[ \t]*// 变量：[^\n]*\r?\n)*\Z)"
    )
    match = pattern.search(prefix)
    if not match:
        return None
    return match.start("block"), match.end("block"), match.group("block")


def ambiguous_comment(text: str) -> bool:
    return any(phrase in text for phrase in AMBIGUOUS_COMMENT_PHRASES)


def state_note(name: str, return_value: str) -> str:
    if return_value == "构造函数":
        return "构造并初始化对象；每组测试建议重新构造"
    if name in {"main", "solve"}:
        return "入口函数；每组测试前按注释清空全局状态"
    if name in {"init", "build"}:
        return "完成初始化；多测时每组重新调用"
    if name in {
        "insert", "add", "update", "modify", "apply", "push", "pull", "push_up",
        "push_down", "extend", "rotate", "splay", "access", "makeroot", "link",
        "cut", "rollback", "add_edge", "add_line", "add_path", "add_subtree",
    }:
        return "会修改当前结构；多测时重新构造或显式清空成员"
    if return_value == "void":
        return "不返回值"
    if return_value == "bool":
        return "返回类型 bool"
    return f"返回类型 {return_value}"


SEGMENT_NODE_FUNCTIONS = {
    "apply", "push", "pull", "build", "update", "query", "modify",
    "range_chmin", "apply_chmin", "push_chmin", "first_at_least",
}

GRAPH_VERTEX_FUNCTIONS = {
    "find", "unite", "dfs", "bfs", "add_edge", "tarjan", "aug",
    "lca", "bottleneck", "component_node", "component_size", "farthest",
    "init_lca", "add_path", "collect", "tree_dp", "dfs1", "dfs2",
    "divide", "dfs_size", "add_subtree", "dsu_on_tree", "dsu",
    "dfs_len", "dfs_chain", "decompose", "get_size", "get_centroid",
    "long_chain_dfs1", "long_chain_dfs2", "reroot1", "reroot2",
    "is_root", "apply_rev", "rotate", "splay", "access", "makeroot",
    "findroot", "link", "cut", "path_sum",
}

VALUE_X_FUNCTIONS = {
    "print_i128", "print128", "lowbit", "is_pow2", "insert", "maximum",
    "can", "max_xor", "qpow", "get", "value", "point_value",
    "add_number", "grundy", "xor_prefix",
}

PARAMETER_OVERRIDES = {
    ("cantor", "p"): "待计算排名的 0-based 排列 p",
    ("inv_cantor", "rank"): "待还原的 0-based Cantor 排名 rank",
    ("inv_cantor", "n"): "待还原排列的长度 n",
    ("rand_tree", "n"): "随机树的顶点数 n",
    ("rand_graph", "n"): "随机图的顶点数 n",
    ("rand_graph", "m"): "随机图的边数 m",
    ("rand_distinct", "n"): "需要生成的整数个数 n",
    ("rand_perm", "n"): "随机排列的长度 n",
    ("xor_n", "m"): "异或前缀的右端点 m",
    ("add_pos", "p"): "加入莫队窗口的数组位置 p",
    ("del_pos", "p"): "移出莫队窗口的数组位置 p",
    ("mod_pow", "p"): "幂运算使用的正模数 p",
    ("Csmall", "p"): "组合数运算使用的质数模数 p",
    ("lucas", "p"): "Lucas 定理使用的质数模数 p",
    ("Lucas", "p"): "Lucas 定理使用的质数模数 p",
    ("tonelli_shanks", "p"): "需要求平方根的奇质数模数 p",
    ("legendre", "p"): "Legendre 符号使用的奇质数模数 p",
    ("on_segment", "p"): "待判断是否在线段 ab 上的点 p",
    ("left_of", "p"): "待判断相对有向直线位置的点 p",
    ("outside", "p"): "待判断是否在半平面外的点 p",
    ("polar_cmp", "i"): "第一个待比较向量的下标 i",
    ("polar_cmp", "j"): "第二个待比较向量的下标 j",
    ("update", "pos"): "持久化线段树中要修改的 0-based 位置 pos",
    ("query", "pos"): "持久化线段树中要查询的 0-based 位置 pos",
    ("solve_digit", "pos"): "当前处理到的十进制数位下标 pos",
    ("dfs", "pos"): "当前处理到的十进制数位下标 pos",
    ("transitive_closure", "reach"): "邻接可达矩阵 reach，调用后变为传递闭包",
    ("transitive_closure", "n"): "参与闭包计算的顶点数 n",
    ("bitset_closure", "reach"): "邻接可达矩阵 reach，调用后变为传递闭包",
    ("bitset_closure", "n"): "参与闭包计算的顶点数 n",
    ("geometry_bitset_closure", "reach"): "几何关系的邻接矩阵 reach，调用后变为传递闭包",
    ("geometry_bitset_closure", "n"): "参与闭包计算的几何对象数 n",
    ("print128", "x"): "待十进制输出的 __int128 整数 x",
    ("print_i128", "x"): "待十进制输出的 __int128 整数 x",
    ("dfs", "n"): "待生成排列的长度 n",
    ("dfs2", "n"): "待生成排列的长度 n",
    ("lowbit", "x"): "要求最低位 1 权值的整数 x",
    ("is_pow2", "x"): "待判定是否为 2 的幂的正整数 x",
    ("enumerate_submasks", "n"): "被枚举全部非零子集的位掩码 n",
    ("gen", "a"): "提供下标区间 [l,r] 元素的输入数组 a",
    ("mitm_max_subset_sum", "a"): "待选择子集的非负整数数组 a",
    ("minimize_max_segment_sum", "a"): "待划分的非负整数数组 a",
    ("minimize_max_segment_sum", "k"): "允许划分的最大连续段数 k",
    ("factor", "n"): "待试除分解的正整数 n",
    ("Csmall", "n"): "组合数 C(n,k) 的上标 n",
    ("lucas", "n"): "组合数 C(n,k) 的上标 n",
    ("Lucas", "n"): "组合数 C(n,k) 的上标 n",
    ("merge_congruence", "a"): "合并后余数的输入输出引用 a",
    ("merge_congruence", "m"): "合并后正模数的输入输出引用 m",
    ("Mat", "n"): "矩阵阶数 n",
    ("operator*", "A"): "矩阵乘法的第一个输入矩阵 A",
    ("operator*", "B"): "矩阵乘法的第二个输入矩阵 B",
    ("mpow", "a"): "待求幂的方阵 a",
    ("expected_dag", "u"): "期望过程的起始状态编号 u",
    ("xor_prefix", "n"): "异或前缀的非负右端点 n",
    ("fib", "n"): "Fibonacci 序列下标 n",
    ("fibonacci", "n"): "Fibonacci 序列下标 n",
    ("ways", "k"): "计数模型中需要选择的元素数 k",
    ("burnside", "group"): "群中每个元素对应的置换列表 group",
    ("burnside", "perm"): "群中每个元素对应的置换列表 perm",
    ("prufer_encode", "g"): "1..n 编号树的无向邻接表 g",
    ("prufer_decode", "code"): "待解码的 Prüfer 序列 code",
    ("tree_count", "lap"): "删去一行一列后的拉普拉斯矩阵 lap",
    ("tonelli_shanks", "n"): "需要求模平方根的剩余 n",
    ("ntt", "a"): "原地执行正变换或逆变换的系数数组 a",
    ("gauss", "a"): "待消元的增广矩阵 a",
    ("gauss_mod", "a"): "待做模意义消元的增广矩阵 a",
    ("gauss_real", "a"): "待做实数高斯消元的增广矩阵 a",
    ("gauss_real", "ans"): "接收唯一解的输出数组 ans",
    ("BigInteger", "text"): "待解析的十进制整数字符串 text",
    ("read", "text"): "待解析的十进制整数字符串 text",
    ("multiply_small", "factor"): "乘到当前大整数上的 uint32_t 因子 factor",
    ("shift_base_add", "block"): "追加到当前大整数最低 BASE 进制位的块 block",
    ("operator>>", "in"): "提供十进制整数文本的输入流 in",
    ("operator<<", "out"): "接收十进制整数文本的输出流 out",
    ("abs_big", "x"): "待取绝对值的任意精度整数 x",
    ("pow_mod_big", "exponent"): "任意精度的非负指数 exponent",
    ("linear_sieve_mu", "n"): "筛法计算的正整数上界 n",
    ("multiply", "a"): "卷积的左系数数组 a",
    ("multiply", "b"): "卷积的右系数数组 b",
    ("DSU", "n"): "并查集管理的元素编号上界 n",
    ("RollbackDSU", "n"): "可回滚并查集管理的元素编号上界 n",
    ("KruskalDSU", "n"): "Kruskal 并查集管理的顶点数 n",
    ("find", "x"): "待查询代表元的元素编号 x",
    ("unite", "x"): "第一个待合并元素编号 x",
    ("unite", "y"): "第二个待合并元素编号 y",
    ("unite", "a"): "第一个待合并元素编号 a",
    ("unite", "b"): "第二个待合并元素编号 b",
    ("qpow", "a"): "待求模幂的底数 a",
    ("mod_pow", "a"): "待求模幂的底数 a",
    ("mul_mod", "a"): "模乘的第一个整数因子 a",
    ("mul_mod", "b"): "模乘的第二个整数因子 b",
    ("exgcd", "a"): "扩展欧几里得的第一个整数输入 a",
    ("exgcd", "b"): "扩展欧几里得的第二个整数输入 b",
    ("legendre", "a"): "待判断二次剩余性的整数 a",
    ("bsgs", "a"): "离散对数方程 a^x=b (mod mod) 的底数 a",
    ("bsgs", "b"): "离散对数方程 a^x=b (mod mod) 的目标剩余 b",
    ("range_add_linear", "a"): "位置 i 增量 a*i+b 的一次项系数 a",
    ("range_add_linear", "b"): "位置 i 增量 a*i+b 的常数项 b",
    ("BIT", "n"): "树状数组管理的最大下标 n",
    ("Fenwick", "n"): "树状数组管理的最大下标 n",
    ("add", "x"): "树状数组的 1-based 修改位置 x",
    ("sum", "x"): "树状数组前缀查询的右端点 x",
    ("first_at_least", "x"): "查询要求达到的值下界 x",
    ("SparseTable", "a"): "用于构造静态区间表的输入数组 a",
    ("difference_constraints", "n"): "差分约束系统的变量个数 n",
    ("difference_constraints", "edges"): "约束 x_v-x_u<=w 的三元组集合 edges",
    ("kth", "u"): "左端前缀版本根 u",
    ("kth", "v"): "右端前缀版本根 v",
    ("kth", "k"): "查询的 1-based 排名 k",
    ("size", "u"): "待统计大小的 Treap 子树根 u",
    ("pull", "u"): "待重算大小的 Treap 节点 u",
    ("split", "u"): "待拆分的 Treap 根 u",
    ("split", "x"): "接收拆分后左 Treap 根的引用 x",
    ("split", "y"): "接收拆分后右 Treap 根的引用 y",
    ("merge", "x"): "待合并的左 Treap 根 x",
    ("merge", "y"): "待合并的右 Treap 根 y",
    ("Line", "k"): "直线斜率 k",
    ("Line", "b"): "直线截距 b",
    ("get", "x"): "计算直线函数值的横坐标 x",
    ("add_line", "nw"): "待插入李超树的直线 nw",
    ("SegBeats", "a"): "用于构造线段树的 1-based 初始数组 a",
    ("build", "a"): "用于构造当前数据结构的初始数组 a",
    ("apply_chmin", "x"): "节点最大值要压低到的上界 x",
    ("push_chmin", "x"): "节点最大值要压低到的上界 x",
    ("range_chmin", "x"): "目标区间元素要压低到的上界 x",
    ("chmin", "x"): "目标区间元素要压低到的上界 x",
    ("apply_change", "c"): "待应用或撤销的离线修改记录 c",
    ("process_query", "q"): "待移动莫队窗口并回答的离线询问 q",
    ("cdq", "a"): "按 x 排序并在 CDQ 中累计二维偏序贡献的点数组 a",
    ("prefix_function", "s"): "待计算前缀函数的字符串 s",
    ("kmp", "text"): "被搜索的主串 text",
    ("kmp", "pat"): "待查找的模式串 pat",
    ("z_function", "s"): "待计算 Z 函数的字符串 s",
    ("count_word", "s"): "待统计完整出现次数的字符串 s",
    ("count_prefix", "s"): "待统计前缀出现次数的字符串 s",
    ("suffix_array", "s"): "待构造后缀数组的字符串 s",
    ("kasai", "s"): "后缀数组对应的原字符串 s",
    ("kasai", "sa"): "原字符串的后缀数组 sa",
    ("scan", "text"): "供自动机扫描匹配的主串 text",
    ("bfs_dist", "g"): "无权图邻接表 g",
    ("bfs_dist", "s"): "单源 BFS 的源点编号 s",
    ("multi_source_bfs", "g"): "无权图邻接表 g",
    ("multi_source_bfs", "sources"): "全部 BFS 源点编号 sources",
    ("kruskal", "n"): "无向图顶点数 n",
    ("kruskal", "edges"): "无向带权边集合 edges",
    ("prim", "g"): "无向带权图邻接表 g",
    ("max_bipartite_matching", "g"): "左部点到右部点的邻接表 g",
    ("max_bipartite_matching", "right_n"): "右部顶点数 right_n",
    ("add_edge", "c"): "Dinic 正向边容量 c",
    ("bfs", "s"): "层次图的源点编号 s",
    ("bfs", "t"): "层次图的汇点编号 t",
    ("dfs", "t"): "增广目标汇点编号 t",
    ("min_cost_flow", "s"): "费用流源点编号 s",
    ("min_cost_flow", "t"): "费用流汇点编号 t",
    ("init_lca", "p"): "当前顶点 u 的父节点 p",
    ("farthest", "s"): "树上最远点搜索的起点 s",
    ("add_node", "delta"): "颜色出现次数的增量 delta，加入为 1，移除为 -1",
    ("collect", "ds"): "接收当前子树距离的输出数组 ds",
    ("zero_one_knapsack", "items"): "每个元素为重量和价值的物品表 items",
    ("zero_one_knapsack", "W"): "背包容量上限 W",
    ("complete_knapsack", "items"): "每个元素为重量和价值的物品表 items",
    ("complete_knapsack", "W"): "背包容量上限 W",
    ("window_min_dp", "base"): "每个位置的基础代价数组 base",
    ("window_min_dp", "k"): "允许转移的最大向前距离 k",
    ("grundy", "x"): "待求 SG 值的游戏状态 x",
    ("nim_first_win", "piles"): "标准 Nim 各堆石子数 piles",
    ("misere_nim_first_win", "piles"): "反常 Nim 各堆石子数 piles",
    ("bash_first_win", "n"): "Bash 游戏当前石子数 n",
    ("bash_first_win", "k"): "每步最多取走的石子数 k",
    ("mex", "values"): "需要求 mex 的非负整数集合 values",
    ("first_win", "starts"): "各独立子游戏的起始状态编号 starts",
    ("solve_subtraction", "n"): "待求 SG 值的石子数 n",
    ("solve_subtraction", "moves"): "每步允许取走的石子数集合 moves",
    ("mex_by_stamp", "values"): "需要求 mex 的非负整数集合 values",
    ("mex_by_stamp", "seen"): "记录各值最后出现时间戳的数组 seen",
    ("nim_move", "a"): "标准 Nim 各堆石子数 a",
    ("bash_win", "n"): "Bash 游戏当前石子数 n",
    ("bash_win", "k"): "每步最多取走的石子数 k",
    ("misere_nim_win", "a"): "反常 Nim 各堆石子数 a",
    ("staircase_nim_win", "a"): "阶梯 Nim 每层石子数 a",
    ("subtraction_sg", "moves"): "每步允许取走的石子数集合 moves",
    ("find_period", "sg"): "已计算并待验证周期的 SG 序列 sg",
    ("alpha_beta", "s"): "当前搜索状态 s",
    ("area2", "p"): "按边界顺序给出的多边形顶点 p",
    ("convex_hull", "p"): "待求凸包的点集 p",
    ("diameter2", "p"): "按逆时针顺序给出的凸多边形顶点 p",
    ("sweep_area", "events"): "按横坐标排序的矩形扫描线事件 events",
    ("sweep_area", "covered_length"): "返回当前 y 轴覆盖总长的回调 covered_length",
    ("sweep_area", "update"): "更新 y 区间覆盖次数的回调 update",
    ("sweep_area", "y_id"): "把 y 坐标映射为离散下标的回调 y_id",
    ("closest", "p"): "按 x 坐标维护的点数组 p",
    ("clip", "poly"): "待裁剪的凸多边形顶点 poly",
    ("half_plane_intersection", "h"): "待求交的有向半平面集合 h",
    ("min_circle", "p"): "待覆盖的输入点集 p",
    ("union_area", "e"): "矩形并面积的扫描线事件 e",
    ("normalize_direction", "dx"): "待规范化方向的横坐标分量 dx",
    ("normalize_direction", "dy"): "待规范化方向的纵坐标分量 dy",
    ("operator+", "b"): "加到当前点或向量上的向量 b",
    ("operator-", "b"): "从当前点或向量中减去的向量 b",
    ("operator*", "k"): "点向量数乘的实数系数 k",
    ("cross", "a"): "叉积左向量 a",
    ("cross", "b"): "叉积右向量 b",
    ("dot", "a"): "点积左向量 a",
    ("dot", "b"): "点积右向量 b",
    ("sgn", "x"): "待按 EPS 判断符号的实数 x",
    ("dist2", "a"): "距离平方的第一个端点 a",
    ("dist2", "b"): "距离平方的第二个端点 b",
    ("left_of", "a"): "有向直线起点 a",
    ("left_of", "b"): "有向直线终点 b",
    ("on_segment", "a"): "闭线段第一个端点 a",
    ("on_segment", "b"): "闭线段第二个端点 b",
    ("intersect", "a"): "第一条闭线段的起点 a",
    ("intersect", "b"): "第一条闭线段的终点 b",
    ("intersect", "c"): "第二条闭线段的起点 c",
    ("intersect", "d"): "第二条闭线段的终点 d",
    ("line_circle", "a"): "直线上的第一个点 a",
    ("line_circle", "b"): "直线上的第二个点 b",
    ("line_circle", "c"): "待求交的圆 c",
    ("line_circle", "p"): "直线经过的基点 p",
    ("line_circle", "v"): "直线方向向量 v",
    ("line_circle", "o"): "圆心 o",
    ("line_circle", "r"): "圆的非负半径 r",
    ("circle_circle", "r"): "以 a 为圆心的圆半径 r",
    ("circle_circle", "R"): "以 b 为圆心的圆半径 R",
    ("prim", "g"): "Prim 使用的 0-based 加权无向图邻接表 g；每项为 (终点,边权)",
    ("prufer_encode", "g"): "1-based 标号树的无向邻接表 g",
    ("bfs_dist", "g"): "0-based 无权图邻接表 g",
    ("multi_source_bfs", "g"): "0-based 无权图邻接表 g",
    ("max_bipartite_matching", "g"): "左部点到右部点的二分图邻接表 g",
    ("closest", "l"): "待处理 0-based 半开区间 [l,r) 的左端点 l",
    ("closest", "r"): "待处理 0-based 半开区间 [l,r) 的右端点 r",
    ("modify", "d"): "本次加入或移除的覆盖计数增量 d",
    ("clip", "a"): "裁剪半平面边界的起点 a",
    ("clip", "b"): "裁剪半平面边界的终点 b",
    ("line_inter", "a"): "第一条有向边界直线 a",
    ("line_inter", "b"): "第二条有向边界直线 b",
    ("intersection", "a"): "第一条有向半平面边界 a",
    ("intersection", "b"): "第二条有向半平面边界 b",
    ("half", "a"): "待分类到上下半平面的向量 a",
    ("polar_cmp", "a"): "第一个待比较极角的向量 a",
    ("polar_cmp", "b"): "第二个待比较极角的向量 b",
}


def parameter_meaning(name: str, parameter: str, declaration: str, section: str) -> str:
    if name == "apply" and parameter in {"mul", "add"}:
        affine_roles = {
            "mul": "新仿射变换 x->mul*x+add 的乘法系数 mul",
            "add": "新仿射变换 x->mul*x+add 的加法常数 add",
        }
        return affine_roles[parameter]
    if name == "find_root" and parameter in {"root", "x"}:
        return {
            "root": "保存当前并查集父指针数组的持久化线段树版本根 root",
            "x": "要在版本 root 中查找代表元的元素编号 x",
        }[parameter]
    if name == "merge_version" and parameter in {"root", "x", "y"}:
        return {
            "root": "作为本次合并起点的持久化并查集版本根 root",
            "x": "第一个待合并集合中的元素编号 x",
            "y": "第二个待合并集合中的元素编号 y",
        }[parameter]
    if name in {"pull", "modify"} and "扫描线" in section:
        scan_roles = {
            "p": "当前覆盖长度线段树节点编号 p（根为 1）",
            "l": "节点 p 表示的离散下标半开区间 [l,r) 左端点 l",
            "r": "节点 p 表示的离散下标半开区间 [l,r) 右端点 r",
            "ql": "目标离散下标半开区间 [ql,qr) 左端点 ql",
            "qr": "目标离散下标半开区间 [ql,qr) 右端点 qr",
            "d": "本次加入或移除的覆盖计数增量 d",
        }
        if parameter in scan_roles:
            return scan_roles[parameter]
    if "Link-Cut" in section or "动态树" in section:
        if parameter in {"x", "y"}:
            return f"Link-Cut Tree 中的原树顶点编号 {parameter}"
    if name in {"extend", "add"} and parameter == "c" and (
        "字符串" in section or "自动机" in section
    ):
        if re.search(r"\bchar\b", declaration):
            return "待加入自动机的字符 c"
        return "待加入自动机的 0-based 字母表编号 c"
    if name == "get_fail" and parameter in {"u", "x"}:
        return f"开始沿 fail 链检查的自动机状态编号 {parameter}"
    if name in {"add", "remove"} and parameter == "p" and "莫队" in section:
        action = "加入" if name == "add" else "移出"
        return f"要{action}当前莫队窗口的数组位置 p"
    if name == "add" and parameter == "p":
        return "当前线段树节点编号 p（根通常为 1）"
    if name in {"query", "get"} and parameter == "x" and "李超" in section:
        return "计算候选直线最优值的横坐标 x"
    if name == "add_line" and parameter == "k":
        return "待插入直线的斜率 k"
    if name == "add_line" and parameter == "b":
        return "待插入直线的截距 b"
    if name == "id" and parameter == "x":
        return "待映射到离散排名的原坐标 x"
    if name == "C" and parameter == "n":
        return "组合数 C(n,k) 的上标 n"
    if name == "C" and parameter == "k":
        return "组合数 C(n,k) 的下标 k"
    if name == "merge" and parameter in {"a", "m", "b", "n"}:
        roles = {
            "a": "第一个同余式余数及合并后余数的输入输出引用 a",
            "m": "第一个同余式模数及合并后模数的输入输出引用 m",
            "b": "第二个同余式的余数 b",
            "n": "第二个同余式的正模数 n",
        }
        return roles[parameter]
    if name == "sum" and parameter == "x":
        return "树状数组前缀查询的 1-based 右端点 x"
    if name == "find_root" and parameter == "x":
        return "待查找并查集代表元的元素编号 x"
    if name == "merge_version" and parameter in {"x", "y"}:
        return f"待合并集合中的元素编号 {parameter}"
    if name in {"mul", "operator*"} and parameter in {"A", "B"}:
        side = "左" if parameter == "A" else "右"
        return f"矩阵乘法的{side}操作数 {parameter}"
    if name == "circle_circle" and parameter in {"a", "b"}:
        ordinal = "第一个" if parameter == "a" else "第二个"
        if re.search(r"\bCircle\b", declaration):
            return f"{ordinal}输入圆 {parameter}"
        if re.search(r"\bPoint\b", declaration):
            return f"{ordinal}输入圆的圆心 {parameter}"
    override = PARAMETER_OVERRIDES.get((name, parameter))
    if override:
        return override
    if parameter == "p" and name in SEGMENT_NODE_FUNCTIONS:
        return "当前线段树节点编号 p（根通常为 1）"
    if re.search(r"\b(?:vector|array|deque|set|map|unordered_|priority_queue)\b", declaration):
        container_roles = {
            "a": "输入数组 a", "b": "输入数组 b", "edges": "输入边集合 edges",
            "fac": "阶乘表 fac", "ifac": "逆阶乘表 ifac",
            "group": "群作用置换列表 group", "perm": "置换列表 perm",
            "piles": "各堆石子数 piles", "moves": "每步允许取走的石子数集合 moves",
            "values": "需要求 mex 的非负整数集合 values",
            "seen": "mex 时间戳数组 seen", "starts": "各独立子游戏的起始状态 starts",
            "sg": "待检查周期的 SG 序列 sg", "poly": "凸多边形顶点序列 poly",
            "sa": "后缀数组 sa", "code": "Prüfer 序列 code", "lap": "拉普拉斯矩阵 lap",
            "g": "图的邻接表 g", "ans": "接收结果的输出数组 ans",
        }
        if parameter in container_roles:
            return container_roles[parameter]
        raise ValueError(f"unresolved container parameter {name}({parameter}): {declaration}")
    if re.search(r"\bstring\b", declaration):
        string_roles = {
            "s": "输入字符串 s", "str": "待构建自动机的完整字符串 str",
            "text": "输入文本 text", "pat": "输入模式串 pat",
        }
        if parameter in string_roles:
            return string_roles[parameter]
        raise ValueError(f"unresolved string parameter {name}({parameter}): {declaration}")
    if re.search(r"\bPoint\b", declaration):
        raise ValueError(f"unresolved Point parameter {name}({parameter}): {declaration}")
    if re.search(r"\bCircle\b", declaration):
        raise ValueError(f"unresolved Circle parameter {name}({parameter}): {declaration}")
    if re.search(r"\bLine\b", declaration):
        line_roles = {
            "a": "按斜率顺序的第一条候选直线 a",
            "b": "按斜率顺序的中间候选直线 b",
            "c": "按斜率顺序的第三条候选直线 c",
            "line": "待插入的候选直线 line", "nw": "待插入的候选直线 nw",
            "x": "待插入的候选直线 x",
        }
        if parameter in line_roles:
            return line_roles[parameter]
        raise ValueError(f"unresolved Line parameter {name}({parameter}): {declaration}")
    if re.search(r"\b(?:Edge|Query|Change|Mat|Matrix)\b", declaration):
        raise ValueError(f"unresolved structured parameter {name}({parameter}): {declaration}")
    if parameter == "p":
        if any(word in section for word in ("数论", "组合数", "卢卡斯", "二次剩余", "模")):
            return "题目给定的正模数 p"
        if any(word in section for word in ("图论", "树", "剖分", "点分治")):
            return "当前节点 u 的父节点 p"
        if any(word in section for word in ("几何", "向量", "浮点", "线段", "圆", "半平面", "凸包")):
            return "输入点 p"
    if parameter in {"a", "b", "c"} and name in {"bad", "useless"}:
        return f"按斜率顺序相邻的候选直线 {parameter}"
    if parameter == "x" and name == "add_line":
        return "待插入的候选直线 x"
    if parameter == "k" and any(
        word in section for word in ("几何", "向量", "浮点")
    ):
        return "向量数乘的实数系数 k"
    if parameter in {"x", "y"} and name == "exgcd":
        return f"输出引用 {parameter}，满足 a*x+b*y=gcd(a,b)"
    if parameter in {"u", "v"} and name in GRAPH_VERTEX_FUNCTIONS:
        role = "当前顶点" if parameter == "u" else "与 u 配对的顶点"
        return f"{role}编号 {parameter}"
    if parameter == "x" and name in VALUE_X_FUNCTIONS:
        value_roles = {
            "insert": "待插入线性基或字典树的数值 x",
            "maximum": "求最大异或值时使用的初始值 x",
            "can": "待判断能否被线性基表示的数值 x",
            "max_xor": "求最大异或值时使用的初始值 x",
            "qpow": "待求幂的底数 x", "get": "直线取值的横坐标 x",
            "value": "直线取值的横坐标 x", "point_value": "单点查询的下标 x",
            "add_number": "待加入统计结构的整数 x", "grundy": "待求 SG 值的状态 x",
            "xor_prefix": "异或前缀的右端点 x",
        }
        if name in value_roles:
            return value_roles[name]
    if parameter == "v" and name in {"add", "apply"} and all(
        token in declaration for token in ("int p", "int l", "int r")
    ):
        return "目标区间内每个元素的统一增加量 v"
    if parameter == "v" and name == "add" and re.search(
        r"\badd\s*\(\s*int\s+x\s*,", declaration
    ):
        return "树状数组位置 x 的点增加量 v"
    if parameter == "v" and name == "add" and re.search(
        r"\badd\s*\(\s*int\s+l\s*,\s*int\s+r", declaration
    ):
        return "闭区间 [l,r] 内每个元素的统一增加量 v"
    if parameter == "v" and name in {"add", "apply", "update", "modify"}:
        return "本次写入或增加的数值 v"
    if parameter == "n" and name == "SegTree":
        return "线段树管理的 1-based 数组长度及最大下标 n"
    if parameter == "n" and name == "LCT":
        return "Link-Cut Tree 管理的 1-based 顶点数量 n"
    if parameter == "n" and name in {"DSU", "BIT", "Fenwick"}:
        return PARAMETER_OVERRIDES[(name, "n")]
    if parameter == "k" and name in {"Csmall", "lucas", "Lucas"}:
        return "组合数 C(n,k) 的下标 k"
    if parameter == "m" and any(
        word in section for word in ("同余", "模运算", "中国剩余", "数论")
    ):
        return "正模数 m"
    if parameter in PARAM_MEANING:
        return PARAM_MEANING[parameter]
    raise ValueError(f"unresolved scalar parameter {name}({parameter}): {declaration}")


def function_purpose(name: str, declaration: str, section: str) -> str:
    """Resolve repeated short function names from signature and section context."""
    if name == "apply" and all(token in declaration for token in ("mul", "add")):
        return "把 x->mul*x+add 作用于节点 p 的区间和，并按新操作在外的顺序合成懒标记"
    if name == "find_root" and all(token in declaration for token in ("root", "x")):
        return "在持久化并查集版本 root 中只读地沿父指针返回元素 x 的代表元"
    if name == "merge_version" and all(token in declaration for token in ("root", "x", "y")):
        return "从版本 root 合并 x、y 的代表元，把 x 根的父指针改为 y 根并返回新版本根"
    if name == "dfs2":
        if "全排列" in section or re.search(r"\bdfs2\s*\(\s*int\s+n\s*\)", declaration):
            return "枚举已排序 nums 的所有不重复全排列并逐个输出"
        return "沿重链优先编号并填写每个顶点的链顶 top"
    if name == "randstr":
        return "生成并返回长度为 len 的均匀随机小写字母字符串"
    if name == "closest":
        return "返回 0-based 半开区间 [l,r) 内最近点对距离"
    if name == "pull":
        if re.search(r"\bpull\s*\(\s*int\s+p\s*,\s*int\s+l\s*,\s*int\s+r", declaration):
            return "按覆盖计数和两个孩子重算扫描线节点 p 表示的实际覆盖长度"
        if re.search(r"\bpull\s*\(\s*int\s+u", declaration):
            return "由左右孩子重算 Treap 节点 u 的子树大小"
        if re.search(r"\bpull\s*\(\s*int\s+p", declaration):
            return "由两个孩子重算线段树节点 p 的聚合信息"
    if name == "modify" and "扫描线" in section:
        return "给扫描线离散下标半开区间 [ql,qr) 增加覆盖计数 d"
    if name == "operator*":
        if re.search(r"\boperator\*\s*\(\s*Real\s+k", declaration):
            return "返回当前二维点向量乘实数系数 k 的数乘结果"
        if "Mat" in declaration:
            return "返回输入矩阵 A 与 B 的矩阵乘积"
    if name == "query":
        if all(token in declaration for token in ("int p", "int l", "int r", "int ql", "int qr")):
            return "返回目标闭区间 [ql,qr] 的元素和"
        if all(token in declaration for token in ("x", "int p", "int l", "int r")) and "__int128" in declaration:
            return "返回横坐标 x 处沿李超树查询路径得到的最优直线函数值"
        if re.search(r"\bquery\s*\(\s*(?:ll|long long|int)\s+x\s*\)", declaration) and "__int128" in declaration:
            return "返回李超树中全部候选直线在横坐标 x 处的最优函数值"
        if re.search(r"\bquery\s*\([^\)]*string", declaration):
            return "扫描主串 s 并返回全部模式串出现次数之和"
        if all(token in declaration for token in ("int p", "int l", "int r", "int pos")):
            return "返回持久化线段树版本 p 在位置 pos 保存的父节点值"
    if name == "dfs":
        if re.search(r"\bdfs\s*\(\s*int\s+n\s*\)", declaration):
            return "枚举并逐个输出 1..n 的全部排列"
        if all(token in declaration for token in ("pos", "tight", "started", "st")):
            return "返回给定数位 DP 状态的合法后缀方案数"
        if "parent_edge" in declaration:
            return "从 u 继续无向图 Tarjan，填写 dfn/low 并收集桥"
        if all(token in declaration for token in ("int u", "int t", "long long f")):
            return "在 Dinic 层次图上从 u 向汇点 t 推送至多 f 的阻塞流"
        if re.search(r"\bdfs\s*\(\s*int\s+u\s*,\s*int\s+p", declaration):
            return "为以 u 为根的子树填写 DFS 序、深度和子树区间"
    if name == "insert":
        if "old" in declaration and "bit" in declaration:
            return "从旧版本根复制路径，向持久化二进制 Trie 插入数值 x 并返回新根"
        if re.search(r"\binsert\s*\([^\)]*string", declaration):
            return "把小写模式串 s 插入 Trie，并在终止节点累计出现次数"
        if "线性基" in section:
            return "把数值 x 消元后插入线性基；线性相关时保持基不变"
        if re.search(r"\binsert\s*\(\s*U\s+x", declaration):
            return "把数值 x 消元后插入线性基；线性相关时保持基不变"
        if "Trie" in section or "字典树" in section:
            return "把整数 x 的各二进制位插入 Trie"
    if name == "max_xor":
        if "left_root" in declaration:
            return "在两个前缀版本之差表示的区间内返回与 x 的最大异或值"
        if "线性基" in section:
            return "返回把 x 与当前线性基中若干向量异或后的最大值"
        if re.search(r"\bmax_xor\s*\(\s*U\s+x", declaration):
            return "返回把 x 与当前线性基中若干向量异或后的最大值"
        if "Trie" in section or "字典树" in section:
            return "沿二进制 Trie 贪心返回与 x 的最大异或值"
    if name == "add":
        if re.search(r"\badd\s*\(\s*char\s+", declaration):
            return "向回文自动机追加字符，更新 last 并返回新的最长回文后缀状态编号"
        if re.search(r"\badd\s*\(\s*int\s+x\s*,", declaration):
            return "把增量 v 加到树状数组的 1-based 位置 x"
        if all(token in declaration for token in ("int p", "int l", "int r", "int ql", "int qr")):
            return "把目标闭区间 [ql,qr] 的元素统一增加 v"
        if re.search(r"\badd\s*\(\s*int\s+l\s*,\s*int\s+r", declaration):
            return "用分块懒标记把闭区间 [l,r] 的元素统一增加 v"
    if name == "merge":
        if all(token in declaration for token in ("a", "m", "b", "n")) and "long long&" in declaration:
            return "合并 x≡a(mod m) 与 x≡b(mod n)，不相容时返回 false"
        if re.search(r"\bmerge\s*\(\s*int\s+x\s*,\s*int\s+y", declaration):
            return "按优先级合并键值有序的左右 Treap，并返回新根"
    if name == "build":
        if "edges" in declaration:
            return "按边权建立 Kruskal 重构树并预处理深度、子树大小和倍增祖先"
        if all(token in declaration for token in ("int p", "int l", "int r", "vector<")):
            return "由 1-based 数组 a 建立区间 chmin 与区间和线段树"
        if re.search(r"\bbuild\s*\(\s*int\s+l\s*,\s*int\s+r", declaration):
            return "建立覆盖闭区间 [l,r] 的初始持久化线段树版本"
        if re.search(r"\bbuild\s*\(\s*\)", declaration):
            return "用 BFS 建立 AC 自动机 fail 指针、补全转移并汇总输出计数"
        if re.search(r"\bbuild\s*\([^\)]*string", declaration):
            return "清空回文自动机，依次加入 str 的字符并沿 fail 汇总出现次数"
    if name == "push":
        if re.search(r"\bpush\s*\(\s*int\s+x", declaration):
            return "把 LCT 辅助树节点 x 的路径反转标记下传给两个儿子"
        if re.search(r"\bpush\s*\(\s*int\s+p\s*,\s*int\s+l", declaration):
            return "把线段树节点 p 的懒标记下传到左右孩子并清空本节点标记"
        if re.search(r"\bpush\s*\(\s*int\s+p\s*\)", declaration):
            return "把 Segment Tree Beats 节点 p 的最大值上界约束下传给两个孩子"
    if name == "add_line":
        if all(token in declaration for token in ("nw", "int p", "int l", "int r")):
            return "把候选直线 nw 插入整数横坐标闭区间 [l,r] 的李超树节点 p"
        if re.search(r"\badd_line\s*\(\s*(?:ll|long long)\s+k\s*,", declaration):
            return "把斜率 k、截距 b 组成的直线插入李超树"
        if "Line" in declaration:
            return "按单调斜率加入候选直线，并从队尾删除永不最优的直线"
    if name == "add_edge":
        if "cost" in declaration:
            return "向最小费用流残量网络加入容量 cap、费用 cost 的边及其反向边"
        if re.search(r"\badd_edge\s*\([^\)]*\bc\b", declaration):
            return "向 Dinic 残量网络加入容量 c 的边及零容量反向边"
    if name == "collect":
        if all(token in declaration for token in ("int u", "int fa", "int d", "vector<int>& ds")):
            return "收集未删除子树中各节点到当前点分治重心的距离"
        if re.search(r"\bcollect\s*\(\s*int\s+u\s*,\s*int\s+p", declaration):
            return "后序累加树上路径差分，把孩子贡献汇总到父节点"
    if name == "decompose" and "entry" in declaration:
        return "找出 entry 所在未删除连通块的重心并递归分解各子块"
    if name == "grundy":
        return "返回状态参数对应的 Sprague-Grundy 值并记忆化"
    if name not in PURPOSE:
        raise ValueError(
            f"cannot safely infer function purpose for {name!r}: {declaration.strip()}"
        )
    purpose = PURPOSE[name]
    if name in CONTEXT_SENSITIVE_PURPOSE_NAMES or ambiguous_comment(purpose):
        raise ValueError(
            f"cannot safely infer context-sensitive function purpose for {name!r}: "
            f"{declaration.strip()}"
        )
    return purpose


def build_comment(match: re.Match[str], section: str) -> str:
    name = match.group("name").replace(" ", "")
    params = split_params(actual_params(match))
    names = [param_name(p) for p in params]
    shown = ", ".join(names)
    purpose = function_purpose(name, match.group(0), section)
    meanings = [
        parameter_meaning(name, n, decl, section)
        for n, decl in zip(names, params)
        if n != "?"
    ]
    ret = return_type(match)
    first = f"// 接口：{name}({shown})：{purpose}；{state_note(name, ret)}。"
    if not meanings:
        return first
    second = "// 参数：" + "；".join(meanings) + "。"
    return first + "\n" + second


def lambda_name(line: str) -> str:
    named = re.search(r"\bauto\s+([A-Za-z_]\w*)\s*=", line)
    if named:
        return named.group(1)
    if "sort" in line or "unique" in line:
        return "比较器 lambda"
    if "count_if" in line:
        return "判定 lambda"
    if "generate" in line:
        return "生成 lambda"
    if "transform" in line:
        return "变换 lambda"
    return "匿名 lambda"


def lambda_semantics(
    line: str, section: str, names: list[str]
) -> tuple[str, list[str]]:
    """Return the concrete callback contract and parameter roles for one lambda."""
    compact = re.sub(r"\s+", " ", line.strip())
    if "count_if" in compact:
        return "判断当前数组元素 v 是否大于 0", ["当前被 count_if 判断的数组元素 v"]
    if "generate" in compact:
        return "调用 rng() 生成当前要写入数组的随机值", []
    if "transform" in compact:
        return "返回输入元素 x 的两倍并写入目标数组", ["当前被 transform 变换的输入元素 x"]
    if "auto check" in compact and "其他实用工具" in section:
        return "示范二分答案判定接口；调用者必须把函数体替换为题目的 mid 可行性条件", ["当前待判定的二分答案 mid"]
    if "sort(idx.begin(), idx.end()" in compact:
        return "按 a[i]、a[j] 的值升序排列下标", ["第一个候选下标 i", "第二个候选下标 j"]
    if "auto range_sum" in compact:
        return "返回 1-based 闭区间 [l,r] 的前缀和差", ["查询闭区间左端点 l", "查询闭区间右端点 r"]
    if "auto range_add" in compact:
        return "在差分数组中记录 1-based 闭区间 [l,r] 增加 v", ["修改闭区间左端点 l", "修改闭区间右端点 r", "区间增加量 v"]
    if "auto check" in compact and "二分答案" in section:
        return "判断能否把非负数组分成至多 k 段且每段和不超过 limit", ["当前候选的最大允许分段和 limit"]
    if "x.second < y.second" in compact or "典型证明模式" in section:
        return "按区间右端点从小到大排序，供不相交区间贪心选择", ["第一个候选区间 x", "第二个候选区间 y"]
    if "x.deadline < y.deadline" in compact or "反悔贪心" in section:
        return "按任务截止时间从小到大排序", ["第一个候选任务 x", "第二个候选任务 y"]
    if "auto id" in compact:
        return "返回原坐标 x 在有序离散数组 xs 中的 0-based 下标", ["待离散化的原坐标 x"]
    if "checked_lcm" in compact:
        return "安全计算 lcm(a,b)，溢出 long long 时返回 nullopt", ["第一个整数 a", "第二个整数 b"]
    if "auto C" in compact:
        return "返回预处理阶乘下的组合数 C(n,k) mod MOD，越界时返回 0", ["组合数上标 n", "组合数下标 k"]
    if "sort(qs.begin(), qs.end()" in compact:
        return "按莫队左端块排序，并在同块内按奇偶交替排列右端点", ["第一个莫队查询 x", "第二个莫队查询 y"]
    if "auto add" in compact and "莫队" in section:
        return "把位置 p 加入莫队窗口，并在该值首次出现时增加 distinct", ["要加入窗口的数组位置 p"]
    if "auto remove" in compact and "莫队" in section:
        return "把位置 p 移出莫队窗口，并在该值不再出现时减少 distinct", ["要移出窗口的数组位置 p"]
    if "Point& A" in compact or "三维偏序" in section:
        return "按点的 y 坐标升序归并 CDQ 子区间", ["第一个候选点 A", "第二个候选点 B"]
    if "auto get_hash" in compact:
        return "返回字符串 0-based 半开区间 [l,r) 的哈希值", ["子串左端点 l", "子串右端点 r（不含）"]
    if "sort(sa.begin(), sa.end()" in compact or "后缀数组" in section:
        return "按长度 2k 的两段排名二元组比较后缀 i 与 j", ["第一个后缀起点 i", "第二个后缀起点 j"]
    if "sort(ord.begin(), ord.end()" in compact or "回文自动机" in section:
        return "按回文长度从大到小排列自动机状态，供出现次数沿 fail 链汇总", ["第一个回文状态 a", "第二个回文状态 b"]
    if "Edge &a" in compact or "Kruskal 重构树" in section:
        return "按边权从小到大排列 Kruskal 候选边", ["第一条候选边 a", "第二条候选边 b"]
    if "function<bool(int)> aug" in compact:
        return "从左部点 u 尝试寻找一条二分图增广路并返回是否成功", ["当前尝试增广的左部点 u"]
    if "unique(p.begin(), p.end()" in compact:
        return "判断两个点 a、b 的坐标是否完全相同，供凸包输入去重", ["第一个候选点 a", "第二个候选点 b"]
    if "sort(p.begin(), p.end()" in compact and "凸包" in section:
        return "按 x 升序、再按 y 升序排列输入点", ["第一个候选点 a", "第二个候选点 b"]
    if "sort(events.begin(), events.end()" in compact:
        return "按扫描线事件的 x 坐标升序排列", ["第一个扫描线事件 a", "第二个扫描线事件 b"]
    if "sort(p.begin() + l, p.begin() + r" in compact:
        return "按 y 坐标升序排列当前最近点对半开区间中的点", ["第一个候选点 a", "第二个候选点 b"]
    if "Point a, Point b" in compact and "最近点对" in section:
        return "按 y 坐标升序归并最近点对的左右子区间", ["第一个候选点 a", "第二个候选点 b"]
    if "HalfPlane& a" in compact or "半平面交" in section:
        return "按半平面边界方向角从小到大排序", ["第一个候选半平面 a", "第二个候选半平面 b"]
    if "sort(e.begin(), e.end()" in compact and "扫描线" in section:
        return "按矩形扫描线事件的 y 坐标升序排列", ["第一个扫描线事件 a", "第二个扫描线事件 b"]
    raise ValueError(f"unresolved lambda semantics in {section}: {compact}")


def build_lambda_comment(match: re.Match[str], section: str) -> str:
    name = lambda_name(match.group("line"))
    params = split_params(match.group("params"))
    names = [param_name(p) for p in params]
    purpose, meanings = lambda_semantics(match.group("line"), section, names)
    first = f"// 接口：{name}({', '.join(names)})：{purpose}。"
    if not meanings:
        return first
    return first + "\n// 参数：" + "；".join(meanings) + "。"


def annotate_body(body: str, section: str, refresh: bool = False) -> tuple[str, int]:
    matches: list[tuple[int, re.Match[str], str]] = [
        (match.start(), match, "function")
        for match in FUNCTION_RE.finditer(body)
        if match.group("name").replace(" ", "") not in CONTROL_NAMES
    ]
    matches.extend((match.start(), match, "lambda") for match in LAMBDA_RE.finditer(body))
    inserted = 0
    for _, match, kind in sorted(matches, key=lambda item: item[0], reverse=True):
        name = (
            match.group("name").replace(" ", "")
            if kind == "function"
            else lambda_name(match.group("line"))
        )
        existing = generated_comment_before(body, match.start(), name)
        if existing:
            if not refresh or not ambiguous_comment(existing[2]):
                continue
        elif has_interface_comment(body, match.start(), name):
            continue
        comment = build_comment(match, section) if kind == "function" else build_lambda_comment(match, section)
        indent = match.group("indent")
        comment = "\n".join(indent + line if line else line for line in comment.splitlines()) + "\n"
        if existing:
            body = body[:existing[0]] + comment + body[existing[1]:]
            inserted += 1
            continue
        insertion = match.start()
        body = body[:insertion] + comment + body[insertion:]
        inserted += 1
    return body, inserted


def strip_generated_comments(text: str) -> str:
    lines = text.splitlines(keepends=True)
    kept: list[str] = []
    drop_parameter = False
    for line in lines:
        # Generated lines always contain “函数名(...)：说明；状态/返回。”.
        generated_interface = bool(
            re.match(r"^[ \t]*// 接口：.*\)：.*；.*。", line)
        )
        if generated_interface:
            drop_parameter = True
            continue
        if drop_parameter and re.match(r"^[ \t]*// 参数：", line):
            drop_parameter = False
            continue
        drop_parameter = False
        kept.append(line)
    return "".join(kept)


def annotate_file(path: Path, refresh: bool = False) -> int:
    text = path.read_text(encoding="utf-8")
    inserted = 0
    pieces: list[str] = []
    cursor = 0
    for listing in LISTING_RE.finditer(text):
        pieces.append(text[cursor:listing.start()])
        section = section_before(text, listing.start())
        body, count = annotate_body(listing.group("body"), section, refresh=refresh)
        pieces.extend((listing.group("open"), body, listing.group("close")))
        inserted += count
        cursor = listing.end()
    pieces.append(text[cursor:])
    if inserted:
        path.write_text("".join(pieces), encoding="utf-8", newline="\n")
    return inserted


def generation_errors(refresh: bool) -> list[str]:
    """Preflight every block that would be inserted or safely refreshed."""
    errors: list[str] = []
    for path in source_files():
        text = path.read_text(encoding="utf-8")
        for listing in LISTING_RE.finditer(text):
            body = listing.group("body")
            section = section_before(text, listing.start())
            base_line = text[:listing.start("body")].count("\n") + 1
            matches = [
                (match, "function") for match in FUNCTION_RE.finditer(body)
                if match.group("name").replace(" ", "") not in CONTROL_NAMES
            ]
            matches.extend((match, "lambda") for match in LAMBDA_RE.finditer(body))
            for match, kind in matches:
                name = match.group("name").replace(" ", "") if kind == "function" else lambda_name(match.group("line"))
                existing = generated_comment_before(body, match.start(), name)
                needs_generation = not has_interface_comment(body, match.start(), name)
                needs_refresh = refresh and existing is not None and ambiguous_comment(existing[2])
                if not (needs_generation or needs_refresh):
                    continue
                try:
                    if kind == "function":
                        build_comment(match, section)
                    else:
                        build_lambda_comment(match, section)
                except ValueError as exc:
                    line = base_line + body[:match.start()].count("\n")
                    errors.append(f"{path.relative_to(ROOT)}:{line}: {exc}")
    return errors


def audit() -> list[Hit]:
    hits: list[Hit] = []
    for path in source_files():
        text = path.read_text(encoding="utf-8")
        for listing_no, listing in enumerate(LISTING_RE.finditer(text), 1):
            body = listing.group("body")
            section = section_before(text, listing.start())
            base_line = text[:listing.start("body")].count("\n") + 1
            for match in FUNCTION_RE.finditer(body):
                name = match.group("name").replace(" ", "")
                if name in CONTROL_NAMES:
                    continue
                hits.append(
                    Hit(
                        path=path.relative_to(ROOT),
                        listing=listing_no,
                        line=base_line + body[:match.start()].count("\n"),
                        name=name,
                        params=[param_name(p) for p in split_params(actual_params(match))],
                        section=section,
                        annotated=has_interface_comment(body, match.start(), name),
                    )
                )
            for match in LAMBDA_RE.finditer(body):
                hits.append(
                    Hit(
                        path=path.relative_to(ROOT),
                        listing=listing_no,
                        line=base_line + body[:match.start()].count("\n"),
                        name=lambda_name(match.group("line")),
                        params=[param_name(p) for p in split_params(match.group("params"))],
                        section=section,
                        annotated=has_interface_comment(
                            body, match.start(), lambda_name(match.group("line"))
                        ),
                    )
                )
    return hits


def audit_struct_fields() -> list[FieldHit]:
    """Audit public template state whose meaning must be known by callers."""
    hits: list[FieldHit] = []
    declaration_re = re.compile(
        r"^(?:(?:static|const|constexpr)\s+)*(?:[\w:<>,*&\[\] ]+)\s+[^();]+;"
    )
    for path in source_files():
        text = path.read_text(encoding="utf-8")
        for listing_no, listing in enumerate(LISTING_RE.finditer(text), 1):
            body = listing.group("body")
            lines = body.splitlines()
            base_line = text[:listing.start("body")].count("\n") + 1
            stack: list[tuple[str, int]] = []
            depth = 0
            for index, line in enumerate(lines):
                stripped = line.strip()
                struct = re.search(r"\b(?:struct|class)\s+([A-Za-z_]\w*)[^;{]*\{", line)
                if struct:
                    stack.append((struct.group(1), depth + line[:struct.end()].count("{")))
                    tail = line[struct.end():]
                    if ";" in tail and "(" not in tail:
                        hits.append(
                            FieldHit(
                                path=path.relative_to(ROOT),
                                listing=listing_no,
                                line=base_line + index,
                                owner=struct.group(1),
                                declaration=tail.split("}", 1)[0].strip(),
                                annotated="//" in line,
                            )
                        )
                if stack and depth == stack[-1][1]:
                    is_decl = bool(declaration_re.match(stripped))
                    is_type_alias = stripped.startswith(("using ", "typedef ", "return "))
                    if is_decl and not is_type_alias and "(" not in stripped:
                        previous = lines[index - 1].strip() if index else ""
                        hits.append(
                            FieldHit(
                                path=path.relative_to(ROOT),
                                listing=listing_no,
                                line=base_line + index,
                                owner=stack[-1][0],
                                declaration=stripped,
                                annotated="//" in line or previous.startswith("//"),
                            )
                        )
                depth += line.count("{") - line.count("}")
                while stack and depth < stack[-1][1]:
                    stack.pop()
    return hits


def duplicate_dict_key_issues() -> list[str]:
    """Report duplicate literal keys before Python can silently overwrite them."""
    issues: list[str] = []
    for path in (Path(__file__), ROOT / "tools" / "audit_large_variables.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            seen: dict[object, int] = {}
            for key in node.keys:
                if not isinstance(key, ast.Constant) or not isinstance(key.value, (str, int, float)):
                    continue
                if key.value in seen:
                    issues.append(
                        f"{path.relative_to(ROOT)}:{key.lineno}: duplicate dict key "
                        f"{key.value!r}; first defined at line {seen[key.value]}"
                    )
                else:
                    seen[key.value] = key.lineno
    return issues


def source_comment_expectation_issues() -> list[str]:
    """Check reviewed source comments against exact high-risk listing contexts."""
    issues: list[str] = []
    texts = {
        path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8")
        for path in source_files()
    }
    for source, code_needle, required, forbidden in SOURCE_COMMENT_EXPECTATIONS:
        text = texts.get(source)
        if text is None:
            issues.append(f"{source}: source semantic expectation file is not rendered")
            continue
        matches = [
            match.group("body") for match in LISTING_RE.finditer(text)
            if code_needle in match.group("body")
        ]
        if len(matches) != 1:
            issues.append(
                f"{source}: semantic expectation selector {code_needle!r} matched "
                f"{len(matches)} listings; expected exactly one"
            )
            continue
        body = matches[0]
        for phrase in required:
            if phrase not in body:
                issues.append(
                    f"{source}: listing {code_needle!r} is missing required semantic "
                    f"phrase {phrase!r}"
                )
        for phrase in forbidden:
            if phrase in body:
                issues.append(
                    f"{source}: listing {code_needle!r} retains forbidden semantic "
                    f"phrase {phrase!r}"
                )
    return issues


def semantic_comment_issues() -> list[str]:
    """Reject known name-only boilerplate in the complete rendered source tree."""
    issues: list[str] = []
    prefixes = ("// 接口：", "// 参数：", "// 变量：", "// 字段：")
    for path in source_files():
        lines = path.read_text(encoding="utf-8").splitlines()
        for line_no, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped.startswith(prefixes):
                continue
            for phrase in AMBIGUOUS_COMMENT_PHRASES:
                if phrase in stripped:
                    issues.append(
                        f"{path.relative_to(ROOT)}:{line_no}: ambiguous semantic comment "
                        f"contains {phrase!r}: {stripped}"
                    )
                    break
            next_code = ""
            for candidate in lines[line_no:line_no + 6]:
                candidate = candidate.strip()
                if candidate and not candidate.startswith("//"):
                    next_code = candidate
                    break
            conflicts: list[str] = []
            if re.search(r"\b(?:Point|Circle)\b", next_code) and any(
                phrase in stripped for phrase in ("线段树节点", "模数 p", "顶点编号")
            ):
                conflicts.append("geometry type conflicts with node/modulus wording")
            if "circle_circle" in next_code and any(
                phrase in stripped for phrase in ("闭区间右端点 r", "闭区间右端点 R")
            ):
                conflicts.append("circle radius is described as an interval endpoint")
            relative = str(path.relative_to(ROOT)).replace("\\", "/")
            if "Prüfer" in stripped and "/03_" not in relative:
                conflicts.append("Prüfer wording escapes the mathematics chapter")
            if "字符串自动机" in stripped and "/08_" in relative:
                conflicts.append("string-automaton wording escapes into dynamic programming")
            if "/10_" in relative and any(
                phrase in stripped for phrase in ("阶梯 Nim", "NTT", "组合数查询", "查询对象 q")
            ):
                conflicts.append("non-geometry wording escapes into the geometry chapter")
            if "closest" in next_code and "闭区间" in stripped:
                conflicts.append("closest uses [l,r) but is described as a closed interval")
            if "modify" in next_code and "/10_" in relative and "闭区间" in stripped:
                conflicts.append("scanline modify uses [ql,qr) but is described as a closed interval")
            for conflict in conflicts:
                issues.append(
                    f"{path.relative_to(ROOT)}:{line_no}: semantic type/context conflict: "
                    f"{conflict}: {stripped}"
                )
    issues.extend(source_comment_expectation_issues())
    issues.extend(duplicate_dict_key_issues())
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="insert missing interface comments")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help=(
            "replace only canonical generated blocks rejected by the semantic audit; "
            "valid and non-canonical reviewed comments are preserved"
        ),
    )
    args = parser.parse_args()

    if args.write or args.refresh:
        errors = generation_errors(refresh=args.refresh)
        if errors:
            print(f"semantic inference errors: {len(errors)}")
            for error in errors:
                print(error)
            return 1
        total = 0
        for path in source_files():
            count = annotate_file(path, refresh=args.refresh)
            if count:
                print(f"annotated {count:3d}  {path.relative_to(ROOT)}")
            total += count
        verb = "inserted/refreshed" if args.refresh else "inserted"
        print(f"{verb}: {total}")

    hits = audit()
    missing = [hit for hit in hits if not hit.annotated]
    fields = audit_struct_fields()
    missing_fields = [field for field in fields if not field.annotated]
    semantic_issues = semantic_comment_issues()
    print(f"functions/methods audited: {len(hits)}")
    print(f"with interface comments:  {len(hits) - len(missing)}")
    print(f"missing comments:         {len(missing)}")
    for hit in missing:
        print(f"{hit.path}:{hit.line}: {hit.name} ({hit.section})")
    print(f"struct field lines audited: {len(fields)}")
    print(f"missing field comments:    {len(missing_fields)}")
    for field in missing_fields:
        print(f"{field.path}:{field.line}: {field.owner}::{field.declaration}")
    print(f"semantic comment issues:   {len(semantic_issues)}")
    for issue in semantic_issues:
        print(issue)
    return bool(missing or missing_fields or semantic_issues)


if __name__ == "__main__":
    raise SystemExit(main())
