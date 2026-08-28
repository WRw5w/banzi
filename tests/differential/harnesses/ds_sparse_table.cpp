#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

int main() {
    const uint64_t seed = 0x5A235EULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 5000; ++round) {
        int n = 1 + rng() % 100;
        vector<int> a(n);
        for (int& x : a) x = (int)(rng() % 200001) - 100000;
        SparseTable table(a);
        for (int query = 0; query < 100; ++query) {
            int l = rng() % n, r = rng() % n;
            if (l > r) swap(l, r);
            int expected = *min_element(a.begin() + l, a.begin() + r + 1);
            int actual = table.query(l, r);
            if (actual != expected) {
                cerr << "seed=" << seed << " round=" << round << " l=" << l
                     << " r=" << r << " expected=" << expected << " actual=" << actual << '\n';
                return 1;
            }
        }
    }
    cout << "rounds=5000 queries=500000 seed=" << seed << '\n';
}
