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

using std::max;
using std::min;
using std::swap;

// @@@TEMPLATE@@@

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    std::ifstream input(argv[1]);
    long long value, cap;
    while (input >> value >> cap) {
        vector<long long> a(2); a[1] = value;
        try {
            SegBeats tree(a);
            tree.chmin(1, 1, cap);
            long long actual = tree.query_sum(1, 1);
            if (actual != cap) return 1;
        } catch (const std::out_of_range&) {
            std::cerr << "value=" << value << " cap=" << cap
                      << " sentinel_recursion\n";
            return 1;
        }
    }
    return 0;
}
