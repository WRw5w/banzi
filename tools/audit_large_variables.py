#!/usr/bin/env python3
"""Audit variable explanations in the large handbook without changing APIs."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from audit_large_interfaces import (
    AMBIGUOUS_COMMENT_PHRASES,
    LISTING_RE,
    ROOT,
    ambiguous_comment,
    duplicate_dict_key_issues,
    section_before,
    source_files,
)


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
    "N": "当前代码允许使用的最大下标上界 N",
    "MAXN": "数组容量上界，必须大于题目最大规模",
    "INF": "表示不可达结果的正无穷哨兵 INF",
    "inf": "表示不可达结果的正无穷哨兵 inf",
    "MOD": "当前取模运算使用的正模数",
    "EPS": "浮点比较容差，绝对值不超过 EPS 视为 0",
    "n": "当前算法处理的对象数量 n",
    "m": "当前算法处理的第二个数量 m",
    "t": "当前步骤使用的数值 t",
    "T": "测试用例数量 T",
    "i": "机械索引 i",
    "j": "内层循环下标 j",
    "k": "当前循环或公式的整数下标 k",
    "l": "当前区间左端点 l",
    "r": "当前区间右端点 r",
    "L": "当前处理范围的左边界 L",
    "R": "当前处理范围的右边界 R",
    "ql": "目标闭区间左端 ql",
    "qr": "目标闭区间右端 qr",
    "mid": "当前区间中点 mid",
    "pos": "当前处理位置 pos",
    "idx": "当前访问容器的 0-based 下标 idx",
    "id": "当前对象的原始编号 id",
    "u": "当前处理对象的编号 u",
    "v": "与 u 配对处理的对象编号 v",
    "w": "当前候选的数值 w",
    "fa": "当前节点的父节点 fa",
    "parent": "当前节点的父节点 parent",
    "root": "当前树结构的根节点编号 root",
    "p": "当前步骤处理的对象 p",
    "x": "当前步骤处理的数值 x",
    "y": "与 x 配对处理的数值 y",
    "z": "当前步骤处理的第三个数值 z",
    "a": "当前步骤读取的第一个对象 a",
    "b": "当前步骤读取的第二个对象 b",
    "c": "当前步骤读取的第三个对象 c",
    "s": "当前输入序列 s",
    "str": "当前输入字符串 str",
    "text": "待匹配主串 text",
    "pat": "待查找模式串 pat",
    "ans": "当前累计答案 ans",
    "answer": "当前维护的答案 answer",
    "res": "准备由函数返回的结果 res",
    "result": "准备返回的结果 result",
    "cur": "当前扫描位置的累计状态 cur",
    "best": "目前找到的最优值 best",
    "sum": "当前累计和 sum",
    "cost": "当前累计费用 cost",
    "dist": "当前维护的距离 dist",
    "d": "当前步骤使用的增量 d",
    "len": "当前长度 len",
    "cnt": "当前计数 cnt",
    "count": "当前计数 count",
    "tot": "当前已经创建的数据结构节点数量 tot",
    "sz": "当前对象包含的元素数量 sz",
    "dep": "节点深度 dep",
    "vis": "访问或记忆化完成标记 vis",
    "used": "记录每个对象是否已被使用的标记 used",
    "ok": "当前条件是否仍成立 ok",
    "found": "是否已找到目标 found",
    "primes": "已经找到的质数表 primes，严格递增",
    "lp": "最小质因子数组 lp；lp[x] 是 x 的最小质因子",
    "phi": "欧拉函数数组 phi；phi[x] 是 1..x 中与 x 互质的数的个数",
    "mu": "莫比乌斯函数数组 mu；取值为 -1、0、1",
    "fac": "阶乘数组 fac",
    "ifac": "逆阶乘数组 ifac",
    "pre": "当前算法维护的前缀数组 pre",
    "dp": "动态规划状态数组 dp；下标含义见本节状态定义",
    "memo": "记忆化缓存 memo；哨兵值表示尚未计算",
    "g": "当前有向图的邻接表 g",
    "edges": "输入或生成的边集合 edges",
    "q": "当前算法使用的队列 q",
    "dq": "当前双端队列 dq",
    "stk": "当前栈 stk",
    "heap": "当前算法使用的优先队列 heap",
    "mp": "当前键值映射 mp",
    "st": "当前搜索或自动机状态 st",
    "us": "当前无序集合 us",
    "path": "当前 DFS 维护的路径 path",
    "mask": "用二进制位编码的当前状态 mask",
    "sub": "当前枚举的子掩码 sub",
    "bit": "当前处理的二进制位 bit",
    "base": "当前幂运算使用的底数 base",
    "pw": "幂次预处理数组 pw",
    "rank": "当前排列的 0-based Cantor 排名 rank",
    "avail": "尚未使用、按值有序的候选元素 avail",
    "old": "当前修改前保存的旧值 old",
    "nw": "本次操作创建的新对象 nw",
    "line": "当前候选直线 line",
    "hull": "按有效顺序维护的凸包候选队列 hull",
    "flow": "当前已经发送的流量 flow",
    "need": "目标发送流量 need",
    "level": "Dinic 层次图中的顶点层数 level",
    "it": "Dinic 当前弧优化下标 it",
    "low": "Tarjan 最低可达时间戳 low",
    "dfn": "DFS 首次访问时间戳 dfn",
    "timer": "DFS 使用的递增时间戳 timer",
    "topo": "拓扑序列 topo",
    "indeg": "每个顶点当前入度 indeg",
    "sg": "Sprague-Grundy 值数组 sg",
    "mex": "当前集合的最小未出现非负整数 mex",
    "events": "扫描线事件集合 events",
    "xs": "离散化后排序去重的坐标 xs",
    "ys": "离散化后排序去重的坐标 ys",
    "pq": "当前优先队列 pq；堆顶含义见比较器",
    "lb": "当前值最低位 1 的权值 lb",
    "secret": "交互题中仅供本地模拟的隐藏答案 secret",
    "queries": "输入询问集合 queries",
    "guess": "本轮向交互器提交的猜测值 guess",
    "fact": "阶乘表 fact；fact[i]=i!",
    "diff": "当前算法维护的差分数组 diff",
    "pivot": "当前高斯消元选择的主元行 pivot",
    "row": "当前高斯消元主元行 row",
    "col": "当前高斯消元处理的列 col",
    "inv": "当前运算使用的逆元 inv",
    "mod": "当前正模数 mod",
    "e": "当前步骤处理的对象 e",
    "x1": "递归子问题返回的 Bézout 系数 x1",
    "y1": "递归子问题返回的 Bézout 系数 y1",
    "C": "当前步骤构造的矩阵 C",
    "bits": "当前值的有效二进制位数 bits",
    "cycles": "当前置换的环数量 cycles",
    "deg": "顶点度数数组 deg",
    "leaves": "当前度数为 1 的叶子最小堆 leaves",
    "leaf": "当前取出的最小叶子 leaf",
    "factor": "当前步骤使用的乘数 factor",
    "tag": "当前节点保存的懒标记 tag",
    "add": "当前操作要叠加的常数增量 add",
    "lef": "新直线在区间左端是否更优 lef",
    "NEG": "表示不存在候选值的负无穷哨兵 NEG",
    "f": "当前递归调用处理的数值 f",
    "sa": "后缀数组 sa；sa[i] 是第 i 小后缀起点",
    "ri": "后缀 i 的当前第一关键字排名 ri",
    "rj": "后缀 j 的当前第一关键字排名 rj",
    "clone": "后缀自动机为拆分转移而复制的克隆状态 clone",
    "ord": "按长度递增排列的自动机状态编号 ord",
    "all_one": "所有堆是否都只有 1 个石子的标记 all_one",
    "values": "当前需要求 mex 的后继 SG 值集合 values",
    "take": "当前尝试取走的石子数量 take",
    "value": "当前处理对象的数值 value",
    "strip": "当前阶梯 Nim 的奇数层石子异或和 strip",
    "range_sum": "返回指定区间和的局部 lambda range_sum",
    "active": "扫描到当前位置时仍然活跃的对象数 active",
    "peak": "扫描过程中出现过的最大活跃数 peak",
    "delta": "当前操作带来的增量 delta",
    "groups": "当前贪心分出的连续组数 groups",
    "left": "当前处理范围的左端点 left",
    "right": "当前处理范围的右端点 right",
    "m1": "当前算法的第一个分界值 m1",
    "m2": "当前算法的第二个分界值 m2",
    "last": "上一个已选择对象对应的值 last",
    "job": "当前按贪心顺序处理的任务 job",
    "inq": "顶点当前是否在队列中的标记 inq",
    "pushed": "当前点进入队列的次数 pushed",
    "nextGreater": "每个位置右侧第一个更大元素下标 nextGreater",
    "quotient": "当前整除分块内恒定的商 quotient=n/l",
    "code": "Prüfer 序列 code",
    "step": "当前 NTT/FWT 合并跨度 step",
    "tt": "当前步骤保存的中间值 tt",
    "cyc": "当前置换的环长度 cyc",
    "wlen": "当前 NTT 蝶形层使用的单位根 wlen",
    "bad": "记录当前状态是否不合法的标记 bad",
    "overflow": "当前乘法或容量是否溢出的标记 overflow",
    "ways": "当前累计的方案数 ways",
    "na": "多项式 a 补齐后的 NTT 长度 na",
    "nm": "合并后需要的最小结果长度 nm",
    "baby": "BSGS 中小步值到指数的哈希表 baby",
    "all_zero": "方程当前行系数是否全为 0 的标记 all_zero",
    "K": "当前算法使用的固定数量 K",
    "high": "当前查询范围的右端 high",
    "left_count": "当前节点左子树中的元素数量 left_count",
    "bl": "当前块左端编号 bl",
    "br": "当前块右端编号 br",
    "block": "当前分块算法使用的块长 block",
    "bx": "查询 x 所在块编号 bx",
    "by": "查询 y 所在块编号 by",
    "remove": "把位置移出当前窗口的局部 lambda remove",
    "qu": "当前离线查询 qu",
    "da": "当前算法为对象 a 计算的数值 da",
    "db": "当前算法为对象 b 计算的数值 db",
    "ca": "当前算法为对象 a 计算的分类值 ca",
    "cb": "当前算法为对象 b 计算的分类值 cb",
    "mul": "当前步骤计算的乘积 mul",
    "want": "当前查询希望找到的值 want",
    "same": "记录当前两个对象是否相同的标记 same",
    "tree": "当前算法维护的树结构存储 tree",
    "pi": "KMP 前缀函数 pi",
    "BASE": "字符串哈希使用的固定底数 BASE",
    "mir": "Manacher 中与 i 关于中心对称的位置 mir",
    "nr": "本轮扩展得到的新右边界 nr",
    "rk": "每个后缀的当前字典序排名 rk",
    "tmp": "本轮排序/合并使用的临时数组 tmp",
    "ra": "当前算法为对象 a 计算的值 ra",
    "rb": "当前算法为对象 b 计算的值 rb",
    "dsu": "当前算法使用的并查集 dsu",
    "INF64": "long long 不可达哨兵 INF64",
    "cap": "当前边的剩余容量 cap",
    "color": "二分图中每个顶点的染色 color",
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
    "dx": "当前步骤使用的横坐标偏移 dx",
    "ptr": "当前遍历位置 ptr",
    "euler": "欧拉路径最终顶点序列 euler",
    "ds": "当前收集到的距离列表 ds",
    "tail": "LIS 各长度对应的最小结尾值数组 tail",
    "lis": "当前最长递增子序列长度 lis",
    "bestEnding": "必须以当前位置结尾的最大子段和 bestEnding",
    "maxSubarray": "扫描至今的最大子段和 maxSubarray",
    "lcs": "当前最长公共子序列长度 lcs",
    "lim": "当前允许的阈值 lim",
    "E": "当前状态的期望值数组 E",
    "prev": "上一层 DP 的状态数组 prev",
    "up": "当前节点来自父侧的 DP 贡献 up",
    "ns": "转移后的 started 状态 ns",
    "nst": "转移后的自动机/DP 状态 nst",
    "best_j": "当前 DP 状态取得最优值的决策下标 best_j",
    "cand": "当前枚举得到的候选答案 cand",
    "other": "当前移动后的另一堆/另一状态 other",
    "I": "当前状态空间的单位矩阵 I",
    "ones": "石子数恰为 1 的堆数量 ones",
    "nxt": "当前一步可到达的后继状态 nxt",
    "total": "当前累计的对象总数 total",
    "win": "状态是否必胜的记忆化数组 win",
    "dag": "DAG 状态转移邻接表 dag",
    "all": "汇总全部候选对象的容器 all",
    "target": "当前希望达到的目标值 target",
    "table": "状态到记忆化答案的哈希表 table",
    "c1": "当前几何判断的第一个叉积 c1",
    "c2": "当前几何判断的第二个叉积 c2",
    "c3": "当前几何判断的第三个叉积 c3",
    "c4": "当前几何判断的第四个叉积 c4",
    "dd": "当前两点距离的平方 dd",
    "foot": "点在直线上的垂足 foot",
    "unit": "单位方向向量 unit",
    "perp": "与当前方向垂直的单位向量 perp",
    "off": "从中点到交点的垂直偏移 off",
    "lower": "凸包的下链顶点序列 lower",
    "ni": "旋转卡壳中 i 的下一个循环下标 ni",
    "area": "当前累计面积 area",
    "last_x": "扫描线上一个事件横坐标 last_x",
    "last_y": "扫描线上一个事件纵坐标 last_y",
    "out": "准备由函数返回的点集 out",
    "cp": "当前点 p 相对基点的向量 cp",
    "cq": "当前点 q 相对基点的向量 cq",
    "poly": "当前凸多边形顶点序列 poly",
    "midx": "当前区间中央横坐标 midx",
    "per": "当前计算得到的周期 per",
    "A": "当前步骤使用的第一个对象 A",
    "D": "当前步骤计算的判别式 D",
    "t1": "第一个参数方程解 t1",
    "t2": "当前步骤计算的第二个参数 t2",
    "seg": "扫描线维护的线段树 seg",
    "det": "高斯消元过程中累计的行列式 det",
    "center": "Manacher 当前最右回文的中心 center",
    "lcp": "相邻后缀最长公共前缀数组 lcp",
    "in": "顶点当前是否在 Tarjan 栈内的标记 in",
    "comp": "每个顶点所属强连通分量编号 comp",
    "cc": "当前已经找到的强连通分量数量 cc",
    "bridges": "已经找到的桥边端点集合 bridges",
    "tin": "DFS 进入每个节点的时间戳 tin",
    "tout": "DFS 离开每个节点的时间戳 tout",
    "dis": "两圆圆心之间的距离 dis",
}

# These names are too overloaded to receive a context-free fallback. A new or
# deleted comment for one of them must match a declaration/section rule below;
# otherwise generation fails and asks for a human-provided meaning. Keeping
# this guard separate from NAME_MEANING prevents one algorithm's role from
# silently leaking into another while retaining the table as shared wording.
CONTEXT_SENSITIVE_FALLBACK_NAMES = {
    name for name in NAME_MEANING if len(name) <= 3
}
CONTEXT_SENSITIVE_FALLBACK_NAMES.update(
    {
        "answer", "result", "value", "line", "root", "parent", "path",
        "mask", "base", "rank", "flow", "need", "level", "factor",
        "target", "table", "left", "right", "delta", "active", "peak",
    }
)


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


def meaning(name: str, line: str, section: str, context: str = "") -> str:
    if name == "old" and "old = (int)res.size()" in line and "Meet-in-the-middle" in section:
        return "加入当前元素 a[i] 生成新子集和之前 res 中已有的元素数量 old"

    if name in {"sa", "rk", "tmp"} and all(token in line for token in ("sa(n)", "rk(n)", "tmp(n)")):
        return {
            "sa": "后缀数组 sa；sa[i] 是字典序第 i 小后缀的 0-based 起点",
            "rk": "rk[i] 表示后缀 s[i..] 按当前倍增长度得到的等价类排名",
            "tmp": "本轮按长度 2k 的排名二元组排序后写入的新等价类排名数组 tmp",
        }[name]
    if name == "k" and re.search(r"for\s*\(int\s+k\s*=\s*1\s*;;\s*k\s*<<=\s*1", line):
        return "后缀数组倍增中排名二元组每一段的长度 k，本轮比较长度 2k 的前缀"
    if name == "diff" and "rk[a] != rk[b]" in line:
        return "相邻后缀 a、b 的第一段长度 k 排名是否不同的标记 diff"
    if name in {"ra", "rb"} and "rk[" in line and "k < n" in line:
        suffix = "a" if name == "ra" else "b"
        return f"后缀 {suffix} 偏移 k 后第二段的排名 {name}，越界时为 -1"
    if name in {"ri", "rj"} and re.search(r"\b(?:rk|r)\s*\[", line) and "k < n" in line:
        suffix = "i" if name == "ri" else "j"
        return f"后缀 {suffix} 偏移 k 后第二段的等价类排名 {name}，越界时为 -1"

    if name == "up" and "tight ? digit[pos] : 9" in line:
        return "数位 pos 可枚举数字的上界 up；tight 为真时取 digit[pos]，否则为 9"
    if name == "nst" and "ns ? go[st][d] : 0" in line:
        return "在自动机状态 st 后放置数字 d 得到的下一状态 nst；仍为前导零时保持起点 0"

    if name == "all" and "unsigned long long all = 0" in line and "nim_move" in context:
        return "标准 Nim 当前局面全部石子堆大小的异或和 all"

    if name == "f" and "int f = t[x].fa" in line and "struct LCT" in context:
        return "LCT 节点 x 当前辅助 splay 树父节点编号 f"
    if name == "f" and "query(root, 1, n, x)" in line and "find_root" in context:
        return "从持久化并查集版本 root 读出的元素 x 当前父节点编号 f"

    if name == "it" and re.search(r"\b(?:lower|upper)_bound\s*\(", line):
        bound = "下界" if "lower_bound" in line else "上界"
        container = re.search(r"(?:lower|upper)_bound\s*\(\s*([A-Za-z_]\w*)\.begin", line)
        if container:
            return f"容器 {container.group(1)} 中二分查找得到的{bound}迭代器 it"
        return f"当前二分查找得到的{bound}迭代器 it"

    if name in {"L", "R"} and "Meet-in-the-middle" in section:
        normalized = re.sub(r"\s+", "", line)
        if re.search(r"autoL=gen\(a,0,[^,]+(?:,[^\)]*)?\),R=gen\(a,[^\)]*\)", normalized):
            side = "左半部分" if name == "L" else "右半部分"
            return f"折半搜索枚举得到的{side}全部子集和列表 {name}"

    escaped_lt = r"(?:<|&lt;)"
    closure_context = "传递闭包" in section or (
        any(token in context for token in ("transitive_closure", "bitset_closure"))
        and "reach[i][k]" in context
    )
    if name == "k" and closure_context and re.search(
        rf"for\s*\(\s*int\s+k\s*=\s*0\s*;\s*k\s*{escaped_lt}\s*n", line
    ):
        return "bitset 传递闭包当前允许作为路径中转点的顶点编号 k"
    if name == "i" and closure_context and re.search(
        rf"for\s*\(\s*int\s+i\s*=\s*0\s*;\s*i\s*{escaped_lt}\s*n", line
    ):
        return "bitset 传递闭包当前检查可达性的起点编号 i"

    range_loop = re.search(r"\bfor\s*\([^:]+\b([A-Za-z_]\w*)\s*:\s*([^\)]+)\)", line)
    if range_loop and name == range_loop.group(1):
        source = range_loop.group(2).strip()
        if name == "c" and source in {"s", "str", "text"}:
            return f"从字符串 {source} 依次读取的字符 c"
        if re.search(r"(?:^|\b)(?:g|tree|child)\s*\[", source):
            return f"从 {source} 枚举的相邻顶点 {name}"
        if re.search(r"(?:^|\b)(?:dag|next)\s*\[", source):
            return f"从 {source} 枚举的后继状态 {name}"
        if source == "piles":
            return f"从 piles 枚举的单堆石子数 {name}"
        if source == "values":
            return f"参与 mex 计算的候选非负整数 {name}"
        if source == "moves[x]":
            return f"状态 x 可到达的后继状态 {name}"
        if source == "moves":
            return f"当前枚举的合法取石数量 {name}"
        if source == "code":
            return f"Prüfer 序列当前编码值 {name}"
        if source == "primes":
            return f"质数表中当前枚举的质数 {name}"
        if source in {"path", "path2", "a", "s.board"}:
            return f"从 {source} 枚举的元素值 {name}"
        if source == "ord":
            return f"按指定顺序枚举的自动机状态编号 {name}"
        return f"从容器 {source} 枚举的元素 {name}"

    structured = re.search(r"for\s*\(\s*auto\s*\[([^\]]+)\]\s*:\s*([^\)]+)\)", line)
    if structured:
        names = [item.strip() for item in structured.group(1).split(",")]
        source = structured.group(2).strip()
        if name in names:
            index = names.index(name)
            if "transitions" in source:
                return ("转移到的后继状态编号 v" if index == 0
                        else "采用该转移的概率 p")
            if source == "updates":
                roles = ("差分更新区间左端点 l", "差分更新区间右端点 r", "区间增加量 v")
                return roles[index]
            if source in {"event", "events"}:
                roles = ("扫描线事件坐标 x", "该事件带来的活跃计数增量 delta")
                return roles[index]
            if any(token in source for token in ("g[", "tree[", "weighted_tree[", "zero_one_graph[")):
                roles = (f"从 {source} 枚举的相邻顶点 v", "连接该顶点的边权 w")
                return roles[min(index, 1)]

    if name == "m" and re.search(r"(?:l\s*\+\s*\(r\s*-\s*l\)|l\s*\+\s*r).*[/>]", line):
        return "当前递归区间 [l,r] 的中点 m"
    if name == "m" and "sqrtl(mod) + 1" in line:
        return "BSGS 大步与小步采用的步长 m=ceil(sqrt(mod))"
    if name == "m" and "cyc.size()" in line:
        return "当前置换环的长度 m"
    if name == "j" and "int n = p.size(), j = 1" in line:
        return "旋转卡壳中沿凸包单调前进的对踵点下标 j"
    if name == "ans" and "int n = p.size(), j = 1" in line:
        return "旋转卡壳当前找到的最大点对距离平方 ans"
    if name == "ni" and "(i + 1) % n" in line:
        return "凸包顶点 i 的下一个循环下标 ni"
    if name == "s" and re.search(r"\bstring\s+s\s*\(len", line):
        return "正在逐字符构造并由 randstr 返回的随机小写字符串 s"
    if name == "strip" and "vector<Point> strip" in line:
        return "最近点对分治中靠近中线、仍可能改进答案的候选点带 strip"
    if name == "q" and "Point q = p - o" in line:
        return "从圆心 o 指向直线基点 p 的位移向量 q"
    if name == "C" and "dot(q, q) - r * r" in line:
        return "直线参数方程代入圆方程后的常数项 C"
    if name == "D" and "B * B - 4 * A * C" in line:
        return "直线与圆求交二次方程的判别式 D"
    if name == "t2" and "(-B + sqrtl(D))" in line:
        return "直线与圆第二个交点对应的参数方程根 t2"
    if name == "step" and "step < n - 2" in line:
        return "Prüfer 编码当前删除第几个叶子的步骤下标 step"
    if name == "z" and "long long z = 2" in line and "Tonelli" in section:
        return "Tonelli-Shanks 正在试探的最小二次非剩余候选 z"
    if name == "cyc" and "vector<int> cyc" in line:
        return "当前置换环按遍历顺序保存的全部元素编号 cyc"
    if name == "cc" and "for (char cc : s)" in line:
        return "从模式串 s 依次读取的字符 cc"
    if name == "cc" and "for (char cc : text)" in line:
        return "从主串 text 依次读取并送入 AC 自动机的字符 cc"
    if name == "cur" and "get_fail(last), c = s[n]" in line:
        return "沿 fail 链找到的、可被新字符扩展的最长回文后缀状态 cur"
    if name == "now" and "int now = ++tot" in line and "回文" in section:
        return "本次新建的回文自动机状态编号 now"
    if name == "u" and "for (int u = 1; u <= tot; ++u) tree[fail[u]]" in line:
        return "当前加入 fail 树的 AC 自动机状态编号 u"
    if name == "cap" and "int cap = 2 * n + 5" in line:
        return "Kruskal 重构树为原点和合并点预留的数组容量 cap"
    if name == "u" and "for (int u = 1; u <= tot; ++u) if (dsu[u] == u)" in line:
        return "当前检查是否为 Kruskal 重构森林根的节点编号 u"
    if name == "u" and "for (int u = 1; u <= tot; ++u)" in line and "Kruskal" in section:
        return "当前填写倍增祖先表的 Kruskal 重构树节点编号 u"
    if name == "dis" and "sqrtl(dd)" in line:
        return "两圆圆心之间的实际距离 dis"
    if name == "target" and "a[i] ^ all" in line:
        return "使操作后 Nim 异或和为 0 时第 i 堆应剩余的石子数 target"
    if name == "same" and "want ^ 1" in line:
        return "与查询值 x 当前二进制位相同的 Trie 分支编号 same"
    if name == "cur" and "for (auto cur : h)" in line and "半平面" in section:
        return "按方向角顺序处理的当前候选半平面 cur"
    if name == "cur" and "long long cur = 0" in line and "差分" in section:
        return "扫描到当前位置时由差分数组累加得到的区间增量 cur"
    if name == "cur" and "long long cur = 1" in line and "BSGS" in section:
        return "BSGS 小步枚举中当前的幂值 a^j mod mod"
    if name == "cur" and re.search(r"int\s+cur\s*=\s*(?:sz\+\+|\+\+tot)", line) and "后缀自动机" in section:
        return "加入新字符后创建的 SAM 状态编号 cur"
    if name == "cur" and "vector<long long> prev" in line:
        return "滚动数组中正在计算的当前 DP 层 cur"
    if name == "prev" and "vector<long long> prev" in line:
        return "滚动数组中保存的上一 DP 层 prev"
    if name == "r" and "int r = s + lb" in line:
        return "Gosper 枚举中大于 s 的下一个同 popcount 掩码构造量 r"
    if name == "r" and "vector<int> sa(n), r(n), nr(n)" in line:
        return "当前轮每个后缀长度 k 前缀的等价类排名数组 r"
    if name == "nr" and "vector<int> sa(n), r(n), nr(n)" in line:
        return "按长度 2k 重新排序后得到的新排名数组 nr"
    if name == "rank" and "vector<int> rank(n), lcp(n)" in line:
        return "每个后缀起点在后缀数组 sa 中的排名 rank"
    if name == "r" and "int r = rank[i]" in line:
        return "后缀 i 在后缀数组 sa 中的排名 r"
    if name == "l" and "lower_bound(xs.begin(), xs.end(), e[j].x1)" in line:
        return "扫描线事件左端横坐标 x1 的离散下标 l"
    if name == "r" and "lower_bound(xs.begin(), xs.end(), e[j].x2)" in line:
        return "扫描线事件右端横坐标 x2 的离散下标 r；更新半开区间 [l,r)"
    if name == "w" and "int w = lca(u, v)" in line:
        return "树上路径 u-v 的最近公共祖先节点 w"
    if name == "id" and "for (auto [v, id] : g[u])" in line:
        return "当前无向边的唯一编号 id，用于跳过 DFS 父边"
    if name == "x" and "for (int x = 1; x <= n; x += 2)" in line:
        return "当前追加到构造序列的奇数 x"
    if name == "vis" and "vector<char> vis" in line and "Burnside" in section:
        return "分解当前群作用置换时记录位置是否已进入某个环的标记 vis"
    if name == "vis" and "vector<int> vis(n), result(n)" in line:
        return "置换环分解中记录每个位置是否已经处理的标记 vis"
    if name == "result" and "vector<int> vis(n), result(n)" in line:
        return "原置换重复应用 k 次后每个位置的映射结果 result"
    if name == "rank" and "int n = a.size(), m = a[0].size() - 1, rank = 0" in line:
        return "高斯消元已经确定主元的行数，即当前矩阵秩 rank"
    if name == "bit" and "int bit = n >> 1" in line:
        return "NTT 位逆序置换中从最高有效位开始移动的掩码 bit"
    if name == "w" and "long long w = 1" in line and "NTT" in section:
        return "NTT 当前蝶形位置使用的单位根幂 w"
    if name == "bad" and "long long bad = 0" in line:
        return "容斥累计得到的、至少被一个给定除数整除的整数个数 bad"
    if name == "l" and "long long l = 1" in line and "容斥" in section:
        return "当前子集内全部除数的最小公倍数 l"
    if name == "bits" and "int bits = 0" in line and "容斥" in section:
        return "当前容斥子集中被选除数的数量 bits"
    if name == "overflow" and "bool overflow = false" in line and "容斥" in section:
        return "当前子集最小公倍数是否已超过安全上界的标记 overflow"
    if name == "ways" and "n / l" in line and "容斥" in section:
        return "1..n 中能被当前子集最小公倍数 l 整除的整数个数 ways"
    if name == "base" and "Point base = a.o + d * (x / dis)" in line:
        return "两圆公共弦中点 base"
    if name == "cp" and "cross(b - a, p - a)" in line:
        return "点 p 相对裁剪有向边 a->b 的带符号叉积 cp"
    if name == "cq" and "cross(b - a, p - a)" in line:
        return "点 q 相对裁剪有向边 a->b 的带符号叉积 cq"
    if name == "q" and "deque<HalfPlane> q" in line:
        return "半平面交中按方向维护有效边界的双端队列 q"
    if name == "ans" and "1e100L" in line and "最近点对" in section:
        return "最近点对当前基础区间内的最小距离平方 ans"
    if name == "ans" and "min(closest" in line:
        return "最近点对左右子区间返回值中的较小距离平方 ans"
    if name == "ans" and "int ans = 0" in line and "暴力解法" in section:
        return "暴力枚举中累计满足题目条件的方案数 ans"
    if name == "ans" and "LLONG_MIN" in line:
        return "整数三分结束后在剩余区间暴力检查得到的最大函数值 ans"
    if name == "ans" and "vector<int> ans" in line and "构造" in section:
        return "按奇数在前、偶数在后生成的构造序列 ans"
    if name == "ans" and "long long ans = 1" in line and any(
        token in section for token in ("组合", "二项式")
    ):
        return "逐项乘除计算组合数 C(n,k) 的累积结果 ans"
    if name == "ans" and "__int128 ans = 0" in line and "容斥" in section:
        return "容斥枚举所有非空集合后累计的带符号计数 ans"
    if name == "ans" and "Poly ans{1}" in line:
        return "多项式快速幂中当前累计乘积 ans"
    if name == "ans" and "push(p, l, r); int m" in line:
        return "线段树查询目标区间时从左右子树累加的区间和 ans"
    if name == "ans" and "int u = 1, ans = 0" in line:
        return "二进制 Trie 贪心过程中已经确定的最大异或值 ans"
    if name == "ans" and "tr[p].get(x)" in line:
        return "李超树当前节点及递归路径在横坐标 x 处的最优函数值 ans"
    if name == "ans" and "first_at_least(p << 1" in line:
        return "左子树中第一个值至少为 x 的位置；不存在时为 -1"
    if name == "ans" and "int u = 0, ans = 0" in line and "Aho" in section:
        return "AC 自动机扫描主串时累计的全部模式匹配次数 ans"
    if name == "ans" and "MstResult ans" in line:
        return "Kruskal 当前生成森林的总权、已选边数、连通状态和边集 ans"
    if name == "ans" and "long long ans = 0" in line and "重链" in section:
        return "重链剖分查询路径 u-v 时累计的各链段区间和 ans"
    if name == "ans" and "__int128 ans = 0, last_y" in line:
        return "扫描线按高度条带累计的矩形并面积 ans"
    if name == "C" and ("Mat C(" in line or "Mat C{}" in line):
        return "矩阵乘法正在累加构造的结果矩阵 C"
    if name == "q" and ("st[p].next" in line or "q = next[p][c]" in line):
        return "SAM 状态 p 经当前字符转移到的既有状态 q"
    if name == "q" and "for (int q : {p << 1" in line:
        return "线段树节点 p 当前枚举的一个孩子节点编号 q"
    if name == "q" and "q = p - 1" in line:
        return "分解 p-1=q*2^s 后得到的奇数因子 q"
    if name == "t" and re.search(r"\bint\s+t\s*=\s*1\s*;", line):
        return "当前程序要执行的测试用例数量 t"
    if name == "t" and "(d / g) * x" in line:
        return "CRT 合并时由 Bézout 系数求出的第二个模数倍数 t"
    if name == "t" and "a[i][col]" in line:
        return "高斯消元当前行在主元列上的消元系数 t"
    if name == "t" and "cross(b.v, b.a - a.a)" in line:
        return "两直线交点在直线 a 参数方程中的参数 t"
    if name == "t" and "dot(c.o - a, d) / dd" in line:
        return "圆心 c.o 在线段 a-b 所在直线上的投影参数 t"
    if name == "t" and "cp / (cp - cq)" in line:
        return "线段 p-q 与裁剪边界交点的线性插值参数 t"
    if name == "t" and "cross(b.p - a.p, b.v)" in line:
        return "两直线交点在直线 a 参数方程中的参数 t"
    if name == "it" and re.search(r"\bauto\s+it\s*=\s*\w+\.find\(", line):
        source = re.search(r"=\s*(\w+)\.find\(", line).group(1)
        return f"容器 {source} 中当前查找结果的迭代器 it"
    if name == "it" and "vector<int> level, it" in line:
        return "Dinic 中每个顶点下一条待尝试边的当前弧下标 it"
    if name == "t2" and "make_tuple" in line:
        return "用于演示 tuple 构造与字典序比较的三元组 t2"
    if name == "path" and "vector<int> path" in line:
        return "排列 DFS 当前已经选定的前缀 path"
    if name == "used" and "vector<int> used" in line:
        return "排列 DFS 中标记每个候选数是否已进入 path 的数组 used"
    if name == "st" and "nextGreater" in line:
        return "维护下标且对应值单调递减的栈 st"
    if name == "st" and "unordered_set" in line:
        return "用于按 pair 键去重的无序集合 st"
    if name == "st" and "vector<int> st" in line:
        if "Kruskal" in section:
            return "遍历 Kruskal 重构森林并计算深度的顶点栈 st"
        if "LCT" in section or "Link-Cut" in section:
            return "splay 前按自底向上顺序收集的辅助树祖先栈 st"
        if "Hierholzer" in section or "欧拉" in section:
            return "Hierholzer 算法维护当前欧拉游走的顶点栈 st"
    if name == "st" and re.search(r"for\s*\(int\s+st\s*=\s*min_start", line):
        return "当前候选周期开始的 0-based 位置 st"
    if name == "e" and "mg[pv[v]][pe[v]]" in line:
        return "最短增广路上从 pv[v] 指向 v 的残量边引用 e"
    if name == "e" and "Point e = d * (1 / len)" in line:
        return "从圆心 a 指向圆心 b 的单位方向向量 e"
    if name == "base" and "base = a + e * x" in line:
        return "两圆公共弦中点 base"
    if name == "per" and "Point per = {-e.y, e.x}" in line:
        return "与圆心连线单位方向 e 垂直的单位向量 per"
    if name == "p" and re.search(r"int\s+p\s*=\s*row", line):
        return "高斯消元为当前列搜索到的主元行 p"
    if name == "p" and re.search(r"int\s+p\s*=\s*\+\+tot", line):
        return "新建可持久化节点的编号 p"
    if name == "p" and re.search(r"for\s*\(int\s+p\s*=\s*1;.*p\s*\*\s*2\s*<=\s*n", line):
        return "当前验证的候选周期长度 p"
    if name == "p" and "pair<int, int> p" in line:
        return "用于演示 pair 接口的整数对 p"
    if name == "p" and "vector<int> p(n)" in line and any(
        token in section for token in ("排列", "随机数据")
    ):
        return "待随机打乱为 1..n 排列的数组 p"
    if name == "p" and "p = last" in line:
        return "SAM 扩展前原末状态的游走指针 p"
    if name == "n" and ".size()" in line:
        source = re.search(r"n\s*=\s*(?:\(int\))?([A-Za-z_]\w*)\.size\(\)", line)
        if source:
            return f"容器 {source.group(1)} 的元素数量 n"
    if name == "n" and "code.size() + 2" in line:
        return "Prüfer 序列对应树的顶点数 n"
    if name == "n" and "g.size() - 1" in line:
        return "1-based 树邻接表 g 中的顶点数 n"
    if name == "n" and "p.size()" in line:
        return "输入排列 p 的长度 n"
    if name == "v" and "forward ? c.newv : c.oldv" in line:
        return "正向修改采用新值、撤销修改采用旧值的实际写入值 v"
    if name in {"x", "y"} and name + " = find(" in line:
        return f"Kruskal 当前边一端所在连通块的代表元 {name}"
    if name == "v" and "stk.back()" in line:
        return "Tarjan 当前弹出并归入强连通分量的顶点 v"
    if name == "c" and "get_centroid" in line:
        return "当前未删除连通块的重心顶点 c"
    if name == "d" and re.search(r"vector<.*>\s+d\(n,", line):
        return "从指定源点到各顶点的距离数组 d"
    if name == "d" and "a2 - a1" in line:
        return "两个同余方程余数之差 d=a2-a1"
    if name == "d" and re.search(r"\bPoint\s+d\s*=\s*b\s*-\s*a", line):
        return "从点 a 指向点 b 的方向向量 d"
    if name == "res" and "memo[" in line:
        return "当前 DP 状态对应的记忆化答案引用 res"
    if name == "res" and "vector<long long> res{0}" in line:
        return "当前半区枚举得到的全部子集和 res"
    if name == "res" and "vector<int> res" in line:
        if "排列序" in section:
            return "逆 Cantor 展开逐位构造的排列 res"
        if "随机数据" in section:
            return "尚未重复采样得到的随机整数结果 res"
    if name == "safe_product":
        return "用 __int128 计算并取模后安全转回 long long 的乘积 safe_product"
    if name == "chosen" and "priority_queue" in line:
        return "维护当前已选任务收益的最小堆 chosen"
    if name == "chosen":
        return "当前已选且满足验证条件的对象数量 chosen"
    if name == "last" and "numeric_limits<int>::min" in line:
        return "上一个被贪心选择的位置 last，初值表示尚未选择"
    if name == "h2":
        return "圆交计算中从圆心连线到交点的垂直距离平方 h2"
    if name == "h" and "vector<Point> h" in line:
        return "Andrew 算法逐步维护的凸包顶点栈 h"
    if name == "h" and "size_t h = 0" in line:
        return "状态哈希的累计值 h"
    if name == "h" and "sqrtl(h2)" in line:
        return "圆交点相对圆心连线的垂直偏移长度 h"
    if name == "h" and "vector<unsigned long long> h" in line:
        return "字符串哈希的前缀哈希数组 h"
    if name == "now" and "++tot" in line:
        if "持久化" in section:
            return "本次新建的持久化数据结构节点编号 now"
        if "自动机" in section:
            return "本次新建的字符串自动机状态编号 now"
    if name == "B" and "sqrt(n)" in line:
        return "块状数组采用的块长 B"
    if name == "depth" and "vector<int> tin" in line:
        return "DFS 树中每个顶点的深度数组 depth"
    if name == "seen" and "bool seen[MAXG]" in line:
        return "记录当前状态各后继 SG 值是否出现的布尔表 seen"
    if name == "seen" and "moves.size()" in line:
        return "为当前减法游戏状态标记后继 SG 值的时间戳数组 seen"
    if name == "A" and "dot(v, v)" in line:
        return "直线参数方程代入圆方程后的二次项系数 A"
    if name == "B" and "2 * dot(q, v)" in line:
        return "直线参数方程代入圆方程后的一次项系数 B"
    if name == "x" and "mod_pow(a, (p - 1) / 2" in line:
        return "Euler 判别得到的 a^((p-1)/2) mod p 值 x"
    if name == "x" and "mod_pow(n, (q + 1) / 2" in line:
        return "Tonelli-Shanks 当前平方根候选 x"
    if name == "c" and "mod_pow(z, q, p)" in line:
        return "Tonelli-Shanks 当前 2 幂阶生成元 c"
    if name == "t" and "mod_pow(n, q, p)" in line:
        return "Tonelli-Shanks 当前误差项 t"
    if name == "m" and re.search(r"m\s*=\s*s", line):
        return "Tonelli-Shanks 当前误差项的 2 幂阶上界 m"
    if name == "ni" and "qpow(n, MOD - 2)" in line:
        return "逆变换使用的长度 n 模逆元 ni"
    if name == "n" and re.fullmatch(r"\s*int\s+n\s*;\s*", line):
        if "线性基" in section:
            return "待插入线性基的整数个数 n"
        if "暴力解法" in section or "随机数据" in section:
            return "输入数组的元素个数 n"
        return "当前测试用例读入的元素个数 n"
    if name == "n" and "int n = 4, k = 2" in line:
        return "被选元素全集的大小 n"
    if name == "a" and "__int128 a = 1" in line:
        return "演示 __int128 算术与模乘的 128 位整数 a"
    if name == "j" and "B[(unsigned char)p[j]][j]" in line:
        return "Shift-And 模式串 p 当前写入位掩码的字符位置 j"
    if name == "j" and "j = i + 1; j < n" in line:
        return "Cantor 排名中位于 i 之后、用于统计较小元素的位置 j"
    if name == "j" and "j = i; j < n" in line and "暴力解法" in section:
        return "暴力枚举中从起点 i 向右扩展的子数组终点 j"
    if name == "j" and "j < old" in line:
        return "组合生成中复制上一轮已有结果的下标 j"
    if name == "j" and "j < A.n" in line:
        return "矩阵乘法结果矩阵的列下标 j"
    if name == "j" and "j < (int)b.size()" in line:
        return "多项式 b 当前参与卷积的系数下标 j"
    if name == "j" and "j = col; j < n" in line:
        return "模高斯消元中从主元列 col 开始更新的列下标 j"
    if name == "j" and "j < len / 2" in line:
        return "NTT 长度为 len 的蝶形块内偏移下标 j"
    if name == "j" and "j = col; j < m" in line:
        return "高斯消元中从主元列 col 开始更新的增广矩阵列下标 j"
    if name == "j" and "j = col; j <= m" in line:
        return "实数高斯消元中从主元列到常数列的更新下标 j"
    if name == "j" and "for (long long j = 0; j < m" in line:
        return "BSGS 小步表中指数 j，对应 a^j mod mod"
    if name == "j" and "j < 2" in line and "矩阵" in section:
        return "2×2 转移矩阵的列下标 j"
    if name == "j" and "j = m + 1; j <= r" in line:
        return "CDQ 合并中扫描右半区间 [m+1,r] 的点下标 j"
    if name == "j" and "int n = s.size(), i = 0, j = 1" in line:
        return "最小循环表示算法当前第二个候选起点 j"
    if name == "j" and "int j = sa[r-1]" in line:
        return "后缀数组中排名紧邻后缀 i 之前的后缀起点 j"
    if name == "j" and "int j = pi[i - 1]" in line:
        return "前缀函数计算中当前可回退的已匹配前缀长度 j"
    if name == "j" and "string t = s + s; int i = 0, j = 1" in line:
        return "最小循环表示算法当前第二个候选起点 j"
    if name == "j" and "j = 1; j <= m" in line and "最长公共" in section:
        return "LCS 状态 lcs[i][j] 对应的字符串 b 前缀长度 j"
    if name == "j" and "j = 1; j <= m" in line and "滚动" in section:
        return "滚动数组中正在计算的当前 DP 状态下标 j"
    if name == "j" and "j = 1; j <= m" in line and "最长公共" in section:
        return "LCS 状态 lcs[i][j] 对应的字符串 b 前缀长度 j"
    if name == "j" and "j = i + 1; j < (int)strip.size()" in line:
        return "最近点对候选带中位于 i 之后、纵坐标差仍可能改进答案的点下标 j"
    if name == "j" and "j < i" in line and "inside(c, p[j])" in line:
        return "最小覆盖圆随机增量中检查当前圆是否覆盖的先前点下标 j"
    if name == "j" and "int j = i" in line and "扫描线" in section:
        return "扫描线中从 i 开始寻找同一 y 坐标事件组末尾的下标 j"
    if name == "j" and "j = optL" in line:
        return "分治 DP 在允许区间 [optL,optR] 内枚举的候选决策点 j"
    if name == "i" and "bs._Find_first()" in line:
        return "动态 bitset 中当前找到的置位下标 i"
    if name == "i" and "i < (int)t.size()" in line and "Shift" in section:
        return "Shift-And 扫描主串 t 的当前字符位置 i"
    if name == "i" and "i = 60; i >= 0" in line:
        return "线性基从高到低贪心检查的二进制位 i"
    if name == "i" and "i = pos; i < n" in line and any(
        token in section for token in ("组合", "排列", "DFS")
    ):
        return "组合 DFS 当前可选择的数组元素下标 i"
    if name == "i" and "i = l; i < r" in line and "old" not in line and "最近点对" not in section:
        return "当前半开区间 [l,r) 内顺序枚举的元素下标 i"
    if name == "i" and "pre[i] = pre[i - 1] + a[i]" in line:
        return "正在计算前缀和 pre[i] 的 1-based 数组位置 i"
    if name == "i" and "fac[i] = fac[i - 1]" in line:
        return "阶乘表正在预处理的整数下标 i"
    if name == "i" and "ifac[i - 1] = ifac[i]" in line:
        return "逆阶乘表自后向前递推的整数下标 i"
    if name == "i" and "long long i = 1, tt" in line:
        return "Tonelli-Shanks 中寻找 t^(2^i)=1 的最小指数 i"
    if name == "i" and "i = 0; i < A.n" in line:
        return "矩阵乘法结果矩阵的行下标 i"
    if name == "i" and "i < (int)a.size()" in line and "卷积" in section:
        return "多项式 a 当前参与卷积的系数下标 i"
    if name == "i" and "if (!vis[i])" in line and (
        "Burnside" in section or "p.size()" in line
    ):
        return "当前群作用置换中尚未归入置换环的位置 i"
    if name == "i" and "deg[i] == 1" in line:
        return "Prüfer 解码初始化时检查度数的顶点编号 i"
    if name == "i" and "i = col + 1; i < n" in line:
        return "模高斯消元中在主元行下方寻找非零元的候选行 i"
    if name == "i" and "i = 1, j = 0; i < n" in line:
        return "NTT 位逆序置换中当前待重排的系数下标 i"
    if name == "i" and "i = 0; i < n; i += len" in line:
        return "NTT 长度为 len 的蝶形块起始下标 i"
    if name == "i" and "i != rank && a[i][col]" in line:
        return "模高斯消元中当前用主元行消去的其它行下标 i"
    if name == "i" and "i = row; i < n" in line and "a[i][col]" in line:
        return "高斯消元中为当前主元列寻找非零元的候选行 i"
    if name == "i" and "i != row" in line and "高斯" in section:
        return "高斯消元中当前用主元行消去的其它方程行 i"
    if name == "i" and "i = row + 1; i < n" in line:
        return "实数高斯消元中在主元行下方寻找最大绝对值元的候选行 i"
    if name == "i" and "i = row; i < n" in line and "高斯" in section:
        return "实数高斯消元结束后检查一致性的剩余方程行 i"
    if name == "i" and "int i = l" in line and "CDQ" in section:
        return "CDQ 合并中扫描左半区间 [l,m] 的点下标 i"
    if name == "i" and "i = 1; i < (int)s.size()" in line:
        return "前缀函数正在计算 pi[i] 的字符串位置 i"
    if name == "i" and "i < (int)text.size()" in line:
        return "KMP 正在扫描的主串字符位置 i"
    if name == "i" and "i = 1; i < n" in line and "Z" in section:
        return "Z 函数正在计算 z[i] 的后缀起点 i"
    if name == "i" and "i + 1 < (int)t.size()" in line:
        return "Manacher 扩展串中当前计算回文半径的中心位置 i"
    if name == "i" and "r[i] = (unsigned char)s[i]" in line:
        return "后缀数组初始化单字符排名的后缀起点 i"
    if name == "i" and "rk[i] = s[i]" in line:
        return "后缀数组初始化单字符排名的后缀起点 i"
    if name == "i" and "i = 1; i < n" in line and "后缀数组" in section:
        return "后缀数组排序后用于比较相邻后缀并重编号的排名位置 i"
    if name == "i" and "rank[sa[i]] = i" in line:
        return "后缀数组 sa 中当前排名位置 i"
    if name == "i" and "i = 0, h = 0; i < n" in line:
        return "Kasai 算法当前计算 LCP 的后缀起点 i"
    if name == "i" and "string t = s + s; int i = 0" in line:
        return "最小循环表示算法当前第一个候选起点 i"
    if name == "i" and "int n = s.size(), i = 0" in line:
        return "最小循环表示算法当前第一个候选起点 i"
    if name == "i" and "i = l; i < r" in line and "最近点对" in section:
        return "最近点对当前半开区间 [l,r) 内枚举的点下标 i"
    if name == "i" and "i < (int)strip.size()" in line:
        return "最近点对候选带中作为当前基准点的下标 i"
    if name == "i" and "i < (int)p.size()" in line and "inside(c, p[i])" in line:
        return "最小覆盖圆随机增量中当前检查的点下标 i"
    if name == "i" and "i < (int)e.size()" in line and "扫描线" in section:
        return "扫描线中当前 y 坐标事件组的首事件下标 i"
    if name == "i" and "i < n" in line and "旋转卡壳" in section:
        return "旋转卡壳当前枚举的凸包边起点 i"
    if name == "i" and "i = (int)p.size() - 2" in line:
        return "Andrew 算法自右向左构造凸包上链的点下标 i"
    if name == "i" and "i < (int)poly.size()" in line:
        return "凸多边形裁剪中当前有向边起点的顶点下标 i"
    if name == "i" and "i < (int)q.size()" in line and "半平面" in section:
        return "半平面交结果中当前相邻有效边界的下标 i"
    if name == "i" and "i = 1; i < (int)a.size(); i += 2" in line:
        return "阶梯 Nim 中参与等价异或的奇数层下标 i"
    if name == "i" and "i < (int)a.size()" in line and "Nim" in section:
        return "Nim 当前尝试执行必胜移动的石子堆下标 i"
    if name == "i" and "i = st + p; i < n" in line:
        return "SG 周期验证中与位置 st 对应的后续位置 i"
    if name == "i" and "i < (int)mg[u].size()" in line:
        return "最小费用流中当前检查的顶点 u 出边下标 i"
    if name == "i" and "i < n" in line and "bitset 优化背包" in section:
        return "bitset 0/1 背包当前加入的物品下标 i"
    if name == "i" and "i < n" in line and section == "排列与组合":
        return "当前子集掩码中正在检查是否被选中的元素位 i"
    if name == "i" and "i <= n" in line and "DFS 递归生成全排列" in section:
        return "无重复全排列 DFS 当前尝试放入路径的候选值 i"
    if name == "i" and "i < n" in line and "DFS 递归生成全排列" in section:
        return "含重复元素全排列 DFS 当前尝试使用的 nums 下标 i"
    if name == "i" and "fact[i] = fact[i-1]" in line:
        return "Cantor 排名使用的阶乘表下标 i"
    if name == "i" and "avail.push_back(i)" in line:
        return "逆 Cantor 展开初始化可用值集合的元素值 i"
    if name == "i" and "其他实用工具" in section:
        return "坐标离散化时当前回写压缩编号的数组下标 i"
    if name == "i" and "SOS DP" in section:
        return "SOS DP 当前向所有掩码传播贡献的二进制位 i"
    if name == "i" and "i = 2; i <= n" in line and "随机数据" in section:
        return "随机树生成中当前新加入的顶点编号 i"
    if name == "i" and "i < n" in line and "随机数据" in section:
        return "随机数据生成器当前输出的数组位置 i"
    if name == "i" and "i < n" in line and "暴力解法" in section:
        return "暴力枚举子数组的起点 i"
    if name == "i" and "for (long long i = 1; i <= k" in line:
        return "小组合数 C(n,k) 逐项乘除时的因子下标 i"
    if name == "i" and "a[i][i] = 1" in line:
        return "单位矩阵当前写入对角元的行列下标 i"
    if name == "i" and "i < (int)a.size()" in line and any(
        token in section for token in ("多项式", "生成函数")
    ):
        return "多项式 a 当前参与卷积的系数下标 i"
    if name == "i" and "if (!vis[i])" in line and "置换与循环" in section:
        return "置换环分解中当前尚未访问的位置 i"
    if name == "i" and "i <= n" in line and any(
        token in section for token in ("线性筛", "莫比乌斯")
    ):
        return "线性筛当前处理的整数 i"
    if name == "i" and "i <= m" in line and any(
        token in section for token in ("BSGS", "Giant-step")
    ):
        return "BSGS 巨步枚举次数 i，对应指数块 i*m"
    if name == "i" and "i < 2" in line and "矩阵" in section:
        return "2×2 转移矩阵的行下标 i"
    if name == "i" and "i = 0; i < n" in line and "高斯消元" in section:
        return "实数高斯消元中当前回填唯一解的方程行 i"
    if name == "i" and "i <= n" in line and any(
        token in section for token in ("线性区间更新", "高阶前缀")
    ):
        return "还原线性区间更新后点值的 1-based 位置 i"
    if name == "i" and "i <= n" in line and "一维差分" in section:
        return "差分数组还原时当前累加并写回的 1-based 位置 i"
    if name == "i" and "i < n" in line and "单调栈" in section:
        return "单调栈正在处理并确定右侧更大元素的数组位置 i"
    if name == "i" and "i < n" in line and "单调队列" in section:
        return "滑动窗口右端新加入单调队列的数组位置 i"
    if name == "i" and "i < n" in line and "字符串哈希" in section:
        return "字符串哈希正在扩展前缀哈希的字符位置 i"
    if name == "i" and "pq.push({value[i], i})" in line:
        return "在线中位数初始化时加入优先队列的数组位置 i"
    if name == "i" and "i = l; i <= r" in line:
        return "分块区间修改中直接更新的数组位置 i"
    if name == "i" and "i = l; i < (bl + 1) * B" in line:
        return "分块修改左侧不完整块中直接更新的数组位置 i"
    if name == "i" and "i = br * B; i <= r" in line:
        return "分块修改右侧不完整块中直接更新的数组位置 i"
    if name == "i" and "sz[i] = 1" in line:
        return "Kruskal 重构树初始化子树大小的原图顶点编号 i"
    if name == "i" and "i = 1; i < n" in line and "最大子段" in section:
        return "最大子段和扫描中当前作为结尾的数组位置 i"
    if name == "i" and "i <= n" in line and "最长公共" in section:
        return "LCS 状态 lcs[i][j] 对应的字符串 a 前缀长度 i"
    if name == "i" and "i <= n" in line and "滚动数组" in section:
        return "滚动数组中正在计算的当前 DP 层编号 i"
    if name == "i" and "i < n" in line and "单调队列优化" in section:
        return "单调队列优化 DP 当前计算的状态位置 i"
    if name == "i" and "i < n" in line and any(
        token in section for token in ("状态压缩", "状压博弈")
    ):
        return "状态压缩 DP 状态 mask 中当前尝试选择的对象位 i"
    if name == "i" and "i < (int)p.size()" in line and "多边形" in section:
        return "多边形面积叉积和中当前有向边起点的顶点下标 i"
    if name == "a" and "vector<int> a = {" in line:
        return "用于演示排列算法的整数序列 a"
    if name == "a" and "vector<int> a = input" in line:
        return "输入数组 input 的工作副本 a"
    if name == "a" and re.search(r"vector<.*>\s+a\(n\)", line):
        if "块状数组" in section:
            return "块状数组逐点保存的原始元素数组 a"
        if "暴力解法" in section:
            return "暴力解法读入的长度为 n 的整数数组 a"
        return "当前算法按下标保存的 n 个输入元素数组 a"
    if name == "a" and re.search(r"\bint\s+a\s*,\s*b\s*,\s*c\s*;", line):
        return "字符串解析得到的第一个整数 a"
    if name == "b" and re.search(r"\bint\s+a\s*,\s*b\s*,\s*c\s*;", line):
        return "字符串解析得到的第二个整数 b"
    if name == "c" and re.search(r"\bint\s+a\s*,\s*b\s*,\s*c\s*;", line):
        return "字符串解析得到的第三个整数 c"
    if name == "a" and "int a = sa[i-1]" in line:
        return "字典序前一个后缀的起点 a=sa[i-1]"
    if name == "b" and "b = sa[i]" in line:
        return "字典序当前后缀的起点 b=sa[i]"
    if name == "a" and "up[j][u]" in line:
        return "顶点 u 的 2^j 级祖先 a"
    if name == "b" and re.search(r"for\s*\(int\s+b\s*=\s*30", line):
        return "二进制 Trie 当前处理的位编号 b"
    if name == "b" and "tag[b] += v" in line:
        return "块状数组当前整块更新的块编号 b"
    if name == "b" and "(x >> bit) & 1" in line:
        return "整数 x 在当前 bit 位上的二进制值 b"
    if name == "b" and "MCEdge b" in line:
        return "与正向费用流边配对的反向残量边 b"
    if name == "b" and "t[x].ch[dx ^ 1]" in line:
        return "旋转后要接到 y 下方的子树根 b"
    if name == "c" and "a * (2 * b - a)" in line:
        return "快速倍增公式得到的 F(2k) 值 c"
    if name == "c" and ("Poly c(" in line or "vector<long long> c(" in line):
        return "存放卷积系数的结果多项式 c"
    if name == "c" and re.search(r"for\s*\(int\s+c", line) and any(
        token in section for token in ("字符串", "自动机", "Trie", "字母")
    ):
        return "当前枚举的 0-based 字母表编号 c"
    if name == "c" and re.search(r"for\s*\(char\s+c", line):
        return "当前从输入字符串枚举的字符 c"
    if name == "c" and "c = s[n]" in line:
        return "本次加入回文自动机的字符编号 c"
    if name == "c" and "c = cc - 'a'" in line:
        return "当前文本字符映射到的字母表编号 c"
    if name == "m" and "a[0].size()" in line:
        return "增广矩阵 a 的列数 m"
    if name == "m" and "m = n" in line and "row" in line:
        return "方阵 a 的列数 m"
    if name == "m" and re.search(r"m\s*=\s*l\s*\+.*r\s*-\s*l", line):
        return "当前递归区间 [l,r] 的中点 m"
    if name == "m" and re.search(r"m\s*=\s*\(l\s*\+\s*r\)", line):
        return "当前递归区间 [l,r] 的中点 m"
    if name == "p" and "Point p = poly[i]" in line:
        return "待裁剪多边形当前边的起点 p"
    if name == "q" and "poly[(i + 1) % poly.size()]" in line:
        return "待裁剪多边形当前边的终点 q"
    if name == "x" and "__int128 x = 0" in line:
        return "十进制读入过程中累计绝对值的 __int128 结果 x"
    if name == "x" and re.fullmatch(r"\s*unsigned long long\s+x\s*;\s*", line):
        return "当前读入并待插入线性基的整数 x"
    if name == "x" and "int x = 0, ones = 0" in line:
        return "反常 Nim 全部堆石子数的异或和 x"
    if name == "x" and re.search(r"for\s*\(int\s+x\s*=\s*1;\s*x\s*<=", line) and any(
        token in section for token in ("SG", "Sprague", "减法游戏")
    ):
        return "当前计算 SG 值的石子数 x"
    if name == "x" and "x = c - 'a'" in line:
        return "当前字符映射到的字母表编号 x"
    if name == "x" and "a.r * a.r - b.r * b.r" in line:
        return "两圆公共弦中点沿圆心连线离圆 a 圆心的距离 x"
    if name in {"x", "y"} and "long long x, y, g = exgcd" in line:
        return f"exgcd 返回、满足 m1*x+m2*y=gcd(m1,m2) 的 Bézout 系数 {name}"
    if name in {"x", "y"} and re.search(r"long long\s+x\s*,\s*y\s*;", line):
        return f"exgcd 写回的 Bézout 系数 {name}"
    if name == "x" and re.search(r"for\s*\(long long\s+x\s*=\s*l", line):
        return "暴力检查凹凸函数值的当前整数横坐标 x"
    if name == "x" and "x = 1; x <= n; x += 2" in line:
        return "当前追加到构造序列的奇数 x"
    if name == "x" and "x = 2; x <= n; x += 2" in line:
        return "当前追加到构造序列的偶数 x"
    if name == "k" and "A.a[i][k]" in line:
        return "矩阵乘法中连接行 i 与列 j 的公共维下标 k"
    if name == "k" and re.search(r"k\s*=\s*0;\s*k\s*<\s*2", line):
        return "二阶转移矩阵乘法的公共维下标 k"
    if name == "k" and "optl" in line:
        return "当前 DP 状态枚举的候选决策下标 k"
    if name == "k" and "k < j" in line and "最小覆盖圆" in section:
        return "最小圆增量构造中早于 j 的历史点下标 k"
    if name == "k" and "int k = 0" in line and "while" not in line and any(
        token in section for token in ("最小循环表示", "Booth")
    ):
        return "比较两个循环表示时已匹配的偏移长度 k"
    if name == "k" and "k = 0" in line and "Booth" in section:
        return "比较两个循环表示时已匹配的偏移长度 k"
    if name == "u" and "u = a[i + j]" in line:
        return "NTT 蝶形运算左半位置的旧系数 u"
    if name == "v" and "w * a[i + j + len / 2]" in line:
        return "NTT 蝶形运算右半位置乘单位根后的系数 v"
    if name == "u" and "u = i; !vis[u]; u = perm[u]" in line:
        return "沿当前置换环移动的元素编号 u"
    if name == "u" and "u = i; !vis[u]; u = p[u]" in line:
        return "沿置换 p 当前环移动的元素编号 u"
    if name == "u" and re.search(r"for\s*\(int\s+u\s*=\s*1;\s*u\s*<=\s*n", line) and any(
        token in section for token in ("树", "图", "Kruskal")
    ):
        return "当前枚举的树顶点编号 u"
    if name == "u" and "int u = 0" in line and "ans" not in line and (
        "字符串" in section or "自动机" in section
    ):
        return "字符串自动机从根开始游走的状态编号 u"
    if name == "u" and "int u = 1" in line and "Trie" in section:
        return "二进制 Trie 根节点编号 u"
    if name == "u" and "int u = 0, ans = 0" in line and any(
        token in section for token in ("字符串", "自动机", "Aho", "AC")
    ):
        return "字符串自动机从根开始扫描的状态编号 u"
    if name == "d" and "a * a + b * b" in line:
        return "快速倍增公式得到的 F(2k+1) 值 d"
    if name == "d" and re.search(r"for\s*\(int\s+d\s*=\s*0;\s*d\s*<=", line) and "数位" in section:
        return "数位 DP 当前枚举的十进制数字 d"
    if name == "d" and "dep[u] - dep[v]" in line:
        return "把较深顶点提升到同深度所需的层数差 d"
    if name == "res" and "vector<pair<long long, int>> res" in line and any(
        token in section for token in ("质因数", "质因子", "分解")
    ):
        return "按试除顺序收集的质因子及指数列表 res"
    if name == "res" and "long long res = 0" in line and "数位" in section:
        return "当前数位 DP 状态累计的合法后缀方案数 res"
    if name == "res" and "int res = 0" in line and "CDQ" in section:
        return "当前 CDQ 子问题累计的逆序贡献数 res"
    if name == "res" and "tree[p].get(x)" in line:
        return "李超树当前节点直线在横坐标 x 处的候选最优值 res"
    if name == "sum" and "long long sum = 0" in line and "Burnside" in section:
        return "Burnside 引理对每个群元素固定染色数的累加和 sum"
    if name == "len" and re.search(r"for\s*\(int\s+len\s*=\s*2", line) and "len <<= 1" in line:
        return "NTT 当前蝶形合并块的长度 len"
    if name == "len" and "sqrtl(dot(d, d))" in line:
        return "两个圆心之间的距离 len"
    if name == "len" and "hypotl(d.x, d.y)" in line:
        return "两个输入圆心之间的距离 len"
    if name == "len" and "for (int len = 2; len <= n" in line:
        return "区间 DP 当前枚举的区间长度 len"
    if name == "lim" and "tight ? digits[pos] : 9" in line:
        return "当前数位受 tight 约束允许枚举的最大数字 lim"
    if name == "cnt" and "int cnt = 0" in line and "Prim" in section:
        return "Prim 已经加入生成树的顶点数量 cnt"
    if name == "y" and "t[x].fa" in line:
        return "LCT 旋转中节点 x 的父节点 y"
    if name == "z" and "t[y].fa" in line:
        return "LCT 旋转中节点 y 的父节点 z"
    if name == "dx" and "t[y].ch[1] == x" in line:
        return "节点 x 是 y 的右儿子时为 1 的方向标记 dx"
    if name == "k" and "int n = 4, k = 2" in line:
        return "需要从 n 个元素中选取的元素个数 k"
    if name == "k" and "int k = 5" in line:
        return "限制输出的前 k 个排列数量 k"
    if name == "i" and "i < k; i++) cout << a[i]" in line:
        return "当前输出所选组合中第 i 个元素的下标 i"
    if name == "i" and "i < n; i++) cin >> a[i]" in line:
        return "当前从输入读取数组元素的下标 i"
    if name == "lb" and "int lb = s & (-s)" in line:
        return "Gosper 枚举中当前掩码 s 的最低位 1 对应权值 lb"
    if name == "u" and "randint(1, n), v = randint(1, n)" in line:
        return "随机简单图候选边的第一个端点 u"
    if name == "v" and "randint(1, n), v = randint(1, n)" in line:
        return "随机简单图候选边的第二个端点 v"
    if name == "x" and "randint(lo, hi)" in line:
        return "当前采样并检查去重的随机整数 x"
    if name == "a" and "vector<int> a(n)" in line:
        return "暴力解法读入的长度为 n 的整数数组 a"
    if name == "v" and "int v = 0" in line and "Prüfer" in section:
        return "Prüfer 编码中与当前叶子相邻的未删除顶点 v"
    if name == "v" and "int v = leaves.top()" in line:
        return "Prüfer 解码结束时剩余的第二个叶子顶点 v"
    if name == "k" and re.search(r"(?:long long|long double)\s+k\s*=\s*a\[i\]\[col\]", line):
        return "高斯消元用当前行消去主元列的倍数 k"
    if name == "r" and "long long sum(int x)" in line:
        return "树状数组前缀 [1,x] 的累计和 r"
    if name == "k" and "ll k = 0, b = 0" in line:
        return "空李超树节点使用的直线斜率 k"
    if name == "b" and "ll k = 0, b = 0" in line:
        return "空李超树节点使用的直线截距 b"
    if name == "x" and "int x = p * 2" in line:
        return "线段树节点 p 的左儿子编号 x"
    if name == "y" and "y = p * 2 + 1" in line:
        return "线段树节点 p 的右儿子编号 y"
    if name == "v" and "int &v = ch[u][c]" in line:
        return "自动机状态 u 经字符 c 转移到的状态引用 v"
    if name == "u" and "get_fail(last)" in line:
        return "沿 fail 链找到的可被当前字符扩展的回文状态 u"
    if name == "v" and "int v = ++tot" in line and "回文" in section:
        return "本次新建的回文自动机状态编号 v"
    if name == "t" and "string t = s + s" in line:
        return "用于寻找最小循环表示的双倍字符串 t=s+s"
    if name == "k" and "int k = 0" in line and any(
        token in section for token in ("最小循环表示", "Booth")
    ):
        return "两个循环表示从当前位置起已匹配的字符数 k"
    if name == "v" and "dist[v] <" in line:
        return "当前检查势能更新的费用流顶点 v"
    if name == "v" and "v = t; v != s; v = pv[v]" in line:
        return "沿最短增广路从汇点回溯到源点的当前顶点 v"
    if name == "y" and "for (int y = x; !is_root(y)" in line:
        return "从 x 沿辅助树父链上溯并收集祖先的当前节点 y"
    if name == "y" and "for (int y = 0; x; x = t[y = x].fa)" in line:
        return "access 中上一轮已处理的首选路径根 y"
    if name == "v" and re.search(r"for\s*\(int\s+v\s*=\s*0;\s*v\s*<\s*n", line) and any(
        token in section for token in ("状态压缩", "状压", "DP")
    ):
        return "状态压缩 DP 当前尝试加入集合的顶点 v"
    if name == "u" and re.search(r"for\s*\(int\s+u\s*=\s*0;\s*u\s*<\s*n", line) and any(
        token in section for token in ("状态压缩", "状压", "DP")
    ):
        return "状态压缩 DP 当前路径末端的顶点 u"
    if name == "u" and "for (int u = n - 1" in line and any(
        token in section for token in ("期望", "概率")
    ):
        return "按逆拓扑序计算期望的当前状态 u"
    if name == "len" and "sqrtl(dot(d,d))" in line.replace(" ", ""):
        return "两个输入圆心之间的距离 len"
    if name == "x" and "r*r-R*R+len*len" in line.replace(" ", ""):
        return "公共弦中点沿圆心连线离圆 a 圆心的距离 x"
    if name == "c" and "Circlec{{0,0},-1}" in line.replace(" ", ""):
        return "随机增量算法当前维护的最小覆盖圆 c"
    if name == "m1" and "l + (r - l) / 3" in line:
        return "整数三分区间内靠左的三等分点 m1"
    if name == "m2" and "r - (r - l) / 3" in line:
        return "整数三分区间内靠右的三等分点 m2"
    if name == "other" and "mask ^ sub" in line:
        return "mask 中除 sub 之外的互补子集 other"
    if name == "s" and re.search(r"\bstring\s+s\b", line):
        return "从标准输入读取、供当前字符串算法处理的字符串 s"
    if name == "s" and re.search(r"\bset<.*>\s+s\b", line):
        return "用于演示有序集合接口的 set 容器 s"
    if name == "s" and "(1 << k) - 1" in line:
        return "从前 k 个二进制位全为 1 开始枚举的子集掩码 s"
    if name == "s" and "q = p - 1" in line:
        return "分解 p-1=q*2^s 时因子 2 的指数 s"
    if name == "s" and "for (int s = 0; s < n" in line:
        if "染色" in section:
            return "当前新连通分量开始二分图染色的起点 s"
        return "差分约束初始入队的顶点编号 s"
    if name == "s" and "for (int s : starts)" in line:
        return "当前独立子游戏的起始状态编号 s"
    if name == "s" and "Real s = 0" in line:
        return "多边形有向面积两倍的叉积累加值 s"
    if name == "s" and re.search(r"\bint\s+s\b", line) and "图" in section:
        return "当前图遍历采用的源点编号 s"
    if name == "rank" and "vector<int> rank" in line and "后缀数组" in section:
        return "后缀数组中每个后缀起点的字典序排名 rank"
    if name == "dd" and "Real dd = dot(d, d), t =" in line:
        return "直线方向向量 d 的长度平方 dd"
    if name == "mul" and "long long mul = 1" in line and "仿射" in section:
        return "全局仿射懒标记中作用于每个元素的乘法系数 mul"
    if name == "L" and "int L = 1, R = 0, distinct = 0" in line:
        return "普通莫队当前 1-based 窗口的左端点 L"
    if name == "R" and "int L = 1, R = 0, distinct = 0" in line:
        return "普通莫队当前 1-based 窗口的右端点 R；空窗口时 R=0"
    if name == "L" and "int L = 1, R = 0, T = 0" in line:
        return "带修改莫队当前 1-based 窗口的左端点 L"
    if name == "R" and "int L = 1, R = 0, T = 0" in line:
        return "带修改莫队当前 1-based 窗口的右端点 R；空窗口时 R=0"
    if name == "T" and "int L = 1, R = 0, T = 0" in line:
        return "带修改莫队当前已经应用的修改次数 T"
    if name == "i" and "i < a.digit.size()" in line:
        return "第一个高精度乘数 a 当前参与乘法的内部块下标 i"
    if name == "j" and "j < b.digit.size() || carry" in line:
        return "第二个高精度乘数 b 当前参与乘法的内部块下标 j"
    if name == "j" and "j < m" in line and "高斯" in section:
        return "实数高斯消元中检查剩余方程行是否全零的系数列下标 j"
    if name == "a" and "__int128 a = 1" in line:
        return "演示 __int128 算术与模乘的 128 位整数 a"
    if name == "bit" and any(token in line for token in ("<<", ">>", "LOG")):
        return f"当前处理的二进制位/倍增层 {name}"
    if name == "p" and "primes" in line:
        return "当前从质数表枚举出的质数 p"
    if name == "p" and ("p * p <= n" in line or "n % p" in line):
        return "当前试除的候选质因子 p"
    if name == "g" and "exgcd" in line:
        return "递归返回的 gcd(a,b) 值 g"
    if name == "e" and re.search(r"\bint\s+e\s*=", line) and any(
        token in section for token in ("质因数", "质因子", "分解")
    ):
        return "当前质因子 p 在原数中的指数 e"
    if name == "e" and ("Edge" in line or "g[u]" in line or "fg[u]" in line or "mg[u]" in line):
        return "当前遍历的边对象 e"
    if name == "fg":
        return "Dinic 残量网络邻接表 fg"
    if name == "mg":
        return "最小费用流残量网络邻接表 mg"
    if name in {"a", "b"} and "Edge a{" in line:
        return "正向残量边 a" if name == "a" else "配套的反向残量边 b"
    if name == "q":
        if "queue" in line or "deque" in line:
            return "当前 BFS/单调算法使用的队列 q"
    if name == "r" and "1 % mod" in line:
        return "快速幂当前累计答案 r"
    if name == "r" and "long long sum(int x)" in line:
        return "树状数组前缀查询当前累计和 r"
    if name == "f" and "__int128 x" in line:
        return "读入 __int128 时记录正负号的符号 f"
    if name == "c" and "getchar" in line:
        return "当前从输入读取的字符 c"
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
    if name == "dd" and "dot(d, d)" in line and "sqrtl(dd)" in line:
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
    if name in {"v", "to"} and any(token in line for token in ("g[u]", "Edge", "MCEdge")):
        return f"当前边的终点 {name}"
    if name == "w" and any(token in line for token in ("g[u]", "Edge", "MCEdge")):
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
    if name in CONTEXT_SENSITIVE_FALLBACK_NAMES:
        raise ValueError(
            f"cannot safely infer context-sensitive variable {name!r} "
            f"from declaration: {line.strip()}"
        )
    if name in NAME_MEANING:
        return NAME_MEANING[name]
    raise ValueError(f"cannot infer variable {name!r} from declaration: {line.strip()}")


def is_annotated(lines: list[str], index: int, names: list[str]) -> bool:
    line = lines[index]
    if "//" in line:
        return True
    if index:
        previous = lines[index - 1].strip()
        if previous.startswith("// 变量："):
            return all(re.search(rf"\b{re.escape(name)}\b", previous) for name in names)
    return False


def comment_for(
    names: list[str], line: str, section: str, indent: str, context: str = ""
) -> str:
    items = [f"{name}={meaning(name, line, section, context)}" for name in names]
    return indent + "// 变量：" + "；".join(items) + "。\n"


def generated_variable_comment(lines: list[str], index: int) -> tuple[int, str] | None:
    if not index:
        return None
    previous = lines[index - 1].strip()
    if previous.startswith("// 变量："):
        return index - 1, previous
    return None


def annotate_body(body: str, section: str, refresh: bool = False) -> tuple[str, int]:
    """Run the real variable-comment generation path on one listing body."""
    lines = body.splitlines(keepends=True)
    plain_lines = [item.rstrip("\r\n") for item in lines]
    inserted = 0
    for index in range(len(lines) - 1, -1, -1):
        names = declared_names(lines[index])
        if not names:
            continue
        existing = generated_variable_comment(plain_lines, index)
        if existing:
            if not refresh or not ambiguous_comment(existing[1]):
                continue
            indent = re.match(r"^[ \t]*", lines[index]).group(0)
            lines[existing[0]] = comment_for(names, lines[index], section, indent, body)
            inserted += 1
            continue
        if is_annotated(plain_lines, index, names):
            continue
        indent = re.match(r"^[ \t]*", lines[index]).group(0)
        lines.insert(index, comment_for(names, lines[index], section, indent, body))
        inserted += 1
    return "".join(lines), inserted


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


def annotate_file(path: Path, refresh: bool = False) -> int:
    text = path.read_text(encoding="utf-8")
    pieces: list[str] = []
    cursor = 0
    inserted = 0
    for listing in LISTING_RE.finditer(text):
        pieces.append(text[cursor:listing.start()])
        body = listing.group("body")
        section = section_before(text, listing.start())
        annotated, count = annotate_body(body, section, refresh=refresh)
        inserted += count
        pieces.extend((listing.group("open"), annotated, listing.group("close")))
        cursor = listing.end()
    pieces.append(text[cursor:])
    if inserted:
        path.write_text("".join(pieces), encoding="utf-8", newline="\n")
    return inserted


def generation_errors(refresh: bool) -> list[str]:
    errors: list[str] = []
    for path in source_files():
        text = path.read_text(encoding="utf-8")
        for listing in LISTING_RE.finditer(text):
            section = section_before(text, listing.start())
            lines = listing.group("body").splitlines()
            base_line = text[:listing.start("body")].count("\n") + 1
            for index, line in enumerate(lines):
                names = declared_names(line)
                if not names:
                    continue
                existing = generated_variable_comment(lines, index)
                needs_generation = not is_annotated(lines, index, names)
                needs_refresh = refresh and existing is not None and ambiguous_comment(existing[1])
                if not (needs_generation or needs_refresh):
                    continue
                try:
                    comment_for(
                        names,
                        line,
                        section,
                        re.match(r"^[ \t]*", line).group(0),
                        listing.group("body"),
                    )
                except ValueError as exc:
                    errors.append(f"{path.relative_to(ROOT)}:{base_line + index}: {exc}")
    return errors


def semantic_comment_issues() -> list[str]:
    issues: list[str] = []
    for path in source_files():
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if not stripped.startswith("// 变量："):
                continue
            for phrase in AMBIGUOUS_COMMENT_PHRASES:
                if phrase in stripped:
                    issues.append(
                        f"{path.relative_to(ROOT)}:{line_no}: ambiguous variable comment "
                        f"contains {phrase!r}: {stripped}"
                    )
                    break
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="insert only missing comments")
    parser.add_argument(
        "--refresh", action="store_true",
        help="replace only canonical generated comments rejected by semantic audit",
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
        print(f"{verb} variable comments: {total}")
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
    semantic_issues = semantic_comment_issues()
    print(f"semantic comment issues:         {len(semantic_issues)}")
    for issue in semantic_issues:
        print(issue)
    return bool(missing or semantic_issues)


if __name__ == "__main__":
    raise SystemExit(main())
