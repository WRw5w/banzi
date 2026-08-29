#include <bits/stdc++.h>
using namespace std;

// @@@LCT@@@

bool connected(const vector<set<int>>& graph, int source, int target) {
    vector<char> seen(graph.size());
    queue<int> pending;
    pending.push(source);
    seen[source] = true;
    while (!pending.empty()) {
        int node = pending.front();
        pending.pop();
        if (node == target) return true;
        for (int next : graph[node]) if (!seen[next]) {
            seen[next] = true;
            pending.push(next);
        }
    }
    return false;
}

long long naive_path_sum(
    const vector<set<int>>& graph, const vector<long long>& value, int source, int target
) {
    vector<int> parent(graph.size(), -1);
    queue<int> pending;
    pending.push(source);
    parent[source] = 0;
    while (!pending.empty()) {
        int node = pending.front();
        pending.pop();
        for (int next : graph[node]) if (parent[next] == -1) {
            parent[next] = node;
            pending.push(next);
        }
    }
    long long answer = 0;
    for (int node = target; node; node = parent[node]) {
        answer += value[node];
        if (node == source) break;
    }
    return answer;
}

void set_value(LCT& lct, int node, long long value) {
    lct.access(node);
    lct.splay(node);
    lct.t[node].val = value;
    lct.pull_sum(node);
}

int main() {
    mt19937_64 rng(0x4C43545F464F5245ULL);
    for (int round = 0; round < 250; ++round) {
        int n = 2 + rng() % 11;
        LCT lct(n);
        vector<set<int>> graph(n + 1);
        vector<long long> value(n + 1);
        vector<pair<int, int>> edges;
        for (int node = 1; node <= n; ++node) {
            value[node] = (long long)(rng() % 101) - 50;
            set_value(lct, node, value[node]);
        }
        for (int operation = 0; operation < 350; ++operation) {
            int type = rng() % 4;
            int x = 1 + rng() % n;
            int y = 1 + rng() % n;
            if (type == 0) {
                value[x] = (long long)(rng() % 101) - 50;
                set_value(lct, x, value[x]);
            } else if (type == 1 && x != y && !connected(graph, x, y)) {
                lct.link(x, y);
                graph[x].insert(y);
                graph[y].insert(x);
                edges.push_back({min(x, y), max(x, y)});
            } else if (type == 2 && !edges.empty()) {
                int index = rng() % edges.size();
                auto [u, v] = edges[index];
                lct.cut(u, v);
                graph[u].erase(v);
                graph[v].erase(u);
                edges[index] = edges.back();
                edges.pop_back();
            } else if (x != y && connected(graph, x, y)) {
                long long expected = naive_path_sum(graph, value, x, y);
                long long actual = lct.path_sum(x, y);
                if (actual != expected) {
                    cerr << "path sum mismatch round=" << round
                         << " operation=" << operation << '\n';
                    return 1;
                }
            }
            int a = 1 + rng() % n;
            int b = 1 + rng() % n;
            bool expected_connected = connected(graph, a, b);
            bool actual_connected = lct.findroot(a) == lct.findroot(b);
            if (expected_connected != actual_connected) {
                cerr << "connectivity mismatch\n";
                return 1;
            }
        }
    }
    cout << "rounds=250 operations=87500 LCT forest contracts passed\n";
}
