#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

long long brute_square_sum(int root, int parent) {
    unordered_map<int, int> frequency;
    function<void(int, int)> collect = [&](int u, int p) {
        ++frequency[color[u]];
        for (int v : g[u]) if (v != p) collect(v, u);
    };
    collect(root, parent);
    long long result = 0;
    for (auto [ignored, count] : frequency) result += 1LL * count * count;
    return result;
}

int main(int argc, char** argv) {
    for (int file_index = 1; file_index < argc; ++file_index) {
        ifstream input(argv[file_index]);
        int n;
        while (input >> n) {
            g.assign(n + 1, {});
            sz.assign(n + 1, 0);
            son.assign(n + 1, 0);
            color.assign(n + 1, 0);
            ans.assign(n + 1, 0);
            cnt.assign(n + 2, 0);
            cur_answer = 0;
            for (int u = 1; u <= n; ++u) input >> color[u];
            for (int edge = 1; edge < n; ++edge) {
                int u, v;
                input >> u >> v;
                g[u].push_back(v);
                g[v].push_back(u);
            }
            long long expected;
            input >> expected;
            long long brute = brute_square_sum(1, 0);
            if (expected != brute) {
                cerr << "bad regression oracle: expected=" << expected
                     << " brute=" << brute << '\n';
                return 2;
            }
            dfs_size(1, 0);
            dsu(1, 0, true);
            long long actual = ans[1];
            if (actual != expected) {
                cerr << "expected=" << expected << " actual=" << actual << '\n';
                return 1;
            }
        }
    }
    cout << "DSU-on-tree regressions passed\n";
    return 0;
}
