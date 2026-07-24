#!/usr/bin/env python3
"""Audit variable explanations in the large handbook without changing APIs."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from audit_large_interfaces import LISTING_RE, ROOT, section_before, source_files


TYPE = (
    r"(?:const\s+)?(?:unsigned\s+long\s+long|long\s+double|long\s+long|"
    r"unsigned\s+int|int|bool|double|float|char|string|size_t|auto|Real|"
    r"ll|ull|__int128|[A-Z]\w*|"
    r"(?:vector|array|pair|optional|deque|queue|stack|set|multiset|map|"
    r"unordered_map|unordered_set|priority_queue)\s*<[^;]+?>)"
)
DECL_RE = re.compile(
    rf"^(?P<indent>[ \t]*)(?:(?:static|constexpr|const|inline)\s+)*"
    rf"{TYPE}(?:\s+const)?\s+(?P<decl>[^;]+);"
)
DECL_ANY_RE = re.compile(
    rf"(?P<prefix>^|(?<=[;{{}}]))(?P<indent>[ \t]*)"
    rf"(?:(?:static|constexpr|const|inline)\s+)*{TYPE}"
    rf"(?:\s+const)?\s+(?P<decl>[^;]+);"
)
FOR_RE = re.compile(
    r"\bfor\s*\(\s*(?:const\s+)?(?:auto|int|long long|size_t|char)\s+"
    r"(?:\[([^\]]+)\]|([A-Za-z_]\w*))"
)
FUNCTION_START_RE = re.compile(
    r"^\s*(?:template\s*<.*>\s*)?(?:[\w:<>,&*\[\] ]+)\s+"
    r"(?:operator\s*[^\s(]+|[A-Za-z_]\w*)\s*\([^;]*\)"
    r"\s*(?:const\s*)?(?:noexcept\s*)?(?:->\s*[^{]+)?\s*\{"
)
PROTOTYPE_RE = re.compile(
    r"^\s*(?:bool|void|int|long long|double|Real|[A-Z]\w*)\s+"
    r"[A-Za-z_]\w*\s*\([^;]*(?:\bint\b|\blong\b|\bbool\b|\bchar\b|"
    r"\bconst\b|\b[A-Z]\w*\s+[*&]?[A-Za-z_]\w*)[^;]*\)\s*;"
)


@dataclass
class VariableLine:
    path: Path
    listing: int
    line: int
    names: list[str]
    source: str
    section: str
    annotated: bool


NAME_MEANING = {
    "N": "数组容量/预处理上界；实际合法下标以本节注释为准",
    "MAXN": "数组容量上界，必须大于题目最大规模",
    "INF": "不可达/无穷大哨兵值，参与加法前先判断不是 INF",
    "inf": "不可达/无穷大哨兵值，参与加法前先判断不是 inf",
    "MOD": "当前取模运算使用的正模数",
    "EPS": "浮点比较容差，绝对值不超过 EPS 视为 0",
    "n": "当前元素/顶点/状态数量 n",
    "m": "当前边数、操作数或第二维规模 m",
    "t": "测试用例数量或当前临时值 t",
    "T": "测试用例数量 T",
    "i": "当前循环下标 i",
    "j": "内层循环下标 j",
    "k": "当前排名、选取数量或循环层数 k",
    "l": "当前区间左端点 l",
    "r": "当前区间右端点 r",
    "L": "当前左边界/左半部分 L",
    "R": "当前右边界/右半部分 R",
    "ql": "目标查询/修改闭区间左端 ql",
    "qr": "目标查询/修改闭区间右端 qr",
    "mid": "当前区间中点 mid",
    "pos": "当前数组/字符串/DP 位置 pos",
    "idx": "当前数组或离散化下标 idx",
    "id": "当前对象的原始编号 id",
    "u": "当前顶点/状态编号 u",
    "v": "当前相邻顶点/下一状态 v",
    "w": "当前边权/转移代价 w",
    "fa": "当前节点的父节点 fa",
    "parent": "当前节点的父节点 parent",
    "root": "当前树/版本的根节点编号 root",
    "p": "当前质数、节点编号或指针 p；具体角色见所在公式",
    "x": "当前输入值/查询值/坐标 x",
    "y": "当前输入值/查询值/坐标 y",
    "z": "当前第三维坐标/临时值 z",
    "a": "当前输入数组/操作数 a",
    "b": "当前输入数组/操作数 b",
    "c": "当前字符、容量或第三个操作数 c",
    "s": "当前输入字符串/源点 s",
    "str": "当前输入字符串 str",
    "text": "待匹配主串 text",
    "pat": "待查找模式串 pat",
    "ans": "当前累计答案 ans",
    "answer": "当前累计/最终答案 answer",
    "res": "准备返回的结果容器/结果值 res",
    "result": "准备返回的结果 result",
    "cur": "当前扫描位置的累计状态 cur",
    "best": "目前找到的最优值 best",
    "sum": "当前累计和 sum",
    "cost": "当前累计费用/边权和 cost",
    "dist": "最短路/几何距离数组或当前距离 dist",
    "d": "当前距离、差值或覆盖增量 d",
    "len": "当前长度 len",
    "cnt": "计数数组/当前计数 cnt",
    "count": "当前计数 count",
    "tot": "当前已创建节点总数/累计数量 tot",
    "sz": "子树/集合大小 sz",
    "dep": "节点深度 dep",
    "vis": "访问或记忆化完成标记 vis",
    "used": "是否已使用/选择的标记集合 used",
    "ok": "当前条件是否仍成立 ok",
    "found": "是否已找到目标 found",
    "primes": "已经找到的质数表 primes，严格递增",
    "lp": "最小质因子数组 lp；lp[x] 是 x 的最小质因子",
    "phi": "欧拉函数数组 phi；phi[x] 是 1..x 中与 x 互质的数的个数",
    "mu": "莫比乌斯函数数组 mu；取值为 -1、0、1",
    "fac": "阶乘数组 fac",
    "ifac": "逆阶乘数组 ifac",
    "pre": "前缀和/前缀状态数组 pre",
    "dp": "动态规划状态数组 dp；下标含义见本节状态定义",
    "memo": "记忆化缓存 memo；哨兵值表示尚未计算",
    "g": "图/树的邻接表 g",
    "edges": "输入或生成的边集合 edges",
    "q": "当前队列或查询对象 q",
    "dq": "当前双端队列 dq",
    "stk": "当前栈 stk",
    "heap": "当前优先队列/堆 heap",
    "mp": "当前键值映射 mp",
    "st": "当前集合或自动机/DP 状态 st",
    "us": "当前无序集合 us",
    "path": "当前 DFS 路径/输出路径 path",
    "mask": "当前子集/博弈状态的二进制掩码 mask",
    "sub": "当前枚举的子掩码 sub",
    "bit": "当前处理的二进制位 bit",
    "base": "当前幂运算底数/基多项式 base",
    "pw": "幂次预处理数组 pw",
    "rank": "当前排列的 0-based Cantor 排名 rank",
    "avail": "尚未使用、按值有序的候选元素 avail",
    "old": "修改前版本根/修改前容器大小 old",
    "nw": "待插入的新直线/节点 nw",
    "line": "当前候选直线 line",
    "hull": "按有效顺序维护的凸包候选队列 hull",
    "flow": "当前已经发送的流量 flow",
    "need": "目标发送流量 need",
    "level": "Dinic 层次图中的顶点层数 level",
    "it": "Dinic 当前弧优化下标 it",
    "low": "Tarjan 最低可达时间戳 low",
    "dfn": "DFS 首次访问时间戳 dfn",
    "timer": "DFS/扫描使用的递增时间戳 timer",
    "topo": "拓扑序列 topo",
    "indeg": "每个顶点当前入度 indeg",
    "sg": "Sprague-Grundy 值数组 sg",
    "mex": "当前集合的最小未出现非负整数 mex",
    "events": "扫描线事件集合 events",
    "xs": "离散化后排序去重的坐标 xs",
    "ys": "离散化后排序去重的坐标 ys",
    "it": "当前容器迭代器/当前弧位置 it",
    "pq": "当前优先队列 pq；堆顶含义见比较器",
    "lb": "当前最低位 1 的权值/下界 lb",
    "secret": "交互题中仅供本地模拟的隐藏答案 secret",
    "queries": "输入询问集合 queries",
    "guess": "本轮向交互器提交的猜测值 guess",
    "fact": "阶乘表 fact；fact[i]=i!",
    "diff": "当前差值/差分数组 diff",
    "pivot": "当前高斯消元选择的主元行 pivot",
    "row": "当前高斯消元主元行 row",
    "col": "当前高斯消元列/扫描列 col",
    "inv": "当前逆元/是否执行逆变换 inv",
    "mod": "当前正模数 mod",
    "e": "当前指数、质因子次数或边对象 e",
    "x1": "递归子问题返回的 Bézout 系数 x1",
    "y1": "递归子问题返回的 Bézout 系数 y1",
    "C": "当前组合数查询函数/结果矩阵 C",
    "bits": "当前值的有效二进制位数 bits",
    "cycles": "当前置换的环数量 cycles",
    "deg": "顶点度数数组 deg",
    "leaves": "当前度数为 1 的叶子最小堆 leaves",
    "leaf": "当前取出的最小叶子 leaf",
    "factor": "当前乘数/质因子贡献 factor",
    "tag": "当前时间戳/懒标记 tag",
    "add": "当前增加量/仿射常数项 add",
    "lef": "新直线在区间左端是否更优 lef",
    "NEG": "空直线/不存在次大值使用的负无穷哨兵 NEG",
    "f": "当前流量上限/递归返回值 f",
    "sa": "后缀数组 sa；sa[i] 是第 i 小后缀起点",
    "ri": "后缀 i 的当前第一关键字排名 ri",
    "rj": "后缀 j 的当前第一关键字排名 rj",
    "clone": "后缀自动机为拆分转移而复制的克隆状态 clone",
    "ord": "按长度/拓扑顺序排列的状态编号 ord",
    "cc": "当前强连通分量数量 cc",
    "all_one": "所有堆是否都只有 1 个石子的标记 all_one",
    "values": "当前需要求 mex 的后继 SG 值集合 values",
    "take": "当前尝试取走的石子数量 take",
    "value": "当前元素/局面评估值 value",
    "strip": "当前阶梯 Nim 的奇数层石子异或和 strip",
    "range_sum": "返回指定区间和的局部 lambda range_sum",
    "active": "扫描到当前位置时仍然活跃的对象数 active",
    "peak": "扫描过程中出现过的最大活跃数 peak",
    "delta": "当前事件/修改带来的增量 delta",
    "groups": "当前贪心分出的连续组数 groups",
    "left": "当前窗口/区间左端点 left",
    "right": "当前窗口/区间右端点 right",
    "m1": "第一个模数/第一部分规模 m1",
    "m2": "第二个模数/第二部分规模 m2",
    "last": "上一个已选择位置/值 last",
    "job": "当前按贪心顺序处理的任务 job",
    "inq": "顶点当前是否在队列中的标记 inq",
    "pushed": "当前点进入队列的次数 pushed",
    "nextGreater": "每个位置右侧第一个更大元素下标 nextGreater",
    "quotient": "当前整除分块内恒定的商 quotient=n/l",
    "code": "Prüfer 序列 code",
    "step": "当前 NTT/FWT 合并跨度 step",
    "tt": "当前临时时间戳/变量 tt",
    "cyc": "当前置换环长度/环计数 cyc",
    "wlen": "当前 NTT 蝶形层使用的单位根 wlen",
    "bad": "当前状态是否无解/不合法的标记 bad",
    "overflow": "当前乘法或容量是否溢出的标记 overflow",
    "ways": "当前方案数/多项式 ways",
    "na": "多项式 a 补齐后的 NTT 长度 na",
    "nm": "合并后需要的最小结果长度 nm",
    "baby": "BSGS 中小步值到指数的哈希表 baby",
    "all_zero": "方程当前行系数是否全为 0 的标记 all_zero",
    "K": "当前固定状态数/选取数 K",
    "high": "当前查询范围高端/最高位 high",
    "left_count": "当前节点左子树中的元素数量 left_count",
    "bl": "当前块左端编号 bl",
    "br": "当前块右端编号 br",
    "block": "莫队/分块算法使用的块长 block",
    "bx": "查询 x 所在块编号 bx",
    "by": "查询 y 所在块编号 by",
    "remove": "把位置移出当前窗口的局部 lambda remove",
    "qu": "当前离线查询 qu",
    "da": "点/节点 a 的深度或差值 da",
    "db": "点/节点 b 的深度或差值 db",
    "ca": "圆/节点 a 的当前分类或余弦值 ca",
    "cb": "圆/节点 b 的当前分类或余弦值 cb",
    "mul": "当前仿射乘数/矩阵乘积 mul",
    "want": "当前查询希望找到的分支/值 want",
    "same": "当前两个对象是否相同/重合的标记 same",
    "tree": "当前线段树/树结构存储 tree",
    "pi": "KMP 前缀函数 pi",
    "BASE": "字符串哈希使用的固定底数 BASE",
    "mir": "Manacher 中与 i 关于中心对称的位置 mir",
    "nr": "本轮扩展得到的新右边界 nr",
    "rk": "每个后缀/元素的当前排名 rk",
    "tmp": "本轮排序/合并使用的临时数组 tmp",
    "ra": "对象 a 的当前排名/半径 ra",
    "rb": "对象 b 的当前排名/半径 rb",
    "dsu": "并查集父节点数组/对象 dsu",
    "INF64": "long long 不可达哨兵 INF64",
    "cap": "当前边的剩余容量 cap",
    "color": "顶点颜色/二分图染色数组 color",
    "matchR": "右部点当前匹配到的左部点 matchR",
    "matching": "当前二分图匹配边数 matching",
    "fg": "费用流残量网络邻接表 fg",
    "got": "本次增广实际发送的流量 got",
    "mg": "费用流残量网络 mg",
    "pot": "费用流顶点势能数组 pot",
    "pv": "最短增广路中顶点的前驱点 pv",
    "pe": "最短增广路中使用的前驱边下标 pe",
    "nd": "候选新距离 nd",
    "LOG": "倍增表层数 LOG，需满足 2^LOG 大于最大规模",
    "parent2": "长链/重链剖分中的父节点数组 parent2",
    "depth2": "长链/重链剖分中的深度数组 depth2",
    "heavy_len": "从每个点向下的最长链长度 heavy_len",
    "heavy2": "每个点的最长链儿子 heavy2",
    "top2": "每个点所属最长链链顶 top2",
    "dx": "当前节点/坐标相对偏移 dx",
    "ptr": "当前遍历邻接边/数组的位置指针 ptr",
    "euler": "欧拉路径最终顶点序列 euler",
    "ds": "当前收集到的距离列表 ds",
    "tail": "LIS 各长度对应的最小结尾值数组 tail",
    "lis": "当前最长递增子序列长度 lis",
    "bestEnding": "必须以当前位置结尾的最大子段和 bestEnding",
    "maxSubarray": "扫描至今的最大子段和 maxSubarray",
    "lcs": "最长公共子序列 DP 数组/答案 lcs",
    "lim": "当前允许的阈值/上界 lim",
    "E": "当前状态的期望值数组 E",
    "prev": "上一层/上一个状态的 DP 数组 prev",
    "up": "父侧贡献/倍增祖先数组 up",
    "ns": "转移后的 started 状态 ns",
    "nst": "转移后的自动机/DP 状态 nst",
    "best_j": "当前 DP 状态取得最优值的决策下标 best_j",
    "cand": "当前枚举得到的候选答案 cand",
    "other": "当前移动后的另一堆/另一状态 other",
    "I": "单位矩阵/恒等转移 I",
    "ones": "石子数恰为 1 的堆数量 ones",
    "nxt": "当前一步可到达的后继状态 nxt",
    "total": "当前总数/连通块规模 total",
    "win": "状态是否必胜的记忆化数组 win",
    "dag": "DAG 状态转移邻接表 dag",
    "all": "所有候选/事件的汇总容器 all",
    "target": "当前希望达到的异或值/目标状态 target",
    "table": "状态到记忆化答案的哈希表 table",
    "c1": "第一个方向/圆交辅助量 c1",
    "c2": "第二个方向/圆交辅助量 c2",
    "c3": "第三个方向/圆交辅助量 c3",
    "c4": "第四个方向/圆交辅助量 c4",
    "dd": "两点距离平方/判别式 dd",
    "foot": "点在直线上的垂足 foot",
    "unit": "单位方向向量 unit",
    "perp": "与当前方向垂直的单位向量 perp",
    "off": "从中点到交点的垂直偏移 off",
    "lower": "凸包下链/下方候选 lower",
    "ni": "旋转卡壳中 i 的下一个循环下标 ni",
    "area": "当前累计面积 area",
    "last_x": "扫描线上一个事件横坐标 last_x",
    "last_y": "扫描线上一个事件纵坐标 last_y",
    "out": "准备返回的多边形/交点集合 out",
    "cp": "当前点 p 相对圆心/基点的向量 cp",
    "cq": "当前点 q 相对圆心/基点的向量 cq",
    "poly": "当前凸多边形顶点序列 poly",
    "midx": "当前区间中央横坐标 midx",
    "per": "当前周长/周期 per",
    "A": "当前面积、矩阵或左操作数 A",
    "D": "当前判别式/距离量 D",
    "t1": "第一个参数方程解 t1",
    "t2": "第二个参数方程解/临时元组 t2",
    "seg": "扫描线维护的线段树 seg",
    "det": "高斯消元过程中累计的行列式 det",
    "ni": "变换长度 n 在模 MOD 下的逆元 ni",
    "center": "Manacher 当前最右回文的中心 center",
    "pos": "所有匹配起点的返回数组 pos",
    "right": "当前窗口右端/Manacher 已知最右边界 right",
    "rank": "后缀/排列的当前排名数组或 Cantor 排名 rank",
    "lcp": "相邻后缀最长公共前缀数组 lcp",
    "in": "顶点当前是否在 Tarjan 栈内的标记 in",
    "comp": "每个顶点所属强连通分量编号 comp",
    "cc": "当前已经找到的强连通分量数量 cc",
    "bridges": "已经找到的桥边端点集合 bridges",
    "tin": "DFS 进入每个节点的时间戳 tin",
    "tout": "DFS 离开每个节点的时间戳 tout",
    "dis": "两圆圆心距离/当前实际距离 dis",
}


def split_top_level(raw: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    start = 0
    for index, char in enumerate(raw):
        if char in "<([{":
            depth += 1
        elif char in ">)]}":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            parts.append(raw[start:index].strip())
            start = index + 1
    parts.append(raw[start:].strip())
    return parts


def declared_names(line: str) -> list[str]:
    names: list[str] = []
    loop = FOR_RE.search(line)
    if loop:
        raw = loop.group(1) or loop.group(2)
        names.extend(item.strip() for item in raw.split(","))

    function_start = FUNCTION_START_RE.match(line)
    first_word = re.match(r"^\s*([A-Za-z_]\w*)", line)
    is_control = first_word and first_word.group(1) in {"if", "for", "while", "switch", "catch"}
    if PROTOTYPE_RE.match(line):
        return names
    declaration_source = line
    if function_start and not is_control:
        declaration_source = line[line.find("{"):]
    for declaration in DECL_ANY_RE.finditer(declaration_source):
        for item in split_top_level(declaration.group("decl")):
            match = re.match(r"\s*(?:[*&]\s*)?([A-Za-z_]\w*)", item)
            if match and match.group(1) not in names:
                names.append(match.group(1))
    return names


def meaning(name: str, line: str, section: str) -> str:
    if name in {"i", "j", "k", "bit"} and any(token in line for token in ("<<", ">>", "LOG")):
        return f"当前处理的二进制位/倍增层 {name}"
    if name == "p" and "primes" in line:
        return "当前从质数表枚举出的质数 p"
    if name == "p" and ("p * p <= n" in line or "n % p" in line):
        return "当前试除的候选质因子 p"
    if name == "p" and any(word in section for word in ("线段树", "扫描线", "李超")):
        return "当前线段树节点编号 p"
    if name == "g" and "exgcd" in line:
        return "递归返回的 gcd(a,b) 值 g"
    if name == "e" and re.search(r"\bint\s+e\s*=", line):
        return "当前质因子 p 在原数中的指数 e"
    if name == "e" and ("Edge" in line or "g[u]" in line or "fg[u]" in line or "mg[u]" in line):
        return "当前遍历的边对象 e"
    if name == "fg":
        return "Dinic 残量网络邻接表 fg"
    if name == "mg":
        return "最小费用流残量网络邻接表 mg"
    if name in {"a", "b"} and "Edge a{" in line:
        return "正向残量边 a" if name == "a" else "配套的反向残量边 b"
    if name in {"a", "b", "c"} and any(word in section for word in ("几何", "向量", "圆", "线段", "凸包")):
        return f"当前几何点/向量/圆 {name}"
    if name == "s" and not re.search(r"\bstring\s+s\b", line):
        return "当前枚举的起点/源点 s"
    if name == "q":
        if "queue" in line or "deque" in line:
            return "当前 BFS/单调算法使用的队列 q"
        return "当前查询对象 q"
    if name == "r" and "1 % mod" in line:
        return "快速幂当前累计答案 r"
    if name == "r" and "long long sum(int x)" in line:
        return "树状数组前缀查询当前累计和 r"
    if name == "f" and "__int128 x" in line:
        return "读入 __int128 时记录正负号的符号 f"
    if name == "c" and "getchar" in line:
        return "当前从输入读取的字符 c"
    if name == "q" and "q = p - 1" in line:
        return "把 p-1 写成 q*2^s 后的奇数部分 q"
    if name == "s" and "q = p - 1" in line:
        return "p-1 中因子 2 的指数 s"
    if name == "tt" and "t * t % p" in line:
        return "当前平方根修正量 t 的平方 tt"
    if name == "t" and "pat + '#' + text" in line:
        return "拼接串 pat+'#'+text，用于一次前缀函数匹配"
    if name == "pi" and "prefix_function" in line:
        return "拼接串 t 的 KMP 前缀函数数组 pi"
    if name == "p" and "vector<int> p(t.size())" in line:
        return "Manacher 半径数组 p"
    if name == "z" and "vector<int> z" in line:
        return "Z 函数数组 z；z[i] 是 s 与 s[i..] 的最长公共前缀"
    if name == "d" and "b.o - a.o" in line:
        return "从圆 a 圆心指向圆 b 圆心的向量 d"
    if name == "d" and "Point d = a - b" in line:
        return "从点 b 指向点 a 的差向量 d"
    if name == "dd" and "dot(d, d)" in line:
        return "两圆圆心距离的平方 dd"
    if name == "i" and "long long tt = t * t" in line:
        return "寻找满足 t^(2^i)=1 时的最小指数 i"
    if name == "b" and "mod_pow(c" in line:
        return "Tonelli-Shanks 本轮把 x 调整到下一阶所乘的修正因子 b"
    if name == "c1" and "cross(b - a, c - a)" in line:
        return "点 c 相对有向线段 a->b 的方向叉积 c1"
    if name == "c2" and "cross(b - a, d - a)" in line:
        return "点 d 相对有向线段 a->b 的方向叉积 c2"
    if name == "c3" and "cross(d - c, a - c)" in line:
        return "点 a 相对有向线段 c->d 的方向叉积 c3"
    if name == "c4" and "cross(d - c, b - c)" in line:
        return "点 b 相对有向线段 c->d 的方向叉积 c4"
    if name == "x" and "i * p" in line:
        return "本次由 i*p 得到并筛掉的合数 x"
    if name in {"v", "to"} and any(token in line for token in ("g[u]", "edge", "Edge")):
        return f"当前边的终点 {name}"
    if name == "w" and any(token in line for token in ("g[u]", "edge", "Edge")):
        return "当前边权 w"
    if name in {"l", "r"} and "for (auto [" in line:
        side = "左" if name == "l" else "右"
        return f"当前事件/询问区间{side}端点 {name}"
    if name == "delta":
        return "当前事件带来的计数增量 delta"
    if name == "active":
        return "扫描到当前位置时仍活跃的区间数 active"
    if name == "peak":
        return "扫描过程中出现过的最大活跃数量 peak"
    if name == "distinct":
        return "当前窗口内不同值的数量 distinct"
    if name == "left":
        return "滑动窗口左端点 left"
    if name == "right":
        return "滑动窗口右端点 right"
    if name == "quotient":
        return "当前整除分块内恒定的商 quotient=n/l"
    if name == "rem":
        return "当前模数余数/数位 DP 余数状态 rem"
    if name == "tight":
        return "当前数位前缀是否仍贴住上界 tight"
    if name == "started":
        return "是否已经出现非前导零数字 started"
    if name == "section":
        return "当前所属专题 section"
    return NAME_MEANING.get(
        name,
        f"“{section}”这段代码中的临时量 {name}；值由本行初始化式确定",
    )


def is_annotated(lines: list[str], index: int, names: list[str]) -> bool:
    line = lines[index]
    if "//" in line:
        return True
    if index:
        previous = lines[index - 1].strip()
        if previous.startswith("// 变量："):
            return all(re.search(rf"\b{re.escape(name)}\b", previous) for name in names)
    return False


def comment_for(names: list[str], line: str, section: str, indent: str) -> str:
    items = [f"{name}={meaning(name, line, section)}" for name in names]
    return indent + "// 变量：" + "；".join(items) + "。\n"


def scan() -> list[VariableLine]:
    hits: list[VariableLine] = []
    for path in source_files():
        text = path.read_text(encoding="utf-8")
        for listing_no, listing in enumerate(LISTING_RE.finditer(text), 1):
            body = listing.group("body")
            section = section_before(text, listing.start())
            lines = body.splitlines()
            base_line = text[:listing.start("body")].count("\n") + 1
            for index, line in enumerate(lines):
                names = declared_names(line)
                if not names:
                    continue
                hits.append(
                    VariableLine(
                        path=path.relative_to(ROOT),
                        listing=listing_no,
                        line=base_line + index,
                        names=names,
                        source=line.strip(),
                        section=section,
                        annotated=is_annotated(lines, index, names),
                    )
                )
    return hits


def annotate_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    pieces: list[str] = []
    cursor = 0
    inserted = 0
    for listing in LISTING_RE.finditer(text):
        pieces.append(text[cursor:listing.start()])
        body = listing.group("body")
        section = section_before(text, listing.start())
        lines = body.splitlines(keepends=True)
        for index in range(len(lines) - 1, -1, -1):
            names = declared_names(lines[index])
            if not names or is_annotated([item.rstrip("\r\n") for item in lines], index, names):
                continue
            indent = re.match(r"^[ \t]*", lines[index]).group(0)
            lines.insert(index, comment_for(names, lines[index], section, indent))
            inserted += 1
        pieces.extend((listing.group("open"), "".join(lines), listing.group("close")))
        cursor = listing.end()
    pieces.append(text[cursor:])
    if inserted:
        path.write_text("".join(pieces), encoding="utf-8", newline="\n")
    return inserted


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if args.refresh:
        for path in source_files():
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines(keepends=True)
            stripped = "".join(line for line in lines if not re.match(r"^[ \t]*// 变量：", line))
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
        print(f"inserted variable comments: {total}")
    hits = scan()
    missing = [hit for hit in hits if not hit.annotated]
    variable_count = sum(len(hit.names) for hit in hits)
    missing_variable_count = sum(len(hit.names) for hit in missing)
    print(f"variable declaration lines audited: {len(hits)}")
    print(f"individual variables audited:       {variable_count}")
    print(f"with explanations:                {len(hits) - len(missing)}")
    print(
        f"missing explanations:             {len(missing)} lines / "
        f"{missing_variable_count} variables"
    )
    for hit in missing:
        print(f"{hit.path}:{hit.line}: {', '.join(hit.names)} :: {hit.source}")
    return bool(missing)


if __name__ == "__main__":
    raise SystemExit(main())
