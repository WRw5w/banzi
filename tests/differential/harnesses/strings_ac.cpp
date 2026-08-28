#include <bits/stdc++.h>
using namespace std;

constexpr int MAXN = 256;

// @@@TEMPLATE@@@

int main() {
    const uint64_t seed = 0xACACULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 10000; ++round) {
        int pattern_count = 1 + rng() % 8;
        vector<string> patterns;
        AC automaton;
        for (int id = 0; id < pattern_count; ++id) {
            string pattern;
            for (int i = 0, n = 1 + rng() % 6; i < n; ++i) pattern += "abc"[rng() % 3];
            patterns.push_back(pattern); automaton.insert(pattern);
        }
        automaton.build();
        string text;
        for (int i = 0, n = rng() % 30; i < n; ++i) text += "abc"[rng() % 3];
        int expected = 0;
        for (const string& pattern : patterns)
            for (int i = 0; i + (int)pattern.size() <= (int)text.size(); ++i)
                expected += text.compare(i, pattern.size(), pattern) == 0;
        int actual = automaton.query(text);
        if (actual != expected) {
            cerr << "seed=" << seed << " round=" << round << " text=" << quoted(text)
                 << " expected=" << expected << " actual=" << actual << '\n';
            return 1;
        }
    }
    cout << "rounds=10000 seed=" << seed << '\n';
}
