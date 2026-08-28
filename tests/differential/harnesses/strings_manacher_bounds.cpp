#include <bits/stdc++.h>

class string {
    std::string value_;
public:
    string() = default;
    string(const char* value): value_(value) {}
    explicit string(std::string value): value_(std::move(value)) {}
    string& operator+=(char value) { value_ += value; return *this; }
    std::size_t size() const { return value_.size(); }
    auto begin() const { return value_.begin(); }
    auto end() const { return value_.end(); }
    char operator[](long long index) const {
        if (index < 0 || index >= (long long)value_.size())
            throw std::out_of_range("checked string index");
        return value_[(std::size_t)index];
    }
    const std::string& raw() const { return value_; }
};

using std::min;
using std::vector;

int board_longest_palindrome(const string& s) {
// @@@TEMPLATE@@@
    return p.empty() ? 0 : *std::max_element(p.begin(), p.end());
}

int brute_longest_palindrome(const std::string& s) {
    int answer = 0;
    for (int l = 0; l < (int)s.size(); ++l)
        for (int r = l; r < (int)s.size(); ++r) {
            bool palindrome = true;
            for (int a = l, b = r; a < b; ++a, --b)
                palindrome &= s[a] == s[b];
            if (palindrome) answer = std::max(answer, r - l + 1);
        }
    return answer;
}

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    std::ifstream input(argv[1]);
    std::string raw;
    while (input >> std::quoted(raw)) {
        try {
            int actual = board_longest_palindrome(string(raw));
            int expected = brute_longest_palindrome(raw);
            if (actual != expected) {
                std::cerr << "input=" << std::quoted(raw) << " expected=" << expected
                          << " actual=" << actual << '\n';
                return 1;
            }
        } catch (const std::out_of_range&) {
            std::cerr << "input=" << std::quoted(raw) << " bounds_error\n";
            return 1;
        }
    }
    return 0;
}
