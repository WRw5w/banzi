#pragma once

#include <bits/stdc++.h>

struct BigInteger {
    static constexpr uint32_t BASE = 1000000000;
    static constexpr int WIDTH = 9;
    std::vector<uint32_t> digit;
    bool negative = false;

    BigInteger(long long value = 0) { *this = value; }
    explicit BigInteger(const std::string &text) { read(text); }

    BigInteger &operator=(long long value) {
        digit.clear();
        negative = value < 0;
        unsigned long long magnitude = negative
            ? 0ULL - static_cast<unsigned long long>(value)
            : static_cast<unsigned long long>(value);
        while (magnitude != 0) {
            digit.push_back(magnitude % BASE);
            magnitude /= BASE;
        }
        trim();
        return *this;
    }

    void read(const std::string &text) {
        digit.clear();
        negative = false;
        if (text.empty()) throw std::invalid_argument("empty BigInteger");
        size_t pos = 0;
        if (text[pos] == '+' || text[pos] == '-') {
            negative = text[pos] == '-';
            ++pos;
        }
        if (pos == text.size()) throw std::invalid_argument("invalid BigInteger");
        for (size_t i = pos; i < text.size(); ++i) {
            if (!std::isdigit(static_cast<unsigned char>(text[i])))
                throw std::invalid_argument("invalid BigInteger");
        }
        for (size_t end = text.size(); end > pos;) {
            size_t begin = end >= pos + WIDTH ? end - WIDTH : pos;
            digit.push_back(static_cast<uint32_t>(std::stoul(
                text.substr(begin, end - begin))));
            end = begin;
        }
        trim();
    }

    std::string str() const {
        if (digit.empty()) return "0";
        std::stringstream out;
        if (negative) out << '-';
        out << digit.back();
        for (int i = static_cast<int>(digit.size()) - 2; i >= 0; --i)
            out << std::setw(WIDTH) << std::setfill('0') << digit[i];
        return out.str();
    }

    bool is_zero() const { return digit.empty(); }
    bool is_odd() const { return !digit.empty() && (digit[0] & 1); }

    void divide_by_two() {
        assert(!negative);
        uint64_t carry = 0;
        for (int i = static_cast<int>(digit.size()) - 1; i >= 0; --i) {
            uint64_t current = digit[i] + carry * BASE;
            digit[i] = current / 2;
            carry = current % 2;
        }
        trim();
    }

    void trim() {
        while (!digit.empty() && digit.back() == 0) digit.pop_back();
        if (digit.empty()) negative = false;
    }

    static int abs_compare(const BigInteger &a, const BigInteger &b) {
        if (a.digit.size() != b.digit.size())
            return a.digit.size() < b.digit.size() ? -1 : 1;
        for (int i = static_cast<int>(a.digit.size()) - 1; i >= 0; --i) {
            if (a.digit[i] != b.digit[i])
                return a.digit[i] < b.digit[i] ? -1 : 1;
        }
        return 0;
    }

    static BigInteger abs_add(const BigInteger &a, const BigInteger &b) {
        BigInteger result;
        uint64_t carry = 0;
        size_t size = std::max(a.digit.size(), b.digit.size());
        for (size_t i = 0; i < size || carry != 0; ++i) {
            uint64_t current = carry;
            if (i < a.digit.size()) current += a.digit[i];
            if (i < b.digit.size()) current += b.digit[i];
            result.digit.push_back(current % BASE);
            carry = current / BASE;
        }
        return result;
    }

    static BigInteger abs_sub(const BigInteger &a, const BigInteger &b) {
        assert(abs_compare(a, b) >= 0);
        BigInteger result;
        int64_t borrow = 0;
        for (size_t i = 0; i < a.digit.size(); ++i) {
            int64_t current = static_cast<int64_t>(a.digit[i]) - borrow
                - (i < b.digit.size() ? b.digit[i] : 0);
            if (current < 0) current += BASE, borrow = 1;
            else borrow = 0;
            result.digit.push_back(static_cast<uint32_t>(current));
        }
        result.trim();
        return result;
    }

    BigInteger multiply_small(uint32_t factor) const {
        BigInteger result;
        if (factor == 0 || is_zero()) return result;
        uint64_t carry = 0;
        for (uint32_t block : digit) {
            uint64_t current = static_cast<uint64_t>(block) * factor + carry;
            result.digit.push_back(current % BASE);
            carry = current / BASE;
        }
        if (carry != 0) result.digit.push_back(static_cast<uint32_t>(carry));
        return result;
    }

    void shift_base_add(uint32_t block) {
        assert(!negative && block < BASE);
        digit.insert(digit.begin(), block);
        trim();
    }

    static std::pair<BigInteger, BigInteger> divmod(
            const BigInteger &a, const BigInteger &b) {
        if (b.is_zero()) throw std::domain_error("BigInteger division by zero");
        BigInteger dividend = a.negative ? -a : a;
        BigInteger divisor = b.negative ? -b : b;
        BigInteger quotient, remainder;
        quotient.digit.assign(dividend.digit.size(), 0);
        for (int i = static_cast<int>(dividend.digit.size()) - 1;
             i >= 0; --i) {
            remainder.shift_base_add(dividend.digit[i]);
            uint32_t low = 0, high = BASE - 1, best = 0;
            while (low <= high) {
                uint32_t middle = low + (high - low) / 2;
                if (abs_compare(divisor.multiply_small(middle), remainder) <= 0) {
                    best = middle;
                    low = middle + 1;
                } else {
                    if (middle == 0) break;
                    high = middle - 1;
                }
            }
            quotient.digit[i] = best;
            remainder = abs_sub(remainder, divisor.multiply_small(best));
        }
        quotient.negative = a.negative != b.negative;
        remainder.negative = a.negative;
        quotient.trim();
        remainder.trim();
        return {quotient, remainder};
    }

    BigInteger operator-() const {
        BigInteger result = *this;
        if (!result.is_zero()) result.negative = !result.negative;
        return result;
    }

    friend BigInteger operator+(const BigInteger &a, const BigInteger &b) {
        if (a.negative == b.negative) {
            BigInteger result = abs_add(a, b);
            result.negative = a.negative;
            result.trim();
            return result;
        }
        int order = abs_compare(a, b);
        if (order == 0) return BigInteger(0);
        BigInteger result = order > 0 ? abs_sub(a, b) : abs_sub(b, a);
        result.negative = order > 0 ? a.negative : b.negative;
        return result;
    }

    friend BigInteger operator-(const BigInteger &a, const BigInteger &b) {
        return a + (-b);
    }

    friend BigInteger operator*(const BigInteger &a, const BigInteger &b) {
        BigInteger result;
        if (a.is_zero() || b.is_zero()) return result;
        result.digit.assign(a.digit.size() + b.digit.size(), 0);
        for (size_t i = 0; i < a.digit.size(); ++i) {
            uint64_t carry = 0;
            for (size_t j = 0; j < b.digit.size() || carry != 0; ++j) {
                uint64_t current = result.digit[i + j] + carry;
                if (j < b.digit.size())
                    current += static_cast<uint64_t>(a.digit[i]) * b.digit[j];
                result.digit[i + j] = current % BASE;
                carry = current / BASE;
            }
        }
        result.negative = a.negative != b.negative;
        result.trim();
        return result;
    }

    friend BigInteger operator/(const BigInteger &a, const BigInteger &b) {
        return divmod(a, b).first;
    }

    friend BigInteger operator%(const BigInteger &a, const BigInteger &b) {
        return divmod(a, b).second;
    }

    friend bool operator==(const BigInteger &a, const BigInteger &b) {
        return a.negative == b.negative && a.digit == b.digit;
    }

    friend bool operator!=(const BigInteger &a, const BigInteger &b) {
        return !(a == b);
    }

    friend bool operator<(const BigInteger &a, const BigInteger &b) {
        if (a.negative != b.negative) return a.negative;
        int order = abs_compare(a, b);
        return a.negative ? order > 0 : order < 0;
    }

    friend bool operator<=(const BigInteger &a, const BigInteger &b) {
        return !(b < a);
    }

    friend bool operator>(const BigInteger &a, const BigInteger &b) {
        return b < a;
    }

    friend bool operator>=(const BigInteger &a, const BigInteger &b) {
        return !(a < b);
    }

    friend std::istream &operator>>(std::istream &in, BigInteger &value) {
        std::string text;
        if (in >> text) value.read(text);
        return in;
    }

    friend std::ostream &operator<<(std::ostream &out, const BigInteger &value) {
        return out << value.str();
    }
};

inline BigInteger abs_big(BigInteger x) {
    return x < 0 ? -x : x;
}

inline BigInteger gcd_big(BigInteger a, BigInteger b) {
    a = abs_big(a);
    b = abs_big(b);
    while (!b.is_zero()) {
        BigInteger remainder = a % b;
        a = b;
        b = remainder;
    }
    return a;
}

inline BigInteger pow_mod_big(
        BigInteger base, BigInteger exponent, const BigInteger &mod) {
    assert(!(exponent < 0) && 0 < mod);
    base = base % mod;
    if (base < 0) base = base + mod;
    BigInteger result = BigInteger(1) % mod;
    while (!exponent.is_zero()) {
        if (exponent.is_odd()) result = result * base % mod;
        base = base * base % mod;
        exponent.divide_by_two();
    }
    return result;
}
