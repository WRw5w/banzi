#include <bits/stdc++.h>
using namespace std;

namespace exgcd_case {
// @@@EXGCD@@@
}

namespace factor_case {
// @@@FACTOR@@@
}

namespace lucas_case {
long long qpow(long long a, long long e, long long mod) {
    long long r = 1;
    while (e) { if (e & 1) r = (__int128)r * a % mod; a = (__int128)a * a % mod; e >>= 1; }
    return r;
}
// @@@LUCAS@@@
}

namespace crt_case {
long long exgcd(long long a, long long b, long long& x, long long& y) {
    if (!b) { x = 1; y = 0; return a; }
    long long x1, y1, g = exgcd(b, a % b, x1, y1);
    x = y1; y = x1 - a / b * y1; return g;
}
// @@@CRT_MERGE@@@
}

namespace matrix_case {
constexpr long long MOD = 1000000007;
// @@@MATRIX@@@
}

namespace sequence_case {
// @@@SEQUENCES@@@
}

namespace poly_case {
// @@@POLY@@@
}

namespace tree_count_case {
long long mod_pow(long long a, long long e, long long mod) {
    long long r = 1;
    while (e) { if (e & 1) r = (__int128)r * a % mod; a = (__int128)a * a % mod; e >>= 1; }
    return r;
}
// @@@TREE_COUNT@@@
}

namespace tonelli_case {
long long mod_pow(long long a, long long e, long long mod) {
    long long r = 1;
    while (e) { if (e & 1) r = (__int128)r * a % mod; a = (__int128)a * a % mod; e >>= 1; }
    return r;
}
// @@@TONELLI@@@
}

namespace excrt_detail_case {
// @@@EXCRT_DETAIL@@@
}

namespace mu_case {
// @@@MU_SIEVE@@@
}

namespace matrix_detail_case {
constexpr long long MOD = 1000000007;
// @@@MATRIX_DETAIL@@@
}

namespace gauss_case {
// @@@GAUSS_REAL@@@
}
namespace poly_detail_case {
constexpr long long MOD=1000000007;
// @@@POLY_DETAIL@@@
}

static bool prime(long long x) {
    if (x < 2) return false;
    for (long long d = 2; d * d <= x; ++d) if (x % d == 0) return false;
    return true;
}

int main() {
    mt19937_64 rng(20260829);
    for (int it = 0; it < 5000; ++it) {
        long long a = rng() % 1000000 + 1, b = rng() % 1000000 + 1, x, y;
        long long g = exgcd_case::exgcd(a, b, x, y);
        if (g != gcd(a, b) || (__int128)a * x + (__int128)b * y != g) return 1;
    }
    for (int n = 1; n <= 10000; ++n) {
        long long product = 1;
        for (auto [p, e] : factor_case::factor(n)) {
            if (!prime(p) || e <= 0) return 2;
            while (e--) product *= p;
        }
        if (product != n) return 3;
    }
    for (long long p : {2LL, 3LL, 5LL, 7LL, 11LL}) {
        vector<vector<long long>> c(101, vector<long long>(101)); c[0][0] = 1;
        for (int n = 1; n <= 100; ++n) for (int k = 0; k <= n; ++k)
            c[n][k] = ((k ? c[n - 1][k - 1] : 0) + c[n - 1][k]) % p;
        for (int n = 0; n <= 100; ++n) for (int k = 0; k <= n; ++k)
            if (lucas_case::lucas(n, k, p) != c[n][k]) return 4;
    }
    for (int m1 = 1; m1 <= 15; ++m1) for (int m2 = 1; m2 <= 15; ++m2)
        for (int a1 = 0; a1 < m1; ++a1) for (int a2 = 0; a2 < m2; ++a2) {
            long long a, m; bool ok = crt_case::merge_congruence(a1, m1, a2, m2, a, m);
            int brute = -1; for (int x = 0; x < lcm(m1, m2); ++x)
                if (x % m1 == a1 && x % m2 == a2) { brute = x; break; }
            if (ok != (brute >= 0) || (ok && (a != brute || m != lcm(m1, m2)))) return 5;
            long long da = a1, dm = m1; bool dok = excrt_detail_case::merge(da, dm, a2, m2);
            if (dok != (brute >= 0) || (dok && (da != brute || dm != lcm(m1, m2)))) return 6;
        }
    matrix_case::Mat fibm(2); fibm.a = {{1, 1}, {1, 0}};
    long long f0 = 0, f1 = 1;
    for (int n = 0; n <= 80; ++n) {
        long long got = n == 0 ? 0 : matrix_case::mpow(fibm, n - 1).a[0][0];
        if (got != f0) return 7;
        long long next = (f0 + f1) % matrix_case::MOD; f0 = f1; f1 = next;
    }
    long long xb = 0;
    for (int n = 0; n <= 10000; ++n) {
        xb ^= n;
        if (sequence_case::xor_prefix(n) != xb) return 8;
    }
    long long fa = 0, fb = 1;
    for (int n = 0; n <= 45; ++n) {
        auto got = sequence_case::fib(n);
        if (got != pair<long long,long long>{fa, fb}) return 9;
        tie(fa, fb) = pair<long long,long long>{fb, fa + fb};
    }
    if (poly_case::multiply({1,2,3}, {4,5}, 1000) != poly_case::Poly({4,13,22,15})) return 10;
    if (poly_case::ways({1,1}, 5, 1000) != poly_case::Poly({1,5,10,10,5,1})) return 11;
    const long long mod = 1000000007;
    for (int n = 1; n <= 10; ++n) {
        if (n == 1) continue;
        vector<vector<long long>> lap(n - 1, vector<long long>(n - 1, -1));
        for (int i = 0; i < n - 1; ++i) lap[i][i] = n - 1;
        long long want = tree_count_case::mod_pow(n, n - 2, mod);
        if (tree_count_case::tree_count(lap, mod) != want) return 12;
    }
    for (long long p : {2LL,3LL,5LL,7LL,11LL,13LL,17LL,19LL,23LL,29LL,31LL,37LL,41LL,43LL,47LL})
        for (long long n = 0; n < p; ++n) {
            long long root = tonelli_case::tonelli_shanks(n, p);
            bool exists = false; for (long long x = 0; x < p; ++x) exists |= x*x%p == n;
            if ((root >= 0) != exists || (root >= 0 && root*root%p != n)) return 13;
        }
    mu_case::linear_sieve_mu(5000);
    for (int n = 1; n <= 5000; ++n) {
        int x = n, cnt = 0, want = 1;
        for (int p = 2; p * p <= x; ++p) if (x % p == 0) {
            x /= p; ++cnt; if (x % p == 0) { want = 0; break; }
            while (x % p == 0) x /= p;
        }
        if (want && x > 1) ++cnt;
        if (want) want = (cnt & 1) ? -1 : 1;
        if (mu_case::mu[n] != want) return 14;
    }
    long long p0 = 0, p1 = 1;
    for (int n = 0; n <= 90; ++n) {
        if (matrix_detail_case::fibonacci(n) != p0) return 15;
        long long next = (p0 + p1) % matrix_detail_case::MOD; p0 = p1; p1 = next;
    }
    vector<long double> ans;
    if (gauss_case::gauss_real({{1,1,3},{2,-1,0}}, ans) != 1 ||
        fabsl(ans[0]-1) > 1e-9 || fabsl(ans[1]-2) > 1e-9) return 16;
    if (gauss_case::gauss_real({{1,1,1},{1,1,2}}, ans) != 0) return 17;
    if (gauss_case::gauss_real({{1,1,1},{2,2,2}}, ans) != 2) return 18;
    if(poly_detail_case::multiply({1,2,3},{4,5})!=vector<long long>({4,13,22,15}))return 19;
    cout << "math complete contracts: PASS\n";
}
