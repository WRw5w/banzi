#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

int main() {
    const uint64_t seed = 0xBEA75ULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 300; ++round) {
        int n = 1 + rng() % 70;
        vector<long long> a(n + 1);
        for (int i = 1; i <= n; ++i) a[i] = (long long)(rng() % 2001) - 1000;
        SegBeats tree(a);
        for (int op = 0; op < 500; ++op) {
            int l = 1 + rng() % n, r = 1 + rng() % n;
            if (l > r) swap(l, r);
            if (rng() & 1) {
                long long cap = (long long)(rng() % 2001) - 1000;
                tree.chmin(l, r, cap);
                for (int i = l; i <= r; ++i) a[i] = min(a[i], cap);
            } else {
                long long expected = accumulate(a.begin() + l, a.begin() + r + 1, 0LL);
                long long actual = tree.query_sum(l, r);
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
