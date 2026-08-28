#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

int main() {
    const uint64_t seed = 0x5E67A11ULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 250; ++round) {
        int n = 1 + rng() % 70;
        SegTree tree(n);
        vector<long long> a(n + 1);
        for (int op = 0; op < 500; ++op) {
            int l = 1 + rng() % n, r = 1 + rng() % n;
            if (l > r) swap(l, r);
            if (rng() & 1) {
                long long value = (long long)(rng() % 2001) - 1000;
                tree.add(1, 1, n, l, r, value);
                for (int i = l; i <= r; ++i) a[i] += value;
            } else {
                long long expected = accumulate(a.begin() + l, a.begin() + r + 1, 0LL);
                long long actual = tree.query(1, 1, n, l, r);
                if (actual != expected) {
                    cerr << "seed=" << seed << " round=" << round << " op=" << op
                         << " expected=" << expected << " actual=" << actual << '\n';
                    return 1;
                }
            }
        }
    }
    cout << "rounds=250 operations=125000 seed=" << seed << '\n';
}
