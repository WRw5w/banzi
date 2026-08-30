#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

int main() {
    const uint64_t seed = 0xBEA75ULL;
    mt19937_64 rng(seed);
    {vector<long long>a{0,LLONG_MAX,LLONG_MAX};SegBeats tree(a);if(tree.query_sum(1,2)!=(__int128)LLONG_MAX*2)return 2;tree.chmin(1,2,LLONG_MIN);if(tree.query_sum(1,2)!=(__int128)LLONG_MIN*2)return 3;}
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
                __int128 expected = 0; for(int i=l;i<=r;++i) expected += a[i];
                __int128 actual = tree.query_sum(l, r);
                if (actual != expected) {
                    cerr << "seed=" << seed << " round=" << round << " op=" << op
                         << " sum mismatch\n";
                    return 1;
                }
            }
        }
    }
    cout << "rounds=300 operations=150000 seed=" << seed << '\n';
}
