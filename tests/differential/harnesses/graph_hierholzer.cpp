#include <bits/stdc++.h>
using namespace std;

int n;
vector<vector<pair<int, int>>> g;
vector<char> used;

// @@@TEMPLATE@@@

int main(int argc, char** argv) {
    for (int file_index = 1; file_index < argc; ++file_index) {
        ifstream input(argv[file_index]);
        int m, start;
        while (input >> n >> m >> start) {
            g.assign(n, {});
            used.assign(m, false);
            ptr.assign(n, 0);
            euler.clear();
            for (int id = 0; id < m; ++id) {
                int u, v;
                input >> u >> v;
                g[u].push_back({v, id});
            }
            vector<int> expected(m + 1);
            for (int& vertex : expected) input >> vertex;
            hierholzer(start);
            if (euler != expected) {
                cerr << "expected=";
                for (int vertex : expected) cerr << vertex << ',';
                cerr << " actual=";
                for (int vertex : euler) cerr << vertex << ',';
                cerr << '\n';
                return 1;
            }
        }
    }
    cout << "Hierholzer regressions passed\n";
    return 0;
}
