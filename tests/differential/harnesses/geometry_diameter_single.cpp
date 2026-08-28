#define _GLIBCXX_ASSERTIONS
#include <bits/stdc++.h>
using namespace std;

struct Point {
    long double x, y;
    Point operator-(Point other) const { return {x - other.x, y - other.y}; }
};
long double cross(Point a, Point b) { return a.x * b.y - a.y * b.x; }
long double dist2(Point a, Point b) {
    Point d = a - b;
    return d.x * d.x + d.y * d.y;
}

// @@@TEMPLATE@@@

int main(int argc, char** argv) {
    for (int file_index = 1; file_index < argc; ++file_index) {
        ifstream input(argv[file_index]);
        int n;
        long double expected;
        while (input >> n) {
            vector<Point> polygon(n);
            for (Point& point : polygon) input >> point.x >> point.y;
            input >> expected;
            long double actual = diameter2(polygon);
            if (fabsl(actual - expected) > 1e-12L) {
                cerr << "expected=" << expected << " actual=" << actual << '\n';
                return 1;
            }
        }
    }
    cout << "diameter regressions passed\n";
    return 0;
}
