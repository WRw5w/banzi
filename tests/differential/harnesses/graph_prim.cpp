#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

pair<bool, long long> brute_mst(
        const vector<vector<pair<int, long long>>>& graph) {
    struct Edge { int u, v; long long w; };
    vector<Edge> edges;
    int n = (int)graph.size();
    for (int u = 0; u < n; ++u)
        for (auto [v, w] : graph[u]) if (u < v) edges.push_back({u, v, w});
    if (n <= 1) return {true, 0};
    long long best = numeric_limits<long long>::max();
    int m = (int)edges.size();
    for (unsigned mask = 0; mask < (1U << m); ++mask) {
        if (__builtin_popcount(mask) != n - 1) continue;
        vector<int> parent(n);
        iota(parent.begin(), parent.end(), 0);
        function<int(int)> find = [&](int x) {
            return parent[x] == x ? x : parent[x] = find(parent[x]);
        };
        bool cycle = false;
        long long cost = 0;
        for (int i = 0; i < m; ++i) if (mask >> i & 1U) {
            int x = find(edges[i].u), y = find(edges[i].v);
            if (x == y) { cycle = true; break; }
            parent[x] = y;
            cost += edges[i].w;
        }
        if (!cycle) best = min(best, cost);
    }
    return {best != numeric_limits<long long>::max(),
            best == numeric_limits<long long>::max() ? 0 : best};
}

int main() {
    const uint64_t seed = 0xA11CEBEEFULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 5000; ++round) {
        int n = (int)(rng() % 7);
        vector<vector<pair<int, long long>>> graph(n);
        if (n > 1) {
            for (int v = 1; v < n; ++v) {
                int u = (int)(rng() % v);
                long long w = (long long)(rng() % 31) - 15;
                graph[u].push_back({v, w});
                graph[v].push_back({u, w});
            }
            int extras = (int)(rng() % 4);
            while (extras--) {
                int u = (int)(rng() % n), v = (int)(rng() % n);
                if (u == v) continue;
                long long w = (long long)(rng() % 31) - 15;
                graph[u].push_back({v, w});
                graph[v].push_back({u, w});
            }
        }
        auto actual = prim(graph);
        auto expected = brute_mst(graph);
        if (actual != expected) {
            cerr << "seed=" << seed << " round=" << round
                 << " expected_connected=" << expected.first
                 << " expected_cost=" << expected.second
                 << " actual_connected=" << actual.first
                 << " actual_cost=" << actual.second << '\n';
            return 1;
        }
    }
    cout << "rounds=5000 seed=" << seed << '\n';
    return 0;
}
