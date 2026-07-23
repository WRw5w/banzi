#include <bits/stdc++.h>
#include <cassert>
using namespace std;

// 动态规划与几何的最小完整题例：函数返回题目答案，main 中保留边界断言。

// 接口：返回严格 LIS 长度；输入为空时返回 0。
int lis(const vector<int> &a) {
    vector<int> d;
    for (int x : a) {
        auto it = lower_bound(d.begin(), d.end(), x);
        if (it == d.end()) d.push_back(x);
        else *it = x;
    }
    return d.size();
}

// 接口：返回两个字符串的最长公共子序列长度；允许空串。
int lcs(const string &a, const string &b) {
    vector<int> dp(b.size() + 1);
    for (char x : a) {
        int diagonal = 0;
        for (int j = 1; j <= (int)b.size(); ++j) {
            int old = dp[j];
            if (x == b[j - 1]) dp[j] = diagonal + 1;
            else dp[j] = max(dp[j], dp[j - 1]);
            diagonal = old;
        }
    }
    return dp.back();
}

// 接口：每件物品最多选一次，返回容量不超过 cap 的最大价值。
long long knapsack01(const vector<int> &w, const vector<int> &v, int cap) {
    vector<long long> dp(cap + 1);
    for (int i = 0; i < (int)w.size(); ++i)
        for (int j = cap; j >= w[i]; --j)
            dp[j] = max(dp[j], dp[j - w[i]] + v[i]);
    return dp[cap];
}

// 接口：每件物品可选无限次；容量循环必须正序。
long long complete_knapsack(const vector<int> &w,
                            const vector<int> &v, int cap) {
    vector<long long> dp(cap + 1);
    for (int i = 0; i < (int)w.size(); ++i)
        for (int j = w[i]; j <= cap; ++j)
            dp[j] = max(dp[j], dp[j - w[i]] + v[i]);
    return dp[cap];
}

// 接口：合并相邻石子/文件，代价为每次合并区间和；空数组返回 0。
long long interval_merge(const vector<int> &a) {
    int n = a.size();
    vector<long long> pre(n + 1);
    for (int i = 0; i < n; ++i) pre[i + 1] = pre[i] + a[i];
    vector<vector<long long>> dp(n, vector<long long>(n));
    for (int len = 2; len <= n; ++len) {
        for (int l = 0; l + len <= n; ++l) {
            int r = l + len - 1;
            dp[l][r] = LLONG_MAX / 4;
            for (int k = l; k < r; ++k)
                dp[l][r] = min(dp[l][r],
                    dp[l][k] + dp[k + 1][r] + pre[r + 1] - pre[l]);
        }
    }
    return n ? dp[0][n - 1] : 0;
}

// 接口：统计 [0,x] 中十进制表示不含数字 4 的数；x<0 返回 0。
long long count_without_four(long long x) {
    if (x < 0) return 0;
    string s = to_string(x);
    long long dp[20][2]{};
    dp[0][1] = 1;
    for (int i = 0; i < (int)s.size(); ++i) {
        long long ndp[20][2]{};
        for (int tight = 0; tight <= 1; ++tight) {
            int lim = tight ? s[i] - '0' : 9;
            long long ways = dp[i][tight];
            if (!ways) continue;
            for (int d = 0; d <= lim; ++d) {
                if (d == 4) continue;
                ndp[i + 1][tight && d == lim] += ways;
            }
        }
        memcpy(dp[i + 1], ndp[i + 1], sizeof(ndp[i + 1]));
    }
    return dp[s.size()][0] + dp[s.size()][1];
}

struct Point {
    double x, y;
    bool operator<(const Point &o) const {
        return x != o.x ? x < o.x : y < o.y;
    }
};

double cross(Point a, Point b, Point c) {
    return (b.x - a.x) * (c.y - a.y) -
           (b.y - a.y) * (c.x - a.x);
}

// 接口：Andrew 凸包，去掉共线中间点；重复点会先去重。
vector<Point> convex_hull(vector<Point> p) {
    sort(p.begin(), p.end());
    p.erase(unique(p.begin(), p.end(), [](Point a, Point b) {
        return a.x == b.x && a.y == b.y;
    }), p.end());
    if (p.size() <= 1) return p;
    vector<Point> h(2 * p.size());
    int k = 0;
    for (auto q : p) {
        while (k >= 2 && cross(h[k - 2], h[k - 1], q) <= 0) --k;
        h[k++] = q;
    }
    for (int i = (int)p.size() - 2, t = k + 1; i >= 0; --i) {
        while (k >= t && cross(h[k - 2], h[k - 1], p[i]) <= 0) --k;
        h[k++] = p[i];
    }
    h.resize(k - 1);
    return h;
}

// 接口：按顶点顺序返回多边形面积绝对值；p 至少含 3 个点。
double polygon_area(const vector<Point> &p) {
    double s = 0;
    for (int i = 0; i < (int)p.size(); ++i) {
        int j = (i + 1) % p.size();
        s += p[i].x * p[j].y - p[i].y * p[j].x;
    }
    return abs(s) / 2;
}

// 接口：判断闭线段 AB 与 CD 是否相交，端点接触也算相交。
bool segment_intersects(Point a, Point b, Point c, Point d) {
    auto sgn = [](double x) {
        const double eps = 1e-9;
        return (x > eps) - (x < -eps);
    };
    double c1 = cross(a, b, c), c2 = cross(a, b, d);
    double c3 = cross(c, d, a), c4 = cross(c, d, b);
    auto on_segment = [&](Point p, Point q, Point x) {
        const double eps = 1e-9;
        return sgn(cross(p, q, x)) == 0 &&
               min(p.x, q.x) - eps <= x.x && x.x <= max(p.x, q.x) + eps &&
               min(p.y, q.y) - eps <= x.y && x.y <= max(p.y, q.y) + eps;
    };
    if (on_segment(a, b, c) || on_segment(a, b, d) ||
        on_segment(c, d, a) || on_segment(c, d, b)) return true;
    return sgn(c1) * sgn(c2) < 0 && sgn(c3) * sgn(c4) < 0;
}

// 接口：普通 Nim 是否先手必胜；所有石子堆均为非负整数。
bool nim_first_wins(const vector<int> &heap) {
    int x = 0;
    for (int v : heap) x ^= v;
    return x != 0;
}

int main() {
    assert(lis({5}) == 1);
    assert(lis({3, 1, 2, 5, 4}) == 3);
    assert(lcs("abcde", "ace") == 3 && lcs("", "abc") == 0);
    assert(knapsack01({2, 3, 4}, {3, 4, 5}, 5) == 7);
    assert(knapsack01({}, {}, 0) == 0);
    assert(complete_knapsack({2, 3}, {3, 4}, 6) == 9);
    assert(interval_merge({1, 2, 3, 4}) == 19);
    assert(count_without_four(0) == 1);
    assert(count_without_four(4) == 4);
    assert(count_without_four(10) == 10);
    vector<Point> square{{0, 0}, {1, 0}, {1, 1}, {0, 1}, {0, 0}};
    assert(convex_hull(square).size() == 4);
    assert(abs(polygon_area(square) - 1.0) < 1e-9);
    assert(segment_intersects({0, 0}, {2, 2}, {0, 2}, {2, 0}));
    assert(!segment_intersects({0, 0}, {1, 0}, {0, 1}, {1, 1}));
    assert(!segment_intersects({0, 0}, {1, 0}, {2, 0}, {3, 0}));
    assert(segment_intersects({0, 0}, {1, 0}, {1, 0}, {2, 0}));
    assert(nim_first_wins({1, 2, 4}));
    assert(!nim_first_wins({1, 2, 3}));
    cout << "dp and geometry templates: PASS\n";
}
