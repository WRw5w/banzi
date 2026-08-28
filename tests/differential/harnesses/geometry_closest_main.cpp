#include <bits/stdc++.h>
using namespace std;

using Real = long double;
struct Point {
    Real x, y;
    Point operator-(Point other) const { return {x - other.x, y - other.y}; }
};
Real dist2(Point a, Point b) {
    Point d = a - b;
    return d.x * d.x + d.y * d.y;
}

// @@@TEMPLATE@@@

int main(int argc, char** argv) {
    cout << setprecision(20);
    for (int file_index = 1; file_index < argc; ++file_index) {
        ifstream input(argv[file_index]);
        int n;
        while (input >> n) {
            vector<Point> points(n);
            for (auto& point : points) input >> point.x >> point.y;
            Real expected;
            input >> expected;
            sort(points.begin(), points.end(), [](Point a, Point b) {
                return a.x < b.x || (a.x == b.x && a.y < b.y);
            });
            Real actual = closest(points, 0, n);
            if (fabsl(actual - expected) > 1e-12L) {
                cerr << setprecision(20) << "expected=" << expected
                     << " actual=" << actual << '\n';
                return 1;
            }
        }
    }
    cout << "main closest-pair regressions passed\n";
    return 0;
}
