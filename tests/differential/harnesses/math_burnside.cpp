#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

vector<vector<int>> cyclic_group(int n) {
    vector<vector<int>> group;
    for (int shift = 0; shift < n; ++shift) {
        vector<int> permutation(n);
        for (int i = 0; i < n; ++i) permutation[i] = (i + shift) % n;
        group.push_back(permutation);
    }
    return group;
}

long long necklace_count(int n, int colors) {
    long long fixed_sum = 0;
    for (int shift = 0; shift < n; ++shift) {
        long long fixed = 1;
        for (int i = 0; i < gcd(n, shift); ++i) fixed *= colors;
        fixed_sum += fixed;
    }
    return fixed_sum / n;
}

int main(int argc, char** argv) {
    for (int file_index = 1; file_index < argc; ++file_index) {
        ifstream input(argv[file_index]);
        if (!input) {
            cerr << "cannot open regression file: " << argv[file_index] << '\n';
            return 2;
        }
        int n, colors;
        long long mod, expected;
        while (input >> n >> colors >> mod >> expected) {
            long long actual = burnside(cyclic_group(n), colors, mod);
            if (actual != expected) {
                cerr << "n=" << n << " colors=" << colors << " mod=" << mod
                     << " expected=" << expected << " actual=" << actual << '\n';
                return 1;
            }
        }
    }

    const long long mod = 1000000007;
    for (int n = 1; n <= 9; ++n) {
        for (int colors = 1; colors <= 5; ++colors) {
            long long expected = necklace_count(n, colors) % mod;
            long long actual = burnside(cyclic_group(n), colors, mod);
            if (actual != expected) {
                cerr << "prime-mod n=" << n << " colors=" << colors
                     << " expected=" << expected << " actual=" << actual << '\n';
                return 1;
            }
        }
    }
    cout << "Burnside cyclic groups: PASS\n";
    return 0;
}
