#include <bits/stdc++.h>
#include <cassert>
using namespace std;

// @@@TEMPLATE@@@

string i128_text(__int128 value) {
    if (value == 0) return "0";
    bool negative = value < 0;
    if (negative) value = -value;
    string result;
    while (value != 0) {
        result.push_back(char('0' + value % 10));
        value /= 10;
    }
    if (negative) result.push_back('-');
    reverse(result.begin(), result.end());
    return result;
}

int main() {
    const uint64_t seed = 0xB161A7E20260828ULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 5000; ++round) {
        long long x = (long long)(rng() & ((1ULL << 60) - 1));
        long long y = (long long)(rng() & ((1ULL << 60) - 1));
        if (rng() & 1) x = -x;
        if (rng() & 1) y = -y;
        if (y == 0) y = 1;
        BigInteger a(to_string(x)), b(to_string(y));

        array<pair<string, string>, 5> checks{{
            {(a + b).str(), i128_text((__int128)x + y)},
            {(a - b).str(), i128_text((__int128)x - y)},
            {(a * b).str(), i128_text((__int128)x * y)},
            {(a / b).str(), i128_text((__int128)x / y)},
            {(a % b).str(), i128_text((__int128)x % y)},
        }};
        for (int operation = 0; operation < (int)checks.size(); ++operation) {
            if (checks[operation].first != checks[operation].second) {
                cerr << "seed=" << seed << " round=" << round
                     << " operation=" << operation << " x=" << x << " y=" << y
                     << " expected=" << checks[operation].second
                     << " actual=" << checks[operation].first << '\n';
                return 1;
            }
        }
    }

    if (BigInteger(LLONG_MIN).str() != to_string(LLONG_MIN)) {
        cerr << "LLONG_MIN constructor mismatch\n";
        return 1;
    }
    if (pow_mod_big(BigInteger(-2), BigInteger(5), BigInteger(13)).str() != "7") {
        cerr << "pow_mod_big signed-base regression\n";
        return 1;
    }
    cout << "rounds=5000 seed=" << seed << '\n';
    return 0;
}
