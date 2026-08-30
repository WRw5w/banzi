#include <bits/stdc++.h>

template<class T>
class vector : public std::vector<T> {
    using Base = std::vector<T>;
public:
    using Base::Base;
    T& operator[](std::size_t index) {
        if (index >= Base::size()) throw std::out_of_range("checked vector index");
        return Base::operator[](index);
    }
    const T& operator[](std::size_t index) const {
        if (index >= Base::size()) throw std::out_of_range("checked vector index");
        return Base::operator[](index);
    }
};

using std::min;
using std::swap;

// @@@TEMPLATE@@@

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    std::ifstream input(argv[1]);
    int left, right, x;
    while (input >> left >> right >> x) {
        try {
            LiChao tree(left, right);
            __int128 actual = tree.query(x);
            __int128 expected = (__int128)1 << 126;
            if (actual != expected) return 1;
        } catch (const std::out_of_range&) {
            std::cerr << "domain=[" << left << ',' << right << "] x=" << x
                      << " non_shrinking_recursion\n";
            return 1;
        }
    }
    return 0;
}
