#!/usr/bin/env python3
"""Audit and (optionally) annotate C++ interfaces in the large handbook.

The rendered order is taken from banzi/板子_大版本.tex.  Only lstlisting
blocks are inspected, so TeX commands and prose examples are not mistaken for
C++ interfaces.
"""

from __future__ import annotations

import argparse
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
}

PARAM_MEANING = {
    "n": "规模/上界 n",
    "N": "最大状态或答案上界 N",
    "m": "数量或模数 m（见本节公式）",
    "a": "输入值/数组 a（见本节定义）",
    "b": "输入值/数组 b（见本节定义）",
    "x": "待处理值或点/状态 x",
    "y": "待处理值或点/状态 y",
    "u": "顶点/状态编号 u",
    "v": "顶点/状态编号 v",
    "fa": "父节点 fa",
    "p": "当前节点/模数 p（见本节定义）",
    "l": "闭区间左端点 l",
    "r": "闭区间右端点 r",
    "L": "闭区间左端点 L",
    "R": "闭区间右端点 R",
    "ql": "查询/修改闭区间左端 ql",
    "qr": "查询/修改闭区间右端 qr",
    "pos": "当前 0-based/DP 位置 pos",
    "k": "排名/选取数量 k",
    "mod": "正模数 mod",
    "e": "非负指数 e",
    "s": "输入字符串 s",
    "text": "主串 text",
    "pat": "模式串 pat",
    "start": "起点/起始状态 start",
    "lim": "允许的阈值 lim",
    "limit": "判定阈值 limit",
    "delta": "本次增量 delta",
    "v": "顶点/状态编号 v",
    "value": "写入或查询的值 value",
    "tight": "前缀是否仍贴住上界 tight",
    "started": "是否已经放置非前导零数字 started",
    "rem": "当前余数状态 rem",
    "entry": "当前连通块入口 entry",
    "need": "希望发送的流量 need",
    "invert": "是否执行逆变换 invert",
    "rank": "0-based Cantor 排名 rank",
    "lo": "随机/取值闭区间下界 lo",
    "hi": "随机/取值闭区间上界 hi",
    "len": "目标字符串长度 len",
    "argc": "命令行参数个数 argc",
    "argv": "命令行参数数组 argv",
    "a1": "第一个同余式的余数 a1",
    "m1": "第一个同余式的正模数 m1",
    "a2": "第二个同余式的余数 a2",
    "m2": "第二个同余式的正模数 m2",
    "ident": "是否构造单位矩阵 ident",
    "A": "左操作数/矩阵 A",
    "B": "右操作数/矩阵 B",
    "MOD": "运算使用的正模数 MOD",
    "base": "幂运算的底多项式 base",
    "group": "所有群作用置换的列表 group",
    "colors": "可用颜色数 colors",
    "g": "图的邻接表/生成树拉普拉斯矩阵 g（见本节）",
    "code": "Prüfer 序列 code",
    "lap": "删去一行一列后的拉普拉斯矩阵 lap",
    "inv": "是否执行逆变换 inv",
    "sum": "当前累计值 sum",
    "fac": "阶乘数组 fac[i]=i! mod p",
    "ifac": "逆阶乘数组 ifac[i]=(i!)^{-1} mod p",
    "perm": "一个 0-based 置换 perm",
    "ans": "输出答案容器/引用 ans",
    "old": "旧版本根节点编号 old",
    "key": "拆分键 key",
    "snap": "此前 snapshot() 返回的撤销栈长度 snap",
    "nw": "待插入的新直线 nw",
    "i": "当前 0/1-based 位置 i（见接口区间约定）",
    "mul": "仿射标记乘数 mul",
    "forward": "true=应用修改，false=撤销修改",
    "q": "当前查询对象 q",
    "bit": "当前处理的二进制位 bit",
    "left_root": "区间左端前一个前缀版本根 left_root",
    "right_root": "区间右端前缀版本根 right_root",
    "val": "写入的新值 val",
    "root": "当前版本/树的根节点编号 root",
    "c": "字符编号/边容量/候选对象 c（见本节）",
    "ch": "待加入字符 ch",
    "str": "待完整构建的字符串 str",
    "edges": "输入边集合 edges",
    "n_": "原图点数 n_",
    "parent_edge": "DFS 进入 u 所用的无向边编号 parent_edge",
    "cap": "边容量 cap",
    "cost": "每单位流费用 cost",
    "s": "源点编号或输入字符串 s（见本节类型）",
    "t": "汇点编号或目标状态 t",
    "f": "本次 DFS 允许继续发送的流量 f",
    "topf": "当前重链链顶 topf",
    "top": "当前长链/重链链顶 top",
    "keep": "是否保留 u 子树统计贡献 keep",
    "d": "当前距离/覆盖增量 d",
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
    "o": "用于比较/哈希的另一个对象 o",
    "mid": "当前二分/区间中点 mid",
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
        return "无返回值；结果写入引用参数或当前结构状态"
    if return_value == "bool":
        return "返回 true 表示本节条件成立/操作成功"
    return f"返回类型 {return_value}"


def parameter_meaning(name: str, parameter: str, section: str) -> str:
    if parameter == "p":
        if any(word in section for word in ("线段树", "扫描线", "树状数组")):
            return "当前线段树节点编号 p（根通常为 1）"
        if any(word in section for word in ("数论", "组合数", "卢卡斯", "二次剩余", "模")):
            return "题目给定的质数/正模数 p"
        if any(word in section for word in ("图论", "树", "剖分", "点分治")):
            return "当前节点 u 的父节点 p"
        if any(word in section for word in ("几何", "向量", "浮点", "线段", "圆", "半平面", "凸包")):
            return "输入点 p"
    if parameter in {"a", "b", "c"} and any(
        word in section for word in ("几何", "向量", "浮点", "线段", "圆", "半平面", "凸包")
    ):
        return f"输入点/向量 {parameter}"
    if parameter == "d" and any(
        word in section for word in ("几何", "向量", "浮点", "线段", "圆", "半平面", "凸包")
    ):
        return "第四个输入点/向量 d"
    if parameter in {"a", "b", "c"} and name in {"bad", "useless"}:
        return f"按斜率顺序相邻的候选直线 {parameter}"
    if parameter == "x" and name == "add_line":
        return "待插入的候选直线 x"
    if parameter == "k" and any(
        word in section for word in ("几何", "向量", "浮点")
    ):
        return "向量数乘的实数系数 k"
    if parameter in {"a", "b"} and any(
        word in section for word in ("数组", "序列", "排序", "子序列")
    ):
        return f"输入数组/序列 {parameter}"
    if parameter in {"x", "y"} and name == "exgcd":
        return f"输出引用 {parameter}，满足 a*x+b*y=gcd(a,b)"
    if parameter == "m" and any(
        word in section for word in ("同余", "模运算", "中国剩余", "数论")
    ):
        return "正模数 m"
    return PARAM_MEANING.get(parameter, f"{parameter}=本接口的输入/输出量（含义见本节公式）")


def build_comment(match: re.Match[str], section: str) -> str:
    name = match.group("name").replace(" ", "")
    params = split_params(actual_params(match))
    names = [param_name(p) for p in params]
    shown = ", ".join(names)
    purpose = PURPOSE.get(name, f"执行“{section}”中的 {name} 操作")
    meanings = [parameter_meaning(name, n, section) for n in names if n != "?"]
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
    if "generate" in line or "transform" in line:
        return "生成/变换 lambda"
    return "匿名 lambda"


def build_lambda_comment(match: re.Match[str], section: str) -> str:
    name = lambda_name(match.group("line"))
    params = split_params(match.group("params"))
    names = [param_name(p) for p in params]
    meanings = [parameter_meaning(name, n, section) for n in names if n != "?"]
    first = (
        f"// 接口：{name}({', '.join(names)})：供“{section}”当前语句回调；"
        "返回值含义见调用处条件。"
    )
    if not meanings:
        return first
    return first + "\n// 参数：" + "；".join(meanings) + "。"


def annotate_body(body: str, section: str) -> tuple[str, int]:
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
        if has_interface_comment(body, match.start(), name):
            continue
        comment = build_comment(match, section) if kind == "function" else build_lambda_comment(match, section)
        insertion = match.start()
        indent = match.group("indent")
        comment = "\n".join(indent + line if line else line for line in comment.splitlines()) + "\n"
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


def annotate_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    inserted = 0
    pieces: list[str] = []
    cursor = 0
    for listing in LISTING_RE.finditer(text):
        pieces.append(text[cursor:listing.start()])
        section = section_before(text, listing.start())
        body, count = annotate_body(listing.group("body"), section)
        pieces.extend((listing.group("open"), body, listing.group("close")))
        inserted += count
        cursor = listing.end()
    pieces.append(text[cursor:])
    if inserted:
        path.write_text("".join(pieces), encoding="utf-8", newline="\n")
    return inserted


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="insert missing interface comments")
    parser.add_argument("--refresh", action="store_true", help="replace generated interface comments")
    args = parser.parse_args()

    if args.refresh:
        for path in source_files():
            text = path.read_text(encoding="utf-8")
            stripped = strip_generated_comments(text)
            if stripped != text:
                path.write_text(stripped, encoding="utf-8", newline="\n")
        args.write = True

    if args.write:
        total = 0
        for path in source_files():
            count = annotate_file(path)
            if count:
                print(f"annotated {count:3d}  {path.relative_to(ROOT)}")
            total += count
        print(f"inserted: {total}")

    hits = audit()
    missing = [hit for hit in hits if not hit.annotated]
    fields = audit_struct_fields()
    missing_fields = [field for field in fields if not field.annotated]
    print(f"functions/methods audited: {len(hits)}")
    print(f"with interface comments:  {len(hits) - len(missing)}")
    print(f"missing comments:         {len(missing)}")
    for hit in missing:
        print(f"{hit.path}:{hit.line}: {hit.name} ({hit.section})")
    print(f"struct field lines audited: {len(fields)}")
    print(f"missing field comments:    {len(missing_fields)}")
    for field in missing_fields:
        print(f"{field.path}:{field.line}: {field.owner}::{field.declaration}")
    return bool(missing or missing_fields)


if __name__ == "__main__":
    raise SystemExit(main())
