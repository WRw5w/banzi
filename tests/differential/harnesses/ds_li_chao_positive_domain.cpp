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
                __int128 expected = (__int128)1<<126;
                for (auto [k, b] : lines) expected = min(expected, (__int128)k * x + b);
                __int128 actual = tree.query(x);
                if (actual != expected) {
                    cerr << "seed=" << seed << " round=" << round << " op=" << op
                         << " x=" << x << " value mismatch\n";
                    return 1;
                }
            }
        }
    }
    {LiChao tree(0,2);if(tree.query(2)!=((__int128)1<<126))return 2;tree.add_line(LLONG_MAX,LLONG_MAX);if(tree.query(2)!=(__int128)LLONG_MAX*3)return 3;tree.add_line(LLONG_MIN,LLONG_MIN);if(tree.query(2)!=(__int128)LLONG_MIN*3)return 4;}
    cout << "rounds=500 operations=150000 seed=" << seed << '\n';
}
