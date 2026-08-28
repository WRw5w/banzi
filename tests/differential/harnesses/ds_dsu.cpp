#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

int main() {
    const uint64_t seed = 0xD500ULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 1000; ++round) {
        int n = 2 + rng() % 80;
        DSU dsu(n);
        vector<vector<int>> connected(n + 1, vector<int>(n + 1));
        for (int i = 1; i <= n; ++i) connected[i][i] = 1;
        for (int op = 0; op < 500; ++op) {
            int a = 1 + rng() % n, b = 1 + rng() % n;
            bool expected = !connected[a][b];
            bool actual = dsu.unite(a, b);
            if (actual != expected) return 1;
            if (expected) {
                vector<int> left, right;
                for (int i = 1; i <= n; ++i) {
                    if (connected[a][i]) left.push_back(i);
                    if (connected[b][i]) right.push_back(i);
                }
                for (int x : left) for (int y : right) connected[x][y] = connected[y][x] = 1;
            }
            int x = 1 + rng() % n, y = 1 + rng() % n;
            if ((dsu.find(x) == dsu.find(y)) != (bool)connected[x][y]) return 1;
        }
    }
    cout << "rounds=1000 operations=500000 seed=" << seed << '\n';
}
