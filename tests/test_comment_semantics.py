import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import audit_large_interfaces as interfaces
import audit_large_variables as variables


class CommentSemanticTests(unittest.TestCase):
    def param(self, function: str, name: str, declaration: str, section: str) -> str:
        return interfaces.parameter_meaning(function, name, declaration, section)

    def regenerate_variable_comment(self, source: str, code_needle: str) -> str:
        text = (ROOT / source).read_text(encoding="utf-8")
        listings = [
            match for match in interfaces.LISTING_RE.finditer(text)
            if code_needle in match.group("body")
        ]
        self.assertEqual(len(listings), 1, (source, code_needle))
        listing = listings[0]
        lines = listing.group("body").splitlines(keepends=True)
        code_indexes = [index for index, line in enumerate(lines) if code_needle in line]
        self.assertEqual(len(code_indexes), 1, (source, code_needle))
        code_index = code_indexes[0]
        self.assertGreater(code_index, 0)
        self.assertTrue(lines[code_index - 1].strip().startswith("// 变量："))
        del lines[code_index - 1]
        section = interfaces.section_before(text, listing.start())
        regenerated, count = variables.annotate_body("".join(lines), section)
        self.assertEqual(count, 1, (source, code_needle))
        return regenerated

    def regenerate_interface_comment(self, source: str, code_needle: str) -> str:
        text = (ROOT / source).read_text(encoding="utf-8")
        listings = [
            match for match in interfaces.LISTING_RE.finditer(text)
            if code_needle in match.group("body")
        ]
        self.assertEqual(len(listings), 1, (source, code_needle))
        listing = listings[0]
        lines = listing.group("body").splitlines(keepends=True)
        code_indexes = [index for index, line in enumerate(lines) if code_needle in line]
        self.assertEqual(len(code_indexes), 1, (source, code_needle))
        code_index = code_indexes[0]
        start = code_index - 1
        if start >= 0 and lines[start].strip().startswith("// 参数："):
            start -= 1
        self.assertGreaterEqual(start, 0)
        self.assertTrue(lines[start].strip().startswith("// 接口："))
        del lines[start:code_index]
        section = interfaces.section_before(text, listing.start())
        regenerated, count = interfaces.annotate_body("".join(lines), section)
        self.assertEqual(count, 1, (source, code_needle))
        return regenerated

    def test_p_roles_are_context_specific(self):
        self.assertIn("线段树节点", self.param("apply", "p", "int p", "常见维护"))
        self.assertIn("排列", self.param("cantor", "p", "vector<int>& p", "排列序"))
        self.assertIn("多边形顶点", self.param("area2", "p", "const vector<Point>& p", "多边形"))
        self.assertIn("莫队窗口", self.param("add", "p", "int p", "莫队"))
        self.assertIn("概率", variables.meaning("p", "for (auto [v, p] : transitions[u])", "概率动态规划"))
        self.assertIn(
            "候选周期长度",
            variables.meaning("p", "for (int p = 1; p * 2 <= n; ++p) {", "SG 周期"),
        )

    def test_m_roles_cover_midpoint_bsgs_and_cycle_length(self):
        self.assertIn(
            "中点",
            variables.meaning("m", "int m = l + (r - l) / 2;", "线段树"),
        )
        self.assertIn(
            "BSGS",
            variables.meaning("m", "long long m = sqrtl(mod) + 1;", "BSGS"),
        )
        self.assertIn("置换环", variables.meaning("m", "int m = cyc.size();", "置换环"))

    def test_v_roles_cover_vertex_increment_value_and_direction(self):
        self.assertIn("顶点", self.param("add_edge", "v", "int v", "Dinic"))
        self.assertIn("增加", self.param("apply", "v", "long long v", "线段树"))
        self.assertIn(
            "单堆石子数",
            variables.meaning("v", "for (int v : piles) x ^= v;", "Nim"),
        )
        self.assertIn("方向向量", self.param("line_circle", "v", "Point v", "圆与直线"))

    def test_r_is_radius_or_interval_endpoint_from_function_context(self):
        self.assertIn("半径", self.param("circle_circle", "r", "long double r", "圆交"))
        self.assertIn("右端点", self.param("query", "r", "int r", "线段树"))

    def test_unknown_types_fail_instead_of_emitting_boilerplate(self):
        with self.assertRaisesRegex(ValueError, "unresolved"):
            self.param("mystery", "payload", "Widget payload", "未知专题")
        with self.assertRaisesRegex(ValueError, "cannot infer"):
            variables.meaning("mystery", "Widget mystery;", "未知专题")

    def test_short_names_fail_without_algorithm_specific_evidence(self):
        for name, line, section in (
            ("it", "auto it = helper();", "折半搜索（Meet-in-the-middle）"),
            ("L", "auto L = build_values();", "折半搜索（Meet-in-the-middle）"),
            ("k", "for (int k = 0; k < n; ++k)", "未知专题"),
            ("p", "int p = 0;", "未知专题"),
            ("dd", "Real dd = dot(d, d);", "圆几何"),
            ("ans", "long long ans = 1;", "未知专题"),
            ("res", "int res = 0;", "未知专题"),
            ("st", "vector<int> st;", "未知专题"),
            ("rank", "vector<int> rank(n);", "未知专题"),
            ("u", "for (int u = 1; u <= n; ++u)", "未知专题"),
            ("c", "for (int c = 0; c < 26; ++c)", "未知专题"),
        ):
            with self.subTest(name=name, line=line, section=section):
                with self.assertRaisesRegex(ValueError, "cannot safely infer"):
                    variables.meaning(name, line, section)

    def test_reviewed_cross_algorithm_examples_use_local_context(self):
        self.assertIn(
            "上界迭代器",
            variables.meaning(
                "it",
                "auto it = upper_bound(R.begin(), R.end(), limit - x);",
                "折半搜索（Meet-in-the-middle）",
            ),
        )
        mitm_line = "auto L = gen(a, 0, m), R = gen(a, m, n);"
        self.assertIn("左半部分全部子集和列表", variables.meaning("L", mitm_line, "折半搜索（Meet-in-the-middle）"))
        self.assertIn("右半部分全部子集和列表", variables.meaning("R", mitm_line, "折半搜索（Meet-in-the-middle）"))
        self.assertIn(
            "路径中转点",
            variables.meaning(
                "k",
                "for (int k = 0; k &lt; n; ++k)",
                "bitset 优化传递闭包",
            ),
        )

    def test_deleted_formal_comments_regenerate_with_exact_roles(self):
        cases = (
            (
                "remake/large/02_基础.tex",
                "auto L = gen(a, 0, n / 2, limit), R = gen(a, n / 2, n, limit);",
                ("左半部分全部子集和列表 L", "右半部分全部子集和列表 R"),
            ),
            (
                "remake/large/02_基础.tex",
                "auto it = upper_bound(R.begin(), R.end(), limit - x);",
                ("容器 R 中二分查找得到的上界迭代器 it",),
            ),
            (
                "remake/large/02_基础.tex",
                "for (int k = 0; k < n; ++k)",
                ("路径中转点的顶点编号 k",),
            ),
            (
                "remake/large/03_数学_详解.tex",
                "int p = row;",
                ("主元行 p",),
            ),
            (
                "remake/large/02_基础.tex",
                "int m = l + (r - l) / 2;",
                ("递归区间 [l,r] 的中点 m",),
            ),
            (
                "remake/large/05_字符串.tex",
                "int &v = ch[u][c];",
                ("自动机状态 u 经字符 c 转移到的状态引用 v",),
            ),
            (
                "remake/large/04_数据结构.tex",
                "long long sum(int x) const { long long r = 0;",
                ("树状数组前缀 [1,x] 的累计和 r",),
            ),
            (
                "remake/large/10_几何.tex",
                "Real dd = dot(d, d), t = dot(c.o - a, d) / dd;",
                ("直线方向向量 d 的长度平方 dd", "投影参数 t"),
            ),
        )
        for source, code_needle, required_parts in cases:
            with self.subTest(source=source, code=code_needle):
                regenerated = self.regenerate_variable_comment(source, code_needle)
                for required in required_parts:
                    self.assertIn(required, regenerated)

    def test_fifth_review_variable_comments_regenerate_with_exact_roles(self):
        cases = (
            ("remake/large/02_基础.tex", "int old = (int)res.size();", ("生成新子集和之前", "已有的元素数量 old")),
            ("remake/large/05_字符串_详解.tex", "vector<int> sa(n), rk(n), tmp(n);", ("当前倍增长度", "长度 2k", "新等价类排名数组 tmp")),
            ("remake/large/05_字符串_详解.tex", "for (int k = 1;; k <<= 1)", ("每一段的长度 k", "长度 2k")),
            ("remake/large/05_字符串_详解.tex", "bool diff = rk[a] != rk[b];", ("第一段长度 k 排名",)),
            ("remake/large/05_字符串_详解.tex", "int ra = a+k < n ? rk[a+k] : -1;", ("第二段的排名 ra", "越界时为 -1")),
            ("remake/large/05_字符串_详解.tex", "int rb = b+k < n ? rk[b+k] : -1;", ("第二段的排名 rb", "越界时为 -1")),
            ("remake/large/05_字符串.tex", "int ri = i + k < n ? r[i + k] : -1;", ("偏移 k 后第二段的等价类排名 ri", "越界时为 -1")),
            ("remake/large/05_字符串.tex", "int rj = j + k < n ? r[j + k] : -1;", ("偏移 k 后第二段的等价类排名 rj", "越界时为 -1")),
            ("remake/large/05_字符串_详解.tex", "int ri = i + k < n ? rk[i+k] : -1;", ("偏移 k 后第二段的等价类排名 ri", "越界时为 -1")),
            ("remake/large/05_字符串_详解.tex", "int rj = j + k < n ? rk[j+k] : -1;", ("偏移 k 后第二段的等价类排名 rj", "越界时为 -1")),
            ("remake/large/08_动态规划_详解.tex", "int up = tight ? digit[pos] : 9;", ("tight 为真时取 digit[pos]", "否则为 9")),
            ("remake/large/08_动态规划_详解.tex", "int nst = ns ? go[st][d] : 0;", ("自动机状态 st", "仍为前导零时保持起点 0")),
            ("remake/large/09_博弈_详解.tex", "unsigned long long all = 0;", ("全部石子堆大小的异或和 all",)),
            ("remake/large/06_图论.tex", "int f = t[x].fa;", ("辅助 splay 树父节点编号 f",)),
            ("remake/large/04_数据结构_详解.tex", "int f = query(root, 1, n, x);", ("版本 root", "元素 x 当前父节点编号 f")),
        )
        for source, code_needle, required_parts in cases:
            with self.subTest(source=source, code=code_needle):
                regenerated = self.regenerate_variable_comment(source, code_needle)
                for required in required_parts:
                    self.assertIn(required, regenerated)

    def test_fifth_review_interfaces_regenerate_with_exact_contracts(self):
        cases = (
            (
                "remake/large/04_数据结构_详解.tex",
                "void apply(int p, int l, int r, long long mul, long long add)",
                ("x->mul*x+add", "新操作在外", "乘法系数 mul", "加法常数 add"),
            ),
            (
                "remake/large/04_数据结构_详解.tex",
                "int find_root(int root, int x)",
                ("版本 root 中只读地沿父指针", "版本根 root", "元素编号 x"),
            ),
            (
                "remake/large/04_数据结构_详解.tex",
                "int merge_version(int root, int x, int y)",
                ("从版本 root", "x 根的父指针改为 y 根", "返回新版本根"),
            ),
        )
        for source, code_needle, required_parts in cases:
            with self.subTest(source=source, code=code_needle):
                regenerated = self.regenerate_interface_comment(source, code_needle)
                for required in required_parts:
                    self.assertIn(required, regenerated)

    def test_unknown_function_purpose_fails_instead_of_using_section_boilerplate(self):
        with self.assertRaisesRegex(ValueError, "cannot safely infer function purpose"):
            interfaces.function_purpose("mystery", "Widget mystery(int x) {", "未知专题")
        with self.assertRaisesRegex(ValueError, "context-sensitive function purpose"):
            interfaces.function_purpose("apply", "void apply(Widget payload) {", "未知专题")

    def test_refresh_replaces_only_rejected_canonical_block(self):
        bad = (
            "// 接口：cantor(p)：返回排列 p 的 0-based Cantor 排名；返回类型 int。\n"
            "// 参数：当前节点/模数 p（见本节定义）。\n"
            "int cantor(vector<int>& p) { return 0; }\n"
        )
        refreshed, count = interfaces.annotate_body(bad, "排列序", refresh=True)
        self.assertEqual(count, 1)
        self.assertIn("0-based 排列 p", refreshed)
        reviewed = bad.replace("当前节点/模数 p（见本节定义）", "待计算排名的 0-based 排列 p")
        preserved, count = interfaces.annotate_body(reviewed, "排列序", refresh=True)
        self.assertEqual(count, 0)
        self.assertEqual(preserved, reviewed)

    def test_comment_dictionaries_have_no_duplicate_literal_keys(self):
        self.assertEqual(interfaces.duplicate_dict_key_issues(), [])

    def test_formal_sources_close_reviewed_high_risk_contexts(self):
        texts = {
            path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8")
            for path in interfaces.source_files()
        }
        cases = (
            ("banzi/板子_大版本.tex", "count_if(a.begin()", "当前被 count_if 判断的数组元素 v"),
            ("banzi/板子_大版本.tex", "void dfs2(int n)", "枚举已排序 nums 的所有不重复全排列"),
            ("banzi/板子_大版本.tex", "string randstr(int len)", "由 randstr 返回的随机小写字符串 s"),
            ("remake/large/06_图论.tex", "pair<bool, long long> prim(", "加权无向图邻接表 g"),
            ("remake/large/03_数学.tex", "vector<int> prufer_encode", "标号树的无向邻接表 g"),
            ("remake/large/10_几何.tex", "long double diameter2", "对踵点下标 j"),
            ("remake/large/10_几何.tex", "long double closest(vector<Point>& p", "半开区间 [l,r)"),
            ("remake/large/10_几何_详解.tex", "long double closest(int l, int r)", "靠近中线"),
            ("remake/large/10_几何_详解.tex", "vector<Point> line_circle", "常数项 C"),
            ("remake/large/10_几何_详解.tex", "void pull(int p, int l, int r)", "实际覆盖长度"),
            ("remake/large/10_几何_详解.tex", "void modify(int p, int l, int r", "覆盖计数增量 d"),
            ("remake/large/10_几何.tex", "sort(h.begin(), h.end()", "按半平面边界方向角从小到大排序"),
            ("banzi/板子_大版本.tex", "int lb = s & (-s);", "Gosper 枚举中当前掩码 s 的最低位 1"),
            ("remake/large/03_数学.tex", "void ntt(vector<int>& a", "当前蝶形位置使用的单位根幂 w"),
            ("remake/large/05_字符串_详解.tex", "for (char cc : text)", "送入 AC 自动机的字符 cc"),
            ("remake/large/06_图论.tex", "void build(int n_, vector<Edge> edges)", "Kruskal 重构森林根"),
            ("remake/large/09_博弈_详解.tex", "unsigned long long target = a[i] ^ all;", "第 i 堆应剩余的石子数 target"),
        )
        for source, code_needle, required in cases:
            with self.subTest(source=source, code=code_needle):
                bodies = [
                    match.group("body")
                    for match in interfaces.LISTING_RE.finditer(texts[source])
                    if code_needle in match.group("body")
                ]
                self.assertEqual(len(bodies), 1)
                self.assertIn(required, bodies[0])

    def test_formal_sources_reject_cross_chapter_escape_phrases(self):
        rendered = "\n".join(
            path.read_text(encoding="utf-8") for path in interfaces.source_files()
        )
        for phrase in (
            "返回值含义见调用处条件",
            "回调函数的左操作数",
            "回调函数的右操作数",
            "图的邻接表/生成树拉普拉斯矩阵",
            "节点 p/u",
            "当前查询对象 q",
            "当前组合数查询函数/结果矩阵",
            "当前判别式/距离量",
            "矩阵/几何量",
            "下标或顶点数量",
            "给定位置/区间",
            "仿射乘数/矩阵乘积",
            "左边界/左半部分",
            "右边界/右半部分",
            "本次写入或增加的数值 v",
            "当前累计答案 ans",
            "内层循环下标 j",
            "当前循环下标 i",
            "返回 true 表示上述接口描述成立",
            "本节核心逻辑",
        ):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, rendered)

    def test_source_level_semantic_contracts_are_clean(self):
        self.assertEqual(interfaces.source_comment_expectation_issues(), [])

    def test_formal_sources_have_no_unresolved_operand_placeholders(self):
        rendered = "\n".join(
            path.read_text(encoding="utf-8") for path in interfaces.source_files()
        )
        self.assertNotIn("左操作数", rendered)
        self.assertNotIn("右操作数", rendered)
        self.assertIn("第一个待合并元素编号 a", rendered)
        self.assertIn("第二个待合并元素编号 b", rendered)


if __name__ == "__main__":
    unittest.main()
