#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

vector<int> brute_matches(const string& text, const string& pattern) {
    vector<int> answer;
    if (pattern.empty()) return answer;
    for (int i = 0; i + (int)pattern.size() <= (int)text.size(); ++i)
        if (text.compare(i, pattern.size(), pattern) == 0) answer.push_back(i);
    return answer;
}

string show(const vector<int>& values) {
    string result = "[";
    for (int i = 0; i < (int)values.size(); ++i) {
        if (i) result += ',';
        result += to_string(values[i]);
    }
    return result + ']';
}

int main(int argc, char** argv) {
    for (int file_index = 1; file_index < argc; ++file_index) {
        ifstream input(argv[file_index]);
        string text, pattern; int expected_start;
        while (input >> quoted(text) >> quoted(pattern) >> expected_start) {
            vector<int> expected{expected_start};
            vector<int> actual = kmp(text, pattern);
            if (actual != expected) {
                cerr << "pattern=" << quoted(pattern) << " expected=" << show(expected)
                     << " actual=" << show(actual) << '\n';
                return 1;
            }
        }
    }
    const uint64_t seed = 0x4B4D50ULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 30000; ++round) {
        int n = rng() % 30, m = 1 + rng() % 10;
        string text, pattern;
        for (int i = 0; i < n; ++i) text += "ab#"[rng() % 3];
        for (int i = 0; i < m; ++i) pattern += "ab#"[rng() % 3];
        auto expected = brute_matches(text, pattern), actual = kmp(text, pattern);
        if (actual != expected) {
            cerr << "seed=" << seed << " round=" << round << " pattern=" << quoted(pattern)
                 << " expected=" << show(expected) << " actual=" << show(actual) << '\n';
            return 1;
        }
    }
    cout << "rounds=30000 seed=" << seed << '\n';
}
