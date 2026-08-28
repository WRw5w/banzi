#include <bits/stdc++.h>
using namespace std;

constexpr int MAXN = 64;

// @@@TEMPLATE@@@

int main() {
    const uint64_t seed = 0x50414DULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 15000; ++round) {
        string s;
        for (int i = 0, n = rng() % 18; i < n; ++i) s += "abc"[rng() % 3];
        PAM automaton;
        int actual = automaton.build(s);
        set<string> distinct;
        for (int l = 0; l < (int)s.size(); ++l)
            for (int r = l; r < (int)s.size(); ++r) {
                string part = s.substr(l, r - l + 1);
                string reversed = part; reverse(reversed.begin(), reversed.end());
                if (part == reversed) distinct.insert(part);
            }
        if (actual != (int)distinct.size()) {
            cerr << "seed=" << seed << " round=" << round << " input=" << quoted(s)
                 << " expected=" << distinct.size() << " actual=" << actual << '\n';
            return 1;
        }
    }
    cout << "rounds=15000 seed=" << seed << '\n';
}
