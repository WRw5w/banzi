#include <bits/stdc++.h>
using namespace std;

constexpr int MAXN = 64;

// @@@TEMPLATE@@@

int main() {
    const uint64_t seed = 0x5A4DULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 15000; ++round) {
        string s;
        for (int i = 0, n = rng() % 18; i < n; ++i) s += "abc"[rng() % 3];
        SAM automaton;
        for (char c : s) automaton.extend(c);
        long long actual = 0;
        for (int v = 1; v < automaton.sz; ++v)
            actual += automaton.st[v].len - automaton.st[automaton.st[v].link].len;
        set<string> distinct;
        for (int l = 0; l < (int)s.size(); ++l)
            for (int r = l; r < (int)s.size(); ++r)
                distinct.insert(s.substr(l, r - l + 1));
        if (actual != (long long)distinct.size()) {
            cerr << "seed=" << seed << " round=" << round << " input=" << quoted(s)
                 << " expected=" << distinct.size() << " actual=" << actual << '\n';
            return 1;
        }
    }
    cout << "rounds=15000 seed=" << seed << '\n';
}
