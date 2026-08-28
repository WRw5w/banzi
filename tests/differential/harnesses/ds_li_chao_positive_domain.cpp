#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

int main() {
    const uint64_t seed = 0x11C4A0ULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 500; ++round) {
        int right = 1 + rng() % 80;
        LiChao tree(0, right);
        vector<pair<long long,long long>> lines;
        for (int op = 0; op < 300; ++op) {
            if (lines.empty() || (rng() & 1)) {
                long long k = (long long)(rng() % 201) - 100;
                long long b = (long long)(rng() % 2001) - 1000;
                tree.add_line(k, b); lines.push_back({k, b});
            } else {
                int x = rng() % (right + 1);
                long long expected = (long long)4e18;
                for (auto [k, b] : lines) expected = min(expected, k * x + b);
                long long actual = tree.query(x);
                if (actual != expected) {
                    cerr << "seed=" << seed << " round=" << round << " op=" << op
                         << " x=" << x << " expected=" << expected << " actual=" << actual << '\n';
                    return 1;
                }
            }
        }
    }
    cout << "rounds=500 operations=150000 seed=" << seed << '\n';
}
