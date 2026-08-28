#include <bits/stdc++.h>
using namespace std;

constexpr int MAXNODE = 256;
constexpr int MAXN = 8;

// @@@TEMPLATE@@@

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    ifstream input(argv[1]);
    int bit;
    unsigned long long value;
    while (input >> bit >> value) {
        tot = 0;
        memset(tr, 0, sizeof(tr));
        int right_root = insert(0, bit, value);
        unsigned long long actual = max_xor(0, right_root, bit, 0);
        unsigned long long expected = value;
        if (actual != expected) {
            cerr << "bit=" << bit << " value=" << value << " expected=" << expected
                 << " actual=" << actual << " int_interface_truncates_high_bits\n";
            return 1;
        }
    }
    return 0;
}
