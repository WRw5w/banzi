#include <bits/stdc++.h>
using namespace std;

const long double EPS = 1e-12L;
struct Point {
    long double x, y;
    Point operator+(Point other) const { return {x + other.x, y + other.y}; }
    Point operator-(Point other) const { return {x - other.x, y - other.y}; }
    Point operator*(long double scale) const { return {x * scale, y * scale}; }
};

// @@@TEMPLATE@@@

int main() { return 0; }
