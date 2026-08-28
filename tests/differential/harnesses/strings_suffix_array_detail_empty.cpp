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

using std::iota;
using std::sort;
using std::string;
using std::swap;

// @@@TEMPLATE@@@

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    std::ifstream input(argv[1]);
    std::string value;
    while (input >> std::quoted(value)) {
        try {
            auto actual = suffix_array(value);
            if (!actual.empty()) return 1;
        } catch (const std::out_of_range&) {
            std::cerr << "input=\"\" empty_suffix_array_bounds_error\n";
            return 1;
        }
    }
    return 0;
}
