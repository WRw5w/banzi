#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

int main() {
    const uint64_t seed = 0xB451520260828ULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 500; ++round) {
        int n = 1 + int(rng() % 13);
        vector<unsigned long long> values(n);
        LinearBasis<20> basis;
        for (auto& value : values) {
            value = rng() & ((1ULL << 20) - 1);
            basis.insert(value);
        }

        vector<unsigned long long> generated{0};
        for (auto value : values) {
            size_t old_size = generated.size();
            for (size_t i = 0; i < old_size; ++i)
                generated.push_back(generated[i] ^ value);
        }
        sort(generated.begin(), generated.end());
        generated.erase(unique(generated.begin(), generated.end()), generated.end());

        for (int query = 0; query < 20; ++query) {
            unsigned long long x = rng() & ((1ULL << 20) - 1);
            bool expected_can = binary_search(generated.begin(), generated.end(), x);
            if (basis.can(x) != expected_can) {
                cerr << "seed=" << seed << " round=" << round
                     << " can query=" << x << '\n';
                return 1;
            }
            unsigned long long expected_max = 0;
            for (auto value : generated) expected_max = max(expected_max, x ^ value);
            if (basis.max_xor(x) != expected_max) {
                cerr << "seed=" << seed << " round=" << round
                     << " max query=" << x << " expected=" << expected_max
                     << " actual=" << basis.max_xor(x) << '\n';
                return 1;
            }
        }
    }
    cout << "rounds=500 seed=" << seed << '\n';
    return 0;
}
