#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

vector<int> brute_prefix_function(const string& s) {
    vector<int> answer(s.size());
    for (int i = 0; i < (int)s.size(); ++i) {
        for (int length = 1; length <= i; ++length) {
            if (s.substr(0, length) == s.substr(i - length + 1, length)) {
                answer[i] = length;
            }
        }
    }
    return answer;
}

int main() {
    const uint64_t seed = 0x5A17C0DEULL;
    mt19937_64 rng(seed);
    const string alphabet = "ab#";
    for (int round = 0; round < 20000; ++round) {
        int n = (int)(rng() % 24);
        string s;
        for (int i = 0; i < n; ++i) s.push_back(alphabet[rng() % alphabet.size()]);
        vector<int> actual = prefix_function(s);
        vector<int> expected = brute_prefix_function(s);
        if (actual != expected) {
            cerr << "seed=" << seed << " round=" << round << " input=" << quoted(s) << '\n';
            return 1;
        }
    }
    cout << "rounds=20000 seed=" << seed << '\n';
    return 0;
}
