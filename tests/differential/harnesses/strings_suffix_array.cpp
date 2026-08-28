#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

vector<int> brute_suffix_array(const string& s) {
    vector<int> answer(s.size());
    iota(answer.begin(), answer.end(), 0);
    sort(answer.begin(), answer.end(), [&](int a, int b) {
        return s.substr(a) < s.substr(b);
    });
    return answer;
}

int main() {
    const uint64_t seed = 0x5AFF1AULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 30000; ++round) {
        string s;
        for (int i = 0, n = rng() % 35; i < n; ++i) s += "abcd"[rng() % 4];
        auto expected = brute_suffix_array(s), actual = suffix_array(s);
        if (actual != expected) {
            cerr << "seed=" << seed << " round=" << round << " input=" << quoted(s) << '\n';
            return 1;
        }
    }
    cout << "rounds=30000 seed=" << seed << '\n';
}
