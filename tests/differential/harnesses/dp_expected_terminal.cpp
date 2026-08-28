#include <bits/stdc++.h>
using namespace std;

double run_template(const vector<vector<pair<int, double>>>& input,
                    int target) {
    int n = (int)input.size();
    vector<vector<pair<int, double>>> transitions = input;

    // @@@TEMPLATE@@@

    return E[target];
}

int main(int argc, char** argv) {
    for (int file_index = 1; file_index < argc; ++file_index) {
        ifstream input(argv[file_index]);
        int n, m, target;
        double expected;
        while (input >> n >> m >> target >> expected) {
            vector<vector<pair<int, double>>> transitions(n);
            for (int edge = 0; edge < m; ++edge) {
                int u, v;
                double probability;
                input >> u >> v >> probability;
                transitions[u].push_back({v, probability});
            }
            double actual = run_template(transitions, target);
            if (fabs(actual - expected) > 1e-12) {
                cerr << "expected=" << expected << " actual=" << actual << '\n';
                return 1;
            }
        }
    }
    cout << "expected-DP terminal regressions passed\n";
    return 0;
}
