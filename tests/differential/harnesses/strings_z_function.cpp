#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

vector<int> brute_z(const string& s) {
    vector<int> answer(s.size());
    if (!s.empty()) answer[0] = s.size();
    for (int i = 1; i < (int)s.size(); ++i)
        while (i + answer[i] < (int)s.size() && s[answer[i]] == s[i + answer[i]])
            ++answer[i];
    return answer;
}

int main(int argc, char** argv) {
    for (int file_index = 1; file_index < argc; ++file_index) {
        ifstream input(argv[file_index]);
        string s; int expected_z0;
        while (input >> quoted(s) >> expected_z0) {
            auto actual = z_function(s);
            int actual_z0 = actual.empty() ? 0 : actual[0];
            if (actual_z0 != expected_z0) {
                cerr << "input=" << quoted(s) << " expected_z0=" << expected_z0
                     << " actual_z0=" << actual_z0 << '\n';
                return 1;
            }
        }
    }
    const uint64_t seed = 0x2F00C710ULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 30000; ++round) {
        string s;
        for (int i = 0, n = rng() % 40; i < n; ++i) s += "abc"[rng() % 3];
        auto expected = brute_z(s), actual = z_function(s);
        if (actual != expected) {
            cerr << "seed=" << seed << " round=" << round << " input=" << quoted(s) << '\n';
            return 1;
        }
    }
    cout << "rounds=30000 seed=" << seed << '\n';
}
