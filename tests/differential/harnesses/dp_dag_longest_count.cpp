#include <bits/stdc++.h>
using namespace std;

pair<long long, int> run_template(
        int n, int source, int target, int MOD,
        const vector<vector<pair<int, long long>>>& input_dag) {
    const long long NEG = -4'000'000'000'000'000'000LL;
    vector<int> topo(n);
    iota(topo.begin(), topo.end(), 0);
    vector<vector<pair<int, long long>>> dag = input_dag;
    vector<long long> dp(n, NEG);
    vector<int> ways(n, 0);
    dp[source] = 0;
    ways[source] = 1;

    // @@@TEMPLATE@@@

    return {dp[target], ways[target]};
}

int main(int argc, char** argv) {
    for (int file_index = 1; file_index < argc; ++file_index) {
        ifstream input(argv[file_index]);
        int n, m, source, target, mod, expected_ways;
        long long expected_dp;
        while (input >> n >> m >> source >> target >> mod
                     >> expected_dp >> expected_ways) {
            vector<vector<pair<int, long long>>> dag(n);
            for (int edge = 0; edge < m; ++edge) {
                int u, v;
                long long w;
                input >> u >> v >> w;
                dag[u].push_back({v, w});
            }
            auto [actual_dp, actual_ways] =
                run_template(n, source, target, mod, dag);
            if (actual_dp != expected_dp || actual_ways != expected_ways) {
                cerr << "expected_dp=" << expected_dp
                     << " expected_ways=" << expected_ways
                     << " actual_dp=" << actual_dp
                     << " actual_ways=" << actual_ways << '\n';
                return 1;
            }
        }
    }
    cout << "DAG longest-path count regressions passed\n";
    return 0;
}
