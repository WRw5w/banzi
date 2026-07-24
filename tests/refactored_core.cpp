#include <bits/stdc++.h>
#include <cassert>
using namespace std;

// 这些测试使用“题目接口”调用模板，而不是只检查某个中间数组。
// 每个函数都对应大版本中的一类板子；边界测试覆盖空输入、单点、重复值和负更新。

// 接口：返回子集和不超过 limit 的最大值；a 可为空，元素默认非负。
long long subset_best(const vector<long long> &a, long long limit) {
    int n = a.size(), mid = n / 2;
    auto gen = [&](int l, int r) {
        vector<long long> sums{0};
        for (int i = l; i < r; ++i) {
            int old = sums.size();
            for (int j = 0; j < old; ++j) sums.push_back(sums[j] + a[i]);
        }
        return sums;
    };
    auto left = gen(0, mid), right = gen(mid, n);
    sort(right.begin(), right.end());
    long long ans = 0;
    for (long long x : left) {
        auto it = upper_bound(right.begin(), right.end(), limit - x);
        if (it != right.begin()) ans = max(ans, x + *prev(it));
    }
    return ans;
}

// 接口：a[1..n] 执行闭区间加；返回恢复差分后的 0-based 数组。
// 清空：每组重新创建 diff，不能复用上一组的端点标记。
vector<long long> range_add(vector<long long> a,
                            const vector<tuple<int, int, long long>> &ops) {
    vector<long long> diff(a.size() + 1);
    for (auto [l, r, v] : ops) diff[l] += v, diff[r + 1] -= v;
    long long cur = 0;
    for (int i = 1; i < (int)a.size(); ++i) {
        cur += diff[i];
        a[i] += cur;
    }
    a.erase(a.begin());
    return a;
}

// 接口：有序数组中第一个 >= x 的 0-based 位置；不存在返回 -1。
int first_at_least(const vector<long long> &a, long long x) {
    int l = 0, r = a.size();
    while (l < r) {
        int m = l + (r - l) / 2;
        if (a[m] < x) l = m + 1;
        else r = m;
    }
    return l == (int)a.size() ? -1 : l;
}

// 接口：正数数组至多分 k 段，返回最小化后的最大段和。
long long min_max_segment_sum(const vector<long long> &a, int k) {
    auto check = [&](long long lim) {
        int groups = 1;
        long long sum = 0;
        for (auto x : a) {
            if (x > lim) return false;
            if (sum + x > lim) sum = x, ++groups;
            else sum += x;
        }
        return groups <= k;
    };
    long long l = *max_element(a.begin(), a.end());
    long long r = accumulate(a.begin(), a.end(), 0LL);
    while (l < r) {
        long long m = l + (r - l) / 2;
        if (check(m)) r = m;
        else l = m + 1;
    }
    return l;
}

// 接口：返回至多含 k 种字符的最长连续子串长度；窗口只适用于本题单调条件。
int longest_distinct(const string &s, int k) {
    vector<int> cnt(256);
    int distinct = 0, left = 0, ans = 0;
    for (int right = 0; right < (int)s.size(); ++right) {
        if (cnt[(unsigned char)s[right]]++ == 0) ++distinct;
        while (distinct > k)
            if (--cnt[(unsigned char)s[left++]] == 0) --distinct;
        ans = max(ans, right - left + 1);
    }
    return ans;
}

// 接口：返回每个位置右侧第一个严格更大元素下标；没有则为 -1。
vector<int> next_greater(const vector<long long> &a) {
    vector<int> ans(a.size(), -1), st;
    for (int i = 0; i < (int)a.size(); ++i) {
        while (!st.empty() && a[st.back()] < a[i])
            ans[st.back()] = i, st.pop_back();
        st.push_back(i);
    }
    return ans;
}

// 接口：返回所有长度为 k 的窗口最大值；k 必须在 [1,n]。
vector<long long> sliding_max(const vector<long long> &a, int k) {
    deque<int> q;
    vector<long long> ans;
    for (int i = 0; i < (int)a.size(); ++i) {
        while (!q.empty() && q.front() <= i - k) q.pop_front();
        while (!q.empty() && a[q.back()] <= a[i]) q.pop_back();
        q.push_back(i);
        if (i >= k - 1) ans.push_back(a[q.front()]);
    }
    return ans;
}

// 接口：计算 a^e mod mod；e 非负且 mod 为正。
long long mod_pow(long long a, long long e, long long mod) {
    long long ans = 1 % mod;
    for (; e; e >>= 1, a = a * a % mod)
        if (e & 1) ans = ans * a % mod;
    return ans;
}

// 接口：返回 gcd(a,b)，并写回 ax+by=gcd(a,b)。
long long exgcd(long long a, long long b, long long &x, long long &y) {
    if (!b) return x = 1, y = 0, a;
    long long xx, yy, g = exgcd(b, a % b, xx, yy);
    return x = yy, y = xx - a / b * yy, g;
}

// 接口：返回 1..n 中与 n 互质的整数个数；phi(1)=1。
long long phi(long long n) {
    long long ans = n;
    for (long long p = 2; p * p <= n; ++p) {
        if (n % p) continue;
        while (n % p == 0) n /= p;
        ans = ans / p * (p - 1);
    }
    return n > 1 ? ans / n * (n - 1) : ans;
}

// 接口：返回不超过 n 的素数；n<2 时返回空数组。
vector<int> linear_sieve(int n) {
    vector<int> primes, lp(n + 1);
    for (int i = 2; i <= n; ++i) {
        if (!lp[i]) lp[i] = i, primes.push_back(i);
        for (int p : primes) {
            if (p > lp[i] || i * p > n) break;
            lp[i * p] = p;
        }
    }
    return primes;
}

// 对应大版本接口：同时验证 primes/lp/phi/mu 的含义、下标和重复调用清空。
void linear_sieve_phi_mu(int upper, vector<int>& primes,
                         vector<int>& lp, vector<int>& phi,
                         vector<int>& mu) {
    primes.clear();
    lp.assign(upper + 1, 0);
    phi.assign(upper + 1, 0);
    mu.assign(upper + 1, 0);
    if (upper >= 1) phi[1] = mu[1] = 1;
    for (int i = 2; i <= upper; ++i) {
        if (!lp[i]) {
            lp[i] = i;
            primes.push_back(i);
            phi[i] = i - 1;
            mu[i] = -1;
        }
        for (int p : primes) {
            if (1LL * i * p > upper) break;
            lp[i * p] = p;
            if (p == lp[i]) {
                phi[i * p] = phi[i] * p;
                mu[i * p] = 0;
                break;
            }
            phi[i * p] = phi[i] * (p - 1);
            mu[i * p] = -mu[i];
        }
    }
}

struct DSU {
    vector<int> p, sz;
    explicit DSU(int n) : p(n + 1), sz(n + 1, 1) {
        iota(p.begin(), p.end(), 0);
    }
    int find(int x) { return p[x] == x ? x : p[x] = find(p[x]); }
    // 接口：合并成功返回 true；重复合并返回 false。
    bool unite(int x, int y) {
        x = find(x); y = find(y);
        if (x == y) return false;
        if (sz[x] < sz[y]) swap(x, y);
        p[y] = x; sz[x] += sz[y];
        return true;
    }
};

class Fenwick {
    vector<long long> bit;
public:
    // 接口：1-based 单点加、前缀和；range_sum(l,r) 为闭区间。
    explicit Fenwick(int n) : bit(n + 1) {}
    void add(int x, long long v) {
        for (; x < (int)bit.size(); x += x & -x) bit[x] += v;
    }
    long long sum(int x) const {
        long long ans = 0;
        for (; x; x -= x & -x) ans += bit[x];
        return ans;
    }
    long long range_sum(int l, int r) const { return sum(r) - sum(l - 1); }
};

struct SparseTable {
    vector<vector<long long>> st;
    vector<int> lg;
    explicit SparseTable(const vector<long long> &a) {
        int n = a.size();
        lg.assign(n + 1, 0);
        for (int i = 2; i <= n; ++i) lg[i] = lg[i / 2] + 1;
        st.assign(lg[n] + 1, vector<long long>(n));
        st[0] = a;
        for (int j = 1; j < (int)st.size(); ++j)
            for (int i = 0; i + (1 << j) <= n; ++i)
                st[j][i] = min(st[j - 1][i],
                               st[j - 1][i + (1 << (j - 1))]);
    }
    // 接口：静态数组 0-based 闭区间最小值；不支持更新和区间和。
    long long query(int l, int r) const {
        int k = lg[r - l + 1];
        return min(st[k][l], st[k][r - (1 << k) + 1]);
    }
};

struct SegmentTree {
    int n;
    vector<long long> tr, lazy;
    // 接口：构造 a[1..n]；add/query 都是闭区间，懒标记由对象维护。
    explicit SegmentTree(const vector<long long> &a)
        : n(a.size() - 1), tr(4 * a.size()), lazy(4 * a.size()) {
        build(1, 1, n, a);
    }
    void build(int p, int l, int r, const vector<long long> &a) {
        if (l == r) return void(tr[p] = a[l]);
        int m = (l + r) / 2;
        build(p * 2, l, m, a);
        build(p * 2 + 1, m + 1, r, a);
        tr[p] = tr[p * 2] + tr[p * 2 + 1];
    }
    void apply(int p, int l, int r, long long v) {
        tr[p] += v * (r - l + 1);
        lazy[p] += v;
    }
    void push(int p, int l, int r) {
        if (!lazy[p] || l == r) return;
        int m = (l + r) / 2;
        apply(p * 2, l, m, lazy[p]);
        apply(p * 2 + 1, m + 1, r, lazy[p]);
        lazy[p] = 0;
    }
    void add(int ql, int qr, long long v, int p, int l, int r) {
        if (ql <= l && r <= qr) return apply(p, l, r, v);
        push(p, l, r);
        int m = (l + r) / 2;
        if (ql <= m) add(ql, qr, v, p * 2, l, m);
        if (qr > m) add(ql, qr, v, p * 2 + 1, m + 1, r);
        tr[p] = tr[p * 2] + tr[p * 2 + 1];
    }
    long long query(int ql, int qr, int p, int l, int r) {
        if (ql <= l && r <= qr) return tr[p];
        push(p, l, r);
        int m = (l + r) / 2;
        long long ans = 0;
        if (ql <= m) ans += query(ql, qr, p * 2, l, m);
        if (qr > m) ans += query(ql, qr, p * 2 + 1, m + 1, r);
        return ans;
    }
    void add(int l, int r, long long v) { add(l, r, v, 1, 1, n); }
    long long query(int l, int r) { return query(l, r, 1, 1, n); }
};

struct BinaryTrie {
    struct Node { int ch[2]{}; };
    vector<Node> tr{{}};
    // 接口：插入非负整数，max_xor(x) 返回与已插入数的最大异或值。
    void insert(int x) {
        int u = 0;
        for (int b = 30; b >= 0; --b) {
            int c = (x >> b) & 1;
            if (!tr[u].ch[c]) tr[u].ch[c] = tr.size(), tr.push_back({});
            u = tr[u].ch[c];
        }
    }
    int max_xor(int x) const {
        int u = 0, ans = 0;
        for (int b = 30; b >= 0; --b) {
            int c = (x >> b) & 1;
            if (tr[u].ch[c ^ 1]) ans |= 1 << b, u = tr[u].ch[c ^ 1];
            else u = tr[u].ch[c];
        }
        return ans;
    }
};

struct RollbackDSU {
    vector<int> p, sz;
    vector<pair<int, int>> hist;
    explicit RollbackDSU(int n) : p(n + 1), sz(n + 1, 1) {
        iota(p.begin(), p.end(), 0);
    }
    int find(int x) const {
        while (p[x] != x) x = p[x];
        return x;
    }
    // 接口：snapshot 后可 rollback；不做路径压缩，否则无法恢复父指针。
    int snapshot() const { return hist.size(); }
    bool unite(int x, int y) {
        x = find(x); y = find(y);
        if (x == y) return hist.push_back({-1, -1}), false;
        if (sz[x] < sz[y]) swap(x, y);
        hist.push_back({y, sz[x]});
        p[y] = x; sz[x] += sz[y];
        return true;
    }
    void rollback(int snap) {
        while ((int)hist.size() > snap) {
            auto [y, old_size] = hist.back();
            hist.pop_back();
            if (y == -1) continue;
            int x = p[y];
            sz[x] = old_size;
            p[y] = y;
        }
    }
};

// 接口：返回严格递增子序列长度；lower_bound 不能替换成 upper_bound。
int lis_length(const vector<long long> &a) {
    vector<long long> d;
    for (auto x : a) {
        auto it = lower_bound(d.begin(), d.end(), x);
        if (it == d.end()) d.push_back(x);
        else *it = x;
    }
    return d.size();
}

int main() {
    assert(subset_best({}, 0) == 0);
    assert(subset_best({3, 5, 6}, 8) == 8);
    assert(range_add(vector<long long>{0, 1, 2, 3, 4},
                     {{2, 3, 5}, {1, 4, -1}}) ==
           vector<long long>({0, 6, 7, 3}));
    assert(first_at_least({1, 3, 5}, 4) == 2);
    assert(first_at_least({1, 3, 5}, 6) == -1);
    assert(min_max_segment_sum({7, 2, 5, 10}, 2) == 14);
    assert(longest_distinct("abcba", 3) == 5);
    assert((next_greater({2, 1, 3}) == vector<int>{2, 2, -1}));
    assert((sliding_max({1, 3, -1, 2, 5}, 3) ==
            vector<long long>{3, 3, 5}));

    assert(mod_pow(2, 10, 1000) == 24);
    long long x, y;
    assert(exgcd(30, 18, x, y) == 6 && 30 * x + 18 * y == 6);
    assert(phi(1) == 1 && phi(36) == 12);
    assert((linear_sieve(10) == vector<int>{2, 3, 5, 7}));
    vector<int> primes, lp, phis, mu;
    linear_sieve_phi_mu(10, primes, lp, phis, mu);
    assert((primes == vector<int>{2, 3, 5, 7}));
    assert((vector<int>(lp.begin() + 1, lp.end()) ==
            vector<int>{0, 2, 3, 2, 5, 2, 7, 2, 3, 2}));
    assert((vector<int>(phis.begin() + 1, phis.end()) ==
            vector<int>{1, 1, 2, 2, 4, 2, 6, 4, 6, 4}));
    assert((vector<int>(mu.begin() + 1, mu.end()) ==
            vector<int>{1, -1, -1, 0, -1, 1, -1, 0, 0, 1}));
    linear_sieve_phi_mu(1, primes, lp, phis, mu);
    assert(primes.empty() && lp.size() == 2 && phis[1] == 1 && mu[1] == 1);

    DSU plain_dsu(3);
    assert(plain_dsu.unite(1, 2));
    assert(!plain_dsu.unite(1, 2));
    assert(plain_dsu.find(1) != plain_dsu.find(3));
    Fenwick bit(4);
    for (int i = 1; i <= 4; ++i) bit.add(i, i);
    assert(bit.range_sum(2, 3) == 5);
    SparseTable sparse({3, 1, 2, 1});
    assert(sparse.query(0, 3) == 1 && sparse.query(2, 2) == 2);
    SegmentTree seg({0, 1, 2, 3, 4});
    seg.add(2, 3, 5);
    assert(seg.query(1, 4) == 20 && seg.query(2, 3) == 15);
    BinaryTrie trie;
    for (int x : {1, 2, 4}) trie.insert(x);
    assert(trie.max_xor(3) == 7);

    RollbackDSU dsu(3);
    int snap = dsu.snapshot();
    dsu.unite(1, 2);
    assert(dsu.find(1) == dsu.find(2));
    dsu.rollback(snap);
    assert(dsu.find(1) != dsu.find(2));
    assert(lis_length({3, 1, 2, 5, 4}) == 3);
    cout << "core templates: PASS\n";
}
