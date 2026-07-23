#include <bits/stdc++.h>
#include <cassert>
using namespace std;

// 进阶模板仍采用最小题目接口；所有测试均可独立运行，不依赖 PDF 中的全局数组。

struct LinearBasis {
    long long b[63]{};
    // 接口：insert 返回是否提高了线性基秩；max_xor 返回可表示的最大异或值。
    bool insert(long long x) {
        for (int i = 62; i >= 0; --i) if (x >> i & 1) {
            if (!b[i]) return b[i] = x, true;
            x ^= b[i];
        }
        return false;
    }
    long long max_xor() const {
        long long ans = 0;
        for (int i = 62; i >= 0; --i) ans = max(ans, ans ^ b[i]);
        return ans;
    }
};

long long exgcd(long long a, long long b, long long &x, long long &y) {
    if (!b) return x = 1, y = 0, a;
    long long xx, yy, g = exgcd(b, a % b, xx, yy);
    x = yy;
    y = xx - a / b * yy;
    return g;
}

// 接口：合并 x=a1(mod m1) 与 x=a2(mod m2)；无解返回 nullopt。
optional<pair<long long, long long>> merge_congruence(
        long long a1, long long m1, long long a2, long long m2) {
    long long x, y, g = exgcd(m1, m2, x, y);
    long long d = a2 - a1;
    if (d % g) return nullopt;
    long long mod = m2 / g;
    long long k = (long long)((__int128)(d / g) * x % mod);
    if (k < 0) k += mod;
    long long lcm = m1 / g * m2;
    long long answer = (long long)((a1 + (__int128)m1 * k) % lcm);
    if (answer < 0) answer += lcm;
    return pair<long long, long long>{answer, lcm};
}

struct Matrix {
    long long a[2][2]{};
};

Matrix multiply(Matrix x, Matrix y, long long mod) {
    Matrix z;
    for (int i = 0; i < 2; ++i)
        for (int k = 0; k < 2; ++k)
            for (int j = 0; j < 2; ++j)
                z.a[i][j] = (z.a[i][j] +
                    (__int128)x.a[i][k] * y.a[k][j]) % mod;
    return z;
}

// 接口：返回 F_n mod mod，约定 F_0=0、F_1=1。
long long fibonacci(long long n, long long mod) {
    Matrix ans{{{1, 0}, {0, 1}}};
    Matrix base{{{1, 1}, {1, 0}}};
    while (n) {
        if (n & 1) ans = multiply(ans, base, mod);
        base = multiply(base, base, mod);
        n >>= 1;
    }
    return ans.a[0][1];
}

// 接口：增广矩阵 a 为 n 行 n+1 列；唯一解返回 vector，否则返回 nullopt。
optional<vector<double>> gaussian_unique(vector<vector<double>> a) {
    const double eps = 1e-9;
    int n = a.size(), row = 0;
    for (int col = 0; col < n; ++col) {
        int pivot = row;
        for (int i = row; i < n; ++i)
            if (abs(a[i][col]) > abs(a[pivot][col])) pivot = i;
        if (abs(a[pivot][col]) < eps) continue;
        swap(a[pivot], a[row]);
        double div = a[row][col];
        for (int j = col; j <= n; ++j) a[row][j] /= div;
        for (int i = 0; i < n; ++i) if (i != row) {
            double factor = a[i][col];
            for (int j = col; j <= n; ++j)
                a[i][j] -= factor * a[row][j];
        }
        ++row;
    }
    if (row < n) return nullopt;
    vector<double> answer(n);
    for (int i = 0; i < n; ++i) answer[i] = a[i][n];
    return answer;
}

struct PersistentKth {
    struct Node { int left = 0, right = 0, sum = 0; };
    vector<Node> tr{{}};
    vector<int> root{0}, values;

    int update(int old, int l, int r, int pos) {
        int now = tr.size();
        tr.push_back(tr[old]);
        ++tr[now].sum;
        if (l != r) {
            int m = (l + r) / 2;
            if (pos <= m) tr[now].left = update(tr[old].left, l, m, pos);
            else tr[now].right = update(tr[old].right, m + 1, r, pos);
        }
        return now;
    }
    int query_node(int a, int b, int l, int r, int k) const {
        if (l == r) return l;
        int left_count = tr[tr[b].left].sum - tr[tr[a].left].sum;
        int m = (l + r) / 2;
        if (k <= left_count)
            return query_node(tr[a].left, tr[b].left, l, m, k);
        return query_node(tr[a].right, tr[b].right,
                          m + 1, r, k - left_count);
    }
    explicit PersistentKth(const vector<int> &a) {
        values = a;
        sort(values.begin(), values.end());
        values.erase(unique(values.begin(), values.end()), values.end());
        for (int x : a) {
            int pos = lower_bound(values.begin(), values.end(), x) -
                      values.begin();
            root.push_back(update(root.back(), 0, values.size() - 1, pos));
        }
    }
    // 接口：查询 a[l..r] 的第 k 小，l/r 为 1-based 闭区间。
    int kth(int l, int r, int k) const {
        assert(1 <= k && k <= r - l + 1);
        return values[query_node(root[l - 1], root[r],
                                 0, values.size() - 1, k)];
    }
};

struct LiChao {
    struct Line {
        long long k = 0, b = LLONG_MIN / 4;
        long long value(long long x) const { return k * x + b; }
    };
    int left, right;
    vector<Line> tr;
    LiChao(int l, int r) : left(l), right(r), tr(4 * (r - l + 1)) {}
    void add(Line line, int p, int l, int r) {
        int m = (l + r) / 2;
        bool low = line.value(l) > tr[p].value(l);
        bool mid = line.value(m) > tr[p].value(m);
        if (mid) swap(line, tr[p]);
        if (l == r) return;
        if (low != mid) add(line, p * 2, l, m);
        else add(line, p * 2 + 1, m + 1, r);
    }
    // 接口：加入直线 y=kx+b；query(x) 返回固定整数域上的最大值。
    void add(long long k, long long b) { add({k, b}, 1, left, right); }
    long long query(int x, int p, int l, int r) const {
        long long ans = tr[p].value(x);
        if (l == r) return ans;
        int m = (l + r) / 2;
        if (x <= m) return max(ans, query(x, p * 2, l, m));
        return max(ans, query(x, p * 2 + 1, m + 1, r));
    }
    long long query(int x) const { return query(x, 1, left, right); }
};

int main() {
    LinearBasis basis;
    assert(basis.insert(3));
    assert(basis.insert(5));
    assert(!basis.insert(6));
    assert(basis.max_xor() == 6);

    assert(merge_congruence(1, 4, 3, 6).value() ==
           make_pair(9LL, 12LL));
    assert(!merge_congruence(0, 2, 1, 4).has_value());
    assert(fibonacci(0, 1000000007) == 0);
    assert(fibonacci(10, 1000000007) == 55);

    auto solution = gaussian_unique({{1, 1, 3}, {2, -1, 0}});
    assert(solution.has_value());
    assert(abs((*solution)[0] - 1) < 1e-9);
    assert(abs((*solution)[1] - 2) < 1e-9);
    assert(!gaussian_unique({{1, 1, 2}, {2, 2, 4}}).has_value());

    PersistentKth kth({4, 4, 1, 7});
    assert(kth.kth(1, 4, 2) == 4);
    assert(kth.kth(2, 4, 1) == 1);

    LiChao lichao(-5, 5);
    lichao.add(1, 0);
    lichao.add(-1, 2);
    assert(lichao.query(-2) == 4);
    assert(lichao.query(5) == 5);
    cout << "advanced templates: PASS\n";
}
