#include <bits/stdc++.h>
using namespace std;

long long qpow(long long a, long long e, long long mod) {
    long long result = 1 % mod;
    for (; e; e >>= 1) {
        if (e & 1) result = (long long)((__int128)result * a % mod);
        a = (long long)((__int128)a * a % mod);
    }
    return result;
}

// @@@TEMPLATE@@@

int main() {
    vector<int> value{1, 2, 3, 0};
    ntt(value, false);
}
