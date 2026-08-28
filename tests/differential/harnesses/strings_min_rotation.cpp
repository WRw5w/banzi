#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

int main() {
    const uint64_t seed = 0xB0074ULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 30000; ++round) {
        string s;
        for (int i = 0, n = rng() % 40; i < n; ++i) s += "abcd"[rng() % 4];
        int actual_index = min_rotation(s);
        string actual = s.empty() ? string() : (s + s).substr(actual_index, s.size());
        string expected = actual;
        for (int i = 0; i < (int)s.size(); ++i)
            expected = min(expected, (s + s).substr(i, s.size()));
        if (actual != expected) {
            cerr << "seed=" << seed << " round=" << round << " input=" << quoted(s)
                 << " index=" << actual_index << '\n';
            return 1;
        }
    }
    cout << "rounds=30000 seed=" << seed << '\n';
}
