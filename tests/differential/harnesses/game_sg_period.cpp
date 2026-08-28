#include <bits/stdc++.h>
using namespace std;

// @@@TEMPLATE@@@

int main(int argc, char** argv) {
    for (int file_index = 1; file_index < argc; ++file_index) {
        ifstream input(argv[file_index]);
        int last_index, real_period, expected;
        while (input >> last_index >> real_period >> expected) {
            vector<int> sg(last_index + 1);
            for (int i = 0; i <= last_index; ++i) sg[i] = i % real_period;
            int actual = find_period(sg);
            if (actual != expected) {
                cerr << "expected=" << expected << " actual=" << actual << '\n';
                return 1;
            }
        }
    }
    cout << "SG period regressions passed\n";
    return 0;
}
