#include <bits/stdc++.h>
using namespace std;

long long mod_pow(long long a, long long e, long long mod) {
    a %= mod;
    if (a < 0) a += mod;
    long long result = 1 % mod;
    while (e != 0) {
        if (e & 1) result = (long long)((__int128)result * a % mod);
        a = (long long)((__int128)a * a % mod);
        e >>= 1;
    }
    return result;
}

// @@@TEMPLATE@@@

int main() {
    const vector<int> primes{
        2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41,
        43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97
    };
    for (int p : primes) {
        for (int n = 0; n < p; ++n) {
            vector<int> roots;
            for (int x = 0; x < p; ++x) if (x * x % p == n) roots.push_back(x);
            long long actual = tonelli_shanks(n, p);
            if (roots.empty()) {
                if (actual != -1) {
                    cerr << "p=" << p << " n=" << n << " expected=-1 actual=" << actual << '\n';
                    return 1;
                }
            } else if (actual < 0 || actual >= p || actual * actual % p != n) {
                cerr << "p=" << p << " n=" << n << " invalid_root=" << actual << '\n';
                return 1;
            }
        }
    }
    cout << "Tonelli-Shanks exhaustive small primes: PASS\n";
    return 0;
}
