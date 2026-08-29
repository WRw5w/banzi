#include <bits/stdc++.h>
using namespace std;

const int n = 100;

// @@@TEMPLATE@@@

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    ifstream input(argv[1]);
    int l, r, index;
    long long a, b, expected;
    while (input >> l >> r >> a >> b >> index >> expected) {
        fill(da.begin(), da.end(), 0);
        fill(db.begin(), db.end(), 0);
        range_add_linear(l, r, a, b);
        long long actual = build_linear_values()[index];
        if (actual != expected) {
            cerr << "index=" << index << " expected=" << expected
                 << " actual=" << actual << '\n';
            return 1;
        }
    }
    return 0;
}
