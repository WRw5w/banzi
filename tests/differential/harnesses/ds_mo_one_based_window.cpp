#include <bits/stdc++.h>
using namespace std;

struct InvalidMoIndex : exception {};

struct CheckedValues {
    vector<int> values{0, 7};
    int operator[](int index) const {
        if (index < 1 || index >= (int)values.size()) throw InvalidMoIndex{};
        return values[index];
    }
} a;

struct RawQuery {
    int l, r, id;
    template<class T> operator T() const { return T{l, r, id}; }
};

int block_value() { return 1; }
#define block block_value()

int main() {
    vector<RawQuery> qs{{1, 1, 0}};
    vector<int> cnt(16), answer(1);
    try {
// @@@TEMPLATE@@@
    } catch (const InvalidMoIndex&) {
        cerr << "query=[1,1] invalid_position=0 from_initial_window=[0,-1]\n";
        return 1;
    }
    if (answer[0] != 1) {
        cerr << "query=[1,1] expected=1 actual=" << answer[0] << '\n';
        return 1;
    }
    return 0;
}

#undef block
