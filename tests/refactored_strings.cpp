#include <bits/stdc++.h>
#include <cassert>
using namespace std;

#define int long long
using i64 = long long;

// 接口：返回 pattern 在 text 中所有 0-based 起点，允许重叠；pattern 必须非空。
vector<int> kmp_find(const string &text, const string &pattern) {
    vector<int> pi(pattern.size()), answer;
    for (int i = 1; i < (int)pattern.size(); ++i) {
        int j = pi[i - 1];
        while (j && pattern[i] != pattern[j]) j = pi[j - 1];
        if (pattern[i] == pattern[j]) ++j;
        pi[i] = j;
    }
    for (int i = 0, j = 0; i < (int)text.size(); ++i) {
        while (j && text[i] != pattern[j]) j = pi[j - 1];
        if (text[i] == pattern[j]) ++j;
        if (j == (int)pattern.size()) {
            answer.push_back(i - j + 1);
            j = pi[j - 1];
        }
    }
    return answer;
}

// 接口：z[i] 是 s 与 s[i..] 的最长公共前缀长度；z[0]=|s|。
vector<int> z_function(const string &s) {
    int n = s.size();
    vector<int> z(n);
    if (n) z[0] = n;
    for (int i = 1, l = 0, r = 0; i < n; ++i) {
        if (i <= r) z[i] = min(r - i + 1, z[i - l]);
        while (i + z[i] < n && s[z[i]] == s[i + z[i]]) ++z[i];
        if (i + z[i] - 1 > r) l = i, r = i + z[i] - 1;
    }
    return z;
}

// 接口：返回字符串最长回文子串长度；空串返回 0。
int manacher_longest(const string &s) {
    string t = "^";
    for (char c : s) t += '#', t += c;
    t += "#$";
    vector<int> p(t.size());
    int center = 0, right = 0, answer = 0;
    for (int i = 1; i + 1 < (int)t.size(); ++i) {
        if (i < right) p[i] = min(right - i, p[2 * center - i]);
        while (t[i + p[i] + 1] == t[i - p[i] - 1]) ++p[i];
        if (i + p[i] > right) center = i, right = i + p[i];
        answer = max(answer, p[i]);
    }
    return answer;
}

// 接口：返回字典序最小循环表示的 0-based 起点；空串返回 0。
int booth(const string &s) {
    int n = s.size();
    if (!n) return 0;
    string t = s + s;
    int i = 0, j = 1, k = 0;
    while (i < n && j < n && k < n) {
        if (t[i + k] == t[j + k]) {
            ++k;
            continue;
        }
        if (t[i + k] > t[j + k]) i = i + k + 1;
        else j = j + k + 1;
        if (i == j) ++j;
        k = 0;
    }
    return min(i, j);
}

struct AC {
    vector<array<int, 26>> go;
    vector<int> fail, terminal, output;

    // 接口：init -> insert 所有模式串 -> build -> query_total；
    // 逐模式计数还需对 fail 树做一次反向汇总。
    AC() { init(); }
    void init() {
        go.clear(); fail.clear(); terminal.clear(); output.clear();
        go.push_back({}); go[0].fill(0);
        fail.push_back(0); terminal.push_back(0); output.push_back(0);
    }
    int insert(const string &s) {
        int u = 0;
        for (char ch : s) {
            int c = ch - 'a';
            if (!go[u][c]) {
                go[u][c] = go.size();
                go.push_back({}); go.back().fill(0);
                fail.push_back(0); terminal.push_back(0); output.push_back(0);
            }
            u = go[u][c];
        }
        ++terminal[u];
        return u;
    }
    void build() {
        queue<int> q;
        for (int c = 0; c < 26; ++c) if (go[0][c]) q.push(go[0][c]);
        while (!q.empty()) {
            int u = q.front(); q.pop();
            output[u] = terminal[u] + output[fail[u]];
            for (int c = 0; c < 26; ++c) {
                int &v = go[u][c];
                if (v) fail[v] = go[fail[u]][c], q.push(v);
                else v = go[fail[u]][c];
            }
        }
        output[0] = terminal[0];
    }
    int query_total(const string &text) const {
        int u = 0, ans = 0;
        for (char ch : text) u = go[u][ch - 'a'], ans += output[u];
        return ans;
    }
};

vector<int> count_each_pattern(const AC &ac, const string &text,
                               const vector<int> &pattern_node) {
    vector<int> pass(ac.go.size(), 0), order;
    int u = 0;
    for (char ch : text) ++pass[u = ac.go[u][ch - 'a']];

    vector<vector<int>> fail_tree(ac.go.size());
    for (int v = 1; v < (int)ac.go.size(); ++v)
        fail_tree[ac.fail[v]].push_back(v);
    vector<int> st = {0};
    while (!st.empty()) {
        int x = st.back(); st.pop_back();
        order.push_back(x);
        for (int v : fail_tree[x]) st.push_back(v);
    }
    reverse(order.begin(), order.end());
    for (int x : order) if (x) pass[ac.fail[x]] += pass[x];

    vector<int> answer;
    for (int node : pattern_node) answer.push_back(pass[node]);
    return answer;
}

struct SAM {
    struct Node {
        array<int, 26> go{};
        int link = 0, len = 0, occ = 0;
    };
    vector<Node> st;
    int last = 1;

    // 接口：init(原串长度) 后逐字符 extend；统计出现次数前调用 count_occurrence。
    void init(int n) {
        st.assign(2 * n + 5, Node{});
        st.resize(2);
        last = 1;
    }
    void extend(int c) {
        int cur = st.size();
        st.push_back(Node{});
        st[cur].len = st[last].len + 1;
        st[cur].occ = 1;
        int p = last;
        while (p && !st[p].go[c]) st[p].go[c] = cur, p = st[p].link;
        if (!p) st[cur].link = 1;
        else {
            int q = st[p].go[c];
            if (st[p].len + 1 == st[q].len) st[cur].link = q;
            else {
                int clone = st.size();
                st.push_back(st[q]);
                st[clone].len = st[p].len + 1;
                st[clone].occ = 0;
                while (p && st[p].go[c] == q)
                    st[p].go[c] = clone, p = st[p].link;
                st[q].link = st[cur].link = clone;
            }
        }
        last = cur;
    }
    void count_occurrence() {
        vector<int> ord(st.size() - 1);
        iota(ord.begin(), ord.end(), 1);
        sort(ord.begin(), ord.end(),
             [&](int a, int b) { return st[a].len > st[b].len; });
        for (int u : ord) if (st[u].link) st[st[u].link].occ += st[u].occ;
    }
    int max_repeat_product() const {
        int ans = 0;
        for (int u = 2; u < (int)st.size(); ++u)
            ans = max(ans, st[u].len * st[u].occ);
        return ans;
    }
};

struct PAM {
    struct Node {
        array<int, 26> go{};
        int fail = 0, len = 0, occ = 0;
    };
    vector<Node> tr;
    vector<int> text;
    int last = 1, n = 0;

    // 接口：init(max_len) 后逐字符 add；不同回文数为 tr.size()-2。
    void init(int max_len) {
        tr.clear(); tr.reserve(max_len + 2);
        text.clear(); text.reserve(max_len);
        tr.push_back(Node{}); tr.push_back(Node{});
        tr[0].len = -1; tr[1].len = 0;
        last = 1; n = 0;
    }
    int get_fail(int u) const {
        while (n - 1 - tr[u].len < 0 ||
               text[n - 1 - tr[u].len] != text[n])
            u = tr[u].fail;
        return u;
    }
    int add(char ch) {
        int c = ch - 'a';
        text.push_back(c);
        int cur = get_fail(last);
        if (!tr[cur].go[c]) {
            int now = tr[cur].go[c] = tr.size();
            tr.push_back(Node{});
            tr[now].len = tr[cur].len + 2;
            tr[now].fail = tr[now].len == 1
                ? 1 : tr[get_fail(tr[cur].fail)].go[c];
        }
        last = tr[cur].go[c];
        ++tr[last].occ; ++n;
        return last;
    }
    void count_occurrence() {
        vector<int> ord(tr.size() - 2);
        iota(ord.begin(), ord.end(), 2);
        sort(ord.begin(), ord.end(),
             [&](int a, int b) { return tr[a].len > tr[b].len; });
        for (int u : ord) tr[tr[u].fail].occ += tr[u].occ;
    }
};

// 接口：返回后缀起点的字典序排列；空串返回空数组。
vector<int> suffix_array(const string &s) {
    int n = s.size();
    if (!n) return {};
    vector<int> sa(n), rk(n), tmp(n);
    iota(sa.begin(), sa.end(), 0);
    for (int i = 0; i < n; ++i) rk[i] = s[i];
    for (int k = 1;; k <<= 1) {
        sort(sa.begin(), sa.end(), [&](int i, int j) {
            if (rk[i] != rk[j]) return rk[i] < rk[j];
            int ri = i + k < n ? rk[i + k] : -1;
            int rj = j + k < n ? rk[j + k] : -1;
            return ri < rj;
        });
        tmp[sa[0]] = 0;
        for (int i = 1; i < n; ++i) {
            int a = sa[i - 1], b = sa[i];
            int a2 = a + k < n ? rk[a + k] : -1;
            int b2 = b + k < n ? rk[b + k] : -1;
            tmp[b] = tmp[a] + (rk[a] != rk[b] || a2 != b2);
        }
        rk.swap(tmp);
        if (rk[sa.back()] == n - 1) break;
    }
    return sa;
}

// 接口：sa 已按 suffix_array 排序；lcp[i] 是 sa[i] 与 sa[i-1] 的 LCP。
vector<int> kasai_lcp(const string &s, const vector<int> &sa) {
    int n = s.size();
    vector<int> rank(n), lcp(n);
    for (int i = 0; i < n; ++i) rank[sa[i]] = i;
    int h = 0;
    for (int i = 0; i < n; ++i) {
        int r = rank[i];
        if (!r) continue;
        int j = sa[r - 1];
        while (i + h < n && j + h < n && s[i + h] == s[j + h]) ++h;
        lcp[r] = h;
        if (h) --h;
    }
    return lcp;
}

signed main() {
    assert(kmp_find("aaaaa", "aaa") == vector<int>({0, 1, 2}));
    assert(kmp_find("abc", "d").empty());
    assert(z_function("aaaa") == vector<int>({4, 3, 2, 1}));
    assert(manacher_longest("abacaba") == 7);
    assert(manacher_longest("") == 0);
    assert(booth("baca") == 3); // "abac"

    AC ac;
    vector<int> nodes;
    nodes.push_back(ac.insert("a"));
    nodes.push_back(ac.insert("ab"));
    nodes.push_back(ac.insert("bab"));
    ac.build();
    assert(ac.query_total("abab") == 5);
    assert(count_each_pattern(ac, "abab", nodes) == vector<int>({2, 2, 1}));

    SAM sam;
    string s = "ababa";
    sam.init(s.size());
    for (char c : s) sam.extend(c - 'a');
    sam.count_occurrence();
    assert(sam.max_repeat_product() == 6);

    PAM pam;
    pam.init(7);
    for (char c : string("abacaba")) pam.add(c);
    assert((int)pam.tr.size() - 2 == 7);

    auto sa = suffix_array("banana");
    assert(sa == vector<int>({5, 3, 1, 0, 4, 2}));
    assert(kasai_lcp("banana", sa) == vector<int>({0, 1, 3, 0, 0, 2}));
    cout << "refactored string templates: OK\n";
    return 0;
}
