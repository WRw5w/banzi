#include <bits/stdc++.h>
using namespace std;

// @@@KRUSKAL_RECONSTRUCTION@@@

static const long long INF = (1LL << 60);

long long brute_bottleneck(
    int n, const vector<KruskalTree::Edge>& edges, int source, int target
) {
    if (source == target) return numeric_limits<long long>::lowest();
    vector<vector<long long>> best(n + 1, vector<long long>(n + 1, INF));
    for (int i = 1; i <= n; ++i) best[i][i] = numeric_limits<long long>::lowest();
    for (auto edge : edges) {
        best[edge.u][edge.v] = min(best[edge.u][edge.v], edge.w);
        best[edge.v][edge.u] = min(best[edge.v][edge.u], edge.w);
    }
    for (int k = 1; k <= n; ++k)
        for (int i = 1; i <= n; ++i)
            for (int j = 1; j <= n; ++j)
                best[i][j] = min(best[i][j], max(best[i][k], best[k][j]));
    return best[source][target];
}

int brute_component_size(
    int n, const vector<KruskalTree::Edge>& edges, int source, long long limit
) {
    vector<vector<int>> graph(n + 1);
    for (auto edge : edges) if (edge.w <= limit) {
        graph[edge.u].push_back(edge.v);
        graph[edge.v].push_back(edge.u);
    }
    vector<char> seen(n + 1);
    queue<int> pending;
    pending.push(source);
    seen[source] = true;
    int count = 0;
    while (!pending.empty()) {
        int node = pending.front();
        pending.pop();
        ++count;
        for (int next : graph[node]) if (!seen[next]) {
            seen[next] = true;
            pending.push(next);
        }
    }
    return count;
}

int main() {
    mt19937_64 rng(0x4B5255534B414C4CULL);
    for (int round = 0; round < 1200; ++round) {
        int n = 1 + rng() % 9;
        vector<KruskalTree::Edge> edges;
        for (int u = 1; u <= n; ++u) for (int v = u + 1; v <= n; ++v) {
            if (rng() % 3 == 0) edges.push_back({u, v, (long long)(rng() % 17) - 8});
            if (rng() % 11 == 0) edges.push_back({u, v, (long long)(rng() % 17) - 8});
        }
        KruskalTree tree;
        tree.build(n, edges);
        for (int u = 1; u <= n; ++u) for (int v = 1; v <= n; ++v) {
            long long expected = brute_bottleneck(n, edges, u, v);
            auto actual = tree.bottleneck(u, v);
            if (expected == INF) {
                if (actual.has_value()) {
                    cerr << "disconnected pair returned a bottleneck\n";
                    return 1;
                }
            } else if (!actual.has_value() || *actual != expected) {
                cerr << "bottleneck mismatch\n";
                return 1;
            }
            for (long long limit = -9; limit <= 9; ++limit) {
                int want = brute_component_size(n, edges, u, limit);
                int got = tree.component_size(u, limit);
                if (got != want) {
                    cerr << "component size mismatch\n";
                    return 1;
                }
            }
        }
    }
    cout << "rounds=1200 Kruskal reconstruction contracts passed\n";
}
