#include <bits/stdc++.h>
using namespace std;

long long qpow(long long a, long long e, long long mod) {
    a %= mod;
    if (a < 0) a += mod;
    long long result = 1 % mod;
    for (; e; e >>= 1) {
        if (e & 1) result = (long long)((__int128)result * a % mod);
        a = (long long)((__int128)a * a % mod);
    }
    return result;
}

// @@@TEMPLATE@@@

int main() {
    const uint64_t seed = 0x4E5454524F554E44ULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 5000; ++round) {
        int log_n = 1 + (int)(rng() % 9);
        int n = 1 << log_n;
        vector<int> original(n);
        for (int& value : original) value = (int)(rng() % NTT_MOD);
        vector<int> transformed = original;
        ntt(transformed, false);
        ntt(transformed, true);
        if (transformed != original) {
            cerr << "seed=" << seed << " round=" << round << " n=" << n << '\n';
            return 1;
        }
    }
    cout << "rounds=5000 seed=" << seed << '\n';
    return 0;
}
