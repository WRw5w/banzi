#include <bits/stdc++.h>
using namespace std;

long long mod_pow(long long a, long long e, long long mod) {
    a %= mod;
    if (a < 0) a += mod;
    long long result = 1 % mod;
    while (e != 0) {
        if (e & 1) result = (long long)((__int128)result * a % mod);
        a = (long long)((__int128)a * a % mod);
        e >>= 1;
    }
    return result;
}

// @@@TEMPLATE@@@

int brute_rank(vector<vector<long long>> matrix, long long mod) {
    int n = (int)matrix.size();
    int m = (int)matrix[0].size();
    for (auto& row : matrix)
        for (auto& value : row) value = (value % mod + mod) % mod;
    int rank = 0;
    for (int column = 0; column < m && rank < n; ++column) {
        int pivot = rank;
        while (pivot < n && matrix[pivot][column] == 0) ++pivot;
        if (pivot == n) continue;
        swap(matrix[pivot], matrix[rank]);
        long long inverse = mod_pow(matrix[rank][column], mod - 2, mod);
        for (int j = column; j < m; ++j)
            matrix[rank][j] = matrix[rank][j] * inverse % mod;
        for (int i = 0; i < n; ++i) if (i != rank && matrix[i][column] != 0) {
            long long factor = matrix[i][column];
            for (int j = column; j < m; ++j)
                matrix[i][j] = (matrix[i][j] - factor * matrix[rank][j] % mod + mod) % mod;
        }
        ++rank;
    }
    return rank;
}

int main(int argc, char** argv) {
    for (int file_index = 1; file_index < argc; ++file_index) {
        ifstream input(argv[file_index]);
        if (!input) {
            cerr << "cannot open regression file: " << argv[file_index] << '\n';
            return 2;
        }
        int n, m;
        long long mod, expected;
        while (input >> n >> m >> mod >> expected) {
            vector<vector<long long>> matrix(n, vector<long long>(m));
            for (auto& row : matrix) for (auto& value : row) input >> value;
            int actual = gauss_mod(matrix, mod);
            if (actual != expected) {
                cerr << "n=" << n << " m=" << m << " mod=" << mod
                     << " expected=" << expected << " actual=" << actual << '\n';
                return 1;
            }
        }
    }

    const uint64_t seed = 0x6A05520260828ULL;
    mt19937_64 rng(seed);
    const long long mod = 7;
    for (int round = 0; round < 3000; ++round) {
        int n = 1 + int(rng() % 5), m = 1 + int(rng() % 5);
        vector<vector<long long>> matrix(n, vector<long long>(m));
        for (auto& row : matrix)
            for (auto& value : row) value = (long long)(rng() % 15) - 7;
        int expected = brute_rank(matrix, mod);
        int actual = gauss_mod(matrix, mod);
        if (actual != expected) {
            cerr << "seed=" << seed << " round=" << round
                 << " expected=" << expected << " actual=" << actual << '\n';
            return 1;
        }
    }
    cout << "rounds=3000 seed=" << seed << '\n';
    return 0;
}
