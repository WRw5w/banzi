#include <bits/stdc++.h>
using namespace std;

constexpr int MAXN = 4096;

// @@@TEMPLATE@@@

int main() {
    const uint64_t seed = 0x7A1EULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 5000; ++round) {
        StringTrie trie;
        vector<string> inserted;
        int string_count = rng() % 40;
        for (int id = 0; id < string_count; ++id) {
            string s;
            for (int i = 0, n = rng() % 9; i < n; ++i)
                s += "abcd"[rng() % 4];
            trie.insert(s);
            inserted.push_back(s);
        }

        for (int query_id = 0; query_id < 80; ++query_id) {
            string query;
            for (int i = 0, n = rng() % 9; i < n; ++i)
                query += "abcde"[rng() % 5];

            int expected_word = 0, expected_prefix = 0;
            for (const string& s : inserted) {
                expected_word += s == query;
                expected_prefix += s.size() >= query.size()
                    && s.compare(0, query.size(), query) == 0;
            }
            int actual_word = trie.count_word(query);
            int actual_prefix = trie.count_prefix(query);
            if (actual_word != expected_word || actual_prefix != expected_prefix) {
                cerr << "seed=" << seed << " round=" << round
                     << " query=" << quoted(query)
                     << " expected_word=" << expected_word
                     << " actual_word=" << actual_word
                     << " expected_prefix=" << expected_prefix
                     << " actual_prefix=" << actual_prefix << '\n';
                return 1;
            }
        }
    }
    cout << "rounds=5000 seed=" << seed << '\n';
}
