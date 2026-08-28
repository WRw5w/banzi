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

long long brute_log(long long a, long long b, long long mod) {
    long long value = 1 % mod;
    for (long long exponent = 0; exponent < mod; ++exponent) {
        if (value == b) return exponent;
        value = value * a % mod;
    }
    return -1;
}

int main() {
    const vector<int> primes{2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43};
    for (int mod : primes) {
        for (int a = 1; a < mod; ++a) {
            for (int b = 0; b < mod; ++b) {
                long long expected = brute_log(a, b, mod);
                long long actual = bsgs(a, b, mod);
                if (actual != expected) {
                    cerr << "mod=" << mod << " a=" << a << " b=" << b
                         << " expected=" << expected << " actual=" << actual << '\n';
                    return 1;
                }
            }
        }
    }
    cout << "BSGS exhaustive small prime groups: PASS\n";
    return 0;
}
