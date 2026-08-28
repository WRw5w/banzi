#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

int main() {
    const uint64_t seed = 0xB17A1EULL;
    mt19937_64 rng(seed);
    auto trie = make_unique<BinaryTrie>();
    vector<int> values;
    for (int op = 0; op < 5000; ++op) {
        if (values.empty() || (rng() & 1)) {
            int value = rng() & 0x7fffffff;
            trie->insert(value); values.push_back(value);
        } else {
            int x = rng() & 0x7fffffff, expected = 0;
            for (int value : values) expected = max(expected, value ^ x);
            int actual = trie->max_xor(x);
            if (actual != expected) {
                cerr << "seed=" << seed << " op=" << op << " x=" << x
                     << " expected=" << expected << " actual=" << actual << '\n';
                return 1;
            }
        }
    }
    cout << "operations=5000 seed=" << seed << '\n';
}
