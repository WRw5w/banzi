#include <bits/stdc++.h>
using namespace std;

// @@@DINIC@@@

long long run_dinic(int n, int source, int target) {
    level.assign(n, -1);
    it.assign(n, 0);
    long long answer = 0;
    const long long INF_FLOW = numeric_limits<long long>::max() / 4;
    while (bfs(source, target)) {
        fill(it.begin(), it.end(), 0);
        while (long long pushed = dfs(source, target, INF_FLOW)) answer += pushed;
    }
    return answer;
}

long long edmonds_karp(vector<vector<long long>> capacity, int source, int target) {
    int n = capacity.size();
    long long answer = 0;
    while (true) {
        vector<int> parent(n, -1);
        parent[source] = source;
        queue<int> pending;
        pending.push(source);
        while (!pending.empty() && parent[target] == -1) {
            int node = pending.front();
            pending.pop();
            for (int next = 0; next < n; ++next) {
                if (parent[next] == -1 && capacity[node][next] > 0) {
                    parent[next] = node;
                    pending.push(next);
                }
            }
        }
        if (parent[target] == -1) return answer;
        long long pushed = numeric_limits<long long>::max();
        for (int node = target; node != source; node = parent[node])
            pushed = min(pushed, capacity[parent[node]][node]);
        for (int node = target; node != source; node = parent[node]) {
            capacity[parent[node]][node] -= pushed;
            capacity[node][parent[node]] += pushed;
        }
        answer += pushed;
    }
}

int main() {
    mt19937_64 rng(0x44494E49435F464CULL);
    for (int round = 0; round < 2500; ++round) {
        int n = 2 + rng() % 8;
        int source = 0, target = n - 1;
        fg.assign(n, {});
        vector<vector<long long>> capacity(n, vector<long long>(n));
        for (int u = 0; u < n; ++u) for (int v = 0; v < n; ++v) if (u != v) {
            if (rng() % 4 == 0) {
                long long cap = rng() % 20;
                add_edge(u, v, cap);
                capacity[u][v] += cap;
            }
        }
        long long expected = edmonds_karp(capacity, source, target);
        long long actual = run_dinic(n, source, target);
        if (actual != expected) {
            cerr << "max-flow mismatch round=" << round
                 << " expected=" << expected << " actual=" << actual << '\n';
            return 1;
        }
    }
    cout << "rounds=2500 Dinic vs Edmonds-Karp passed\n";
}
