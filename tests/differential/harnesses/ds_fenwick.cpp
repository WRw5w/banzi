#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

int main() {
    const uint64_t seed = 0xF311B17ULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 300; ++round) {
        int n = 1 + rng() % 80;
        BIT bit(n);
        vector<long long> a(n + 1);
        for (int op = 0; op < 500; ++op) {
            if (rng() & 1) {
                int x = 1 + rng() % n;
                long long value = (long long)(rng() % 2001) - 1000;
                bit.add(x, value); a[x] += value;
            } else {
                int l = 1 + rng() % n, r = 1 + rng() % n;
                if (l > r) swap(l, r);
                long long expected = accumulate(a.begin() + l, a.begin() + r + 1, 0LL);
                long long actual = bit.range(l, r);
                if (actual != expected) {
                    cerr << "seed=" << seed << " round=" << round << " op=" << op
                         << " expected=" << expected << " actual=" << actual << '\n';
                    return 1;
                }
            }
        }
    }
    cout << "rounds=300 operations=150000 seed=" << seed << '\n';
}
