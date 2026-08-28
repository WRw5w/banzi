#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

int main() {
    const uint64_t seed = 0xA11CE20260828ULL;
    mt19937_64 rng(seed);
    for (int n = 2; n <= 30; ++n) {
        for (int round = 0; round < 300; ++round) {
            vector<int> code(max(0, n - 2));
            for (int& value : code) value = 1 + int(rng() % n);
            auto edges = prufer_decode(code);
            vector<vector<int>> graph(n + 1);
            for (auto [u, v] : edges) {
                graph[u].push_back(v);
                graph[v].push_back(u);
            }
            vector<int> encoded = prufer_encode(graph);
            if (encoded != code) {
                cerr << "seed=" << seed << " n=" << n << " round=" << round << '\n';
                return 1;
            }
        }
    }
    cout << "Pruefer round trips: PASS seed=" << seed << '\n';
    return 0;
}
