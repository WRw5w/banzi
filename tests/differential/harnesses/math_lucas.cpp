#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

long long brute_combination_mod(int n, int k, int mod) {
    if (k < 0 || k > n) return 0;
    vector<long long> row(k + 1);
    row[0] = 1 % mod;
    for (int i = 1; i <= n; ++i)
        for (int j = min(i, k); j >= 1; --j)
            row[j] = (row[j] + row[j - 1]) % mod;
    return row[k];
}

int main() {
    const vector<int> primes{2, 3, 5, 7, 11, 13, 17, 19};
    for (int p : primes) {
        vector<long long> fac(p), ifac(p);
        fac[0] = 1;
        for (int i = 1; i < p; ++i) fac[i] = fac[i - 1] * i % p;
        ifac[p - 1] = mod_pow(fac[p - 1], p - 2, p);
        for (int i = p - 1; i >= 1; --i) ifac[i - 1] = ifac[i] * i % p;
        for (int n = 0; n <= 180; ++n) {
            for (int k = 0; k <= 200; ++k) {
                long long expected = brute_combination_mod(n, k, p);
                long long actual = Lucas(n, k, p, fac, ifac);
                if (actual != expected) {
                    cerr << "p=" << p << " n=" << n << " k=" << k
                         << " expected=" << expected << " actual=" << actual << '\n';
                    return 1;
                }
            }
        }
    }
    cout << "Lucas exhaustive small range: PASS\n";
    return 0;
}
