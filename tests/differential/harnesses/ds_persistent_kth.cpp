#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

int main() {
    const uint64_t seed = 0xB0557EULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 1000; ++round) {
        int n = 1 + rng() % 100;
        vector<int> a(n + 1), values;
        for (int i = 1; i <= n; ++i) a[i] = (int)(rng() % 101) - 50, values.push_back(a[i]);
        sort(values.begin(), values.end());
        values.erase(unique(values.begin(), values.end()), values.end());
        tot = 0; tr[0] = {};
        vector<int> root(n + 1);
        for (int i = 1; i <= n; ++i) {
            int position = lower_bound(values.begin(), values.end(), a[i]) - values.begin();
            root[i] = update(root[i - 1], 0, (int)values.size() - 1, position);
        }
        for (int query = 0; query < 200; ++query) {
            int l = 1 + rng() % n, r = 1 + rng() % n;
            if (l > r) swap(l, r);
            int k = 1 + rng() % (r - l + 1);
            vector<int> part(a.begin() + l, a.begin() + r + 1);
            nth_element(part.begin(), part.begin() + k - 1, part.end());
            int expected = part[k - 1];
            int index = kth(root[l - 1], root[r], 0, (int)values.size() - 1, k);
            int actual = values[index];
            if (actual != expected) {
                cerr << "seed=" << seed << " round=" << round << " l=" << l << " r=" << r
                     << " k=" << k << " expected=" << expected << " actual=" << actual << '\n';
                return 1;
            }
        }
    }
    cout << "rounds=1000 queries=200000 seed=" << seed << '\n';
}
