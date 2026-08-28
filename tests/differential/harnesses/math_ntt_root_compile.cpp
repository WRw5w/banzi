#include <bits/stdc++.h>
using namespace std;

constexpr int MOD = 998244353;

long long qpow(long long a, long long e) {
    long long result = 1;
    for (; e; e >>= 1) {
        if (e & 1) result = result * a % MOD;
        a = a * a % MOD;
    }
    return result;
}

// @@@TEMPLATE@@@

int main() {
    vector<int> value{1, 2, 3, 0};
    ntt(value, false);
}
