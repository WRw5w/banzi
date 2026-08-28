#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

int main(int argc, char** argv) {
    for (int file_index = 1; file_index < argc; ++file_index) {
        ifstream input(argv[file_index]);
        int n, expected;
        while (input >> n) {
            vector<int> piles(n);
            for (int& pile : piles) input >> pile;
            input >> expected;
            int actual = misere_nim_first_win(piles);
            if (actual != expected) {
                cerr << "expected=" << expected << " actual=" << actual << '\n';
                return 1;
            }
        }
    }
    cout << "misere Nim regressions passed\n";
    return 0;
}
