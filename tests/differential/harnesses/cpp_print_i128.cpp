#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

int main(int argc, char** argv) {
    i128 minimum = -((i128)1 << 126);
    minimum *= 2;

    ostringstream captured;
    streambuf* previous = cout.rdbuf(captured.rdbuf());
    print_i128(minimum);
    cout.rdbuf(previous);

    string expected = "-170141183460469231731687303715884105728";
    if (argc > 1) {
        ifstream input(argv[1]);
        if (!input || !(input >> expected)) {
            cerr << "cannot read print_i128 regression\n";
            return 2;
        }
    }
    if (captured.str() != expected) {
        cerr << "print_i128(INT128_MIN) mismatch\n";
        return 1;
    }

    cout << "print_i128 edge cases: PASS\n";
    return 0;
}
