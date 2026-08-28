#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

bool brute_connected(int n, const vector<pair<int,int>>& edges, int s, int t) {
    vector<vector<int>> graph(n + 1);
    for (auto [u, v] : edges) graph[u].push_back(v), graph[v].push_back(u);
    vector<int> seen(n + 1); queue<int> q; q.push(s); seen[s] = 1;
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v : graph[u]) if (!seen[v]) seen[v] = 1, q.push(v);
    }
    return seen[t];
}

int main() {
    const uint64_t seed = 0xBACCDA7AULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 500; ++round) {
        int n = 2 + rng() % 28;
        RollbackDSU dsu(n);
        vector<pair<int,int>> base;
        for (int phase = 0; phase < 30; ++phase) {
            int snap = dsu.snapshot();
            vector<pair<int,int>> saved = base;
            for (int op = 0; op < 30; ++op) {
                int u = 1 + rng() % n, v = 1 + rng() % n;
                bool expected_merge = !brute_connected(n, base, u, v);
                bool actual_merge = dsu.unite(u, v);
                if (actual_merge != expected_merge) return 1;
                if (actual_merge) base.push_back({u, v});
                int x = 1 + rng() % n, y = 1 + rng() % n;
                if ((dsu.find(x) == dsu.find(y)) != brute_connected(n, base, x, y)) return 1;
            }
            dsu.rollback(snap); base = saved;
            for (int x = 1; x <= n; ++x)
                for (int y = 1; y <= n; ++y)
                    if ((dsu.find(x) == dsu.find(y)) != brute_connected(n, base, x, y)) return 1;
            int u = 1 + rng() % n, v = 1 + rng() % n;
            if (dsu.unite(u, v)) base.push_back({u, v});
        }
    }
    cout << "rounds=500 seed=" << seed << '\n';
}
