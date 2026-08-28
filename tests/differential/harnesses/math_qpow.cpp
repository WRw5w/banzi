#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

long long brute_qpow(long long a, long long e, long long mod) {
    long long base = a % mod;
    if (base < 0) base += mod;
    long long result = 1 % mod;
    for (long long i = 0; i < e; ++i) {
        result = (long long)((__int128)result * base % mod);
    }
    return result;
}

int main(int argc, char** argv) {
    for (int file_index = 1; file_index < argc; ++file_index) {
        ifstream input(argv[file_index]);
        if (!input) {
            cerr << "cannot open regression file: " << argv[file_index] << '\n';
            return 2;
        }
        long long a, e, mod, expected;
        while (input >> a >> e >> mod >> expected) {
            long long actual = qpow(a, e, mod);
            if (actual != expected) {
                cerr << "regression=" << argv[file_index] << " a=" << a << " e=" << e
                     << " mod=" << mod << " expected=" << expected << " actual=" << actual << '\n';
                return 1;
            }
        }
    }

    const uint64_t seed = 0xA11CE20260828ULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 20000; ++round) {
        long long mod = 1 + (long long)(rng() % 100000);
        long long a = (long long)(rng() % 200001) - 100000;
        long long e = (long long)(rng() % 20);
        long long actual = qpow(a, e, mod);
        long long expected = brute_qpow(a, e, mod);
        if (actual != expected) {
            cerr << "seed=" << seed << " round=" << round << " a=" << a << " e=" << e
                 << " mod=" << mod << " expected=" << expected << " actual=" << actual << '\n';
            return 1;
        }
    }
    cout << "rounds=20000 seed=" << seed << '\n';
    return 0;
}
