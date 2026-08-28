#include <bits/stdc++.h>
using namespace std;

struct Point { long double x, y; };
const long double INF = 1e100L;
vector<Point> p;
long double dist2(Point a, Point b) {
    long double dx = a.x - b.x, dy = a.y - b.y;
    return dx * dx + dy * dy;
}
bool by_y(Point a, Point b) { return a.y < b.y; }

// @@@TEMPLATE@@@

long double brute_closest(const vector<Point>& points) {
    long double answer = INF;
    for (int i = 0; i < (int)points.size(); ++i)
        for (int j = 0; j < i; ++j)
            answer = min(answer, dist2(points[i], points[j]));
    return answer;
}

int main() {
    const uint64_t seed = 0xC105E572028ULL;
    mt19937_64 rng(seed);
    for (int round = 0; round < 20000; ++round) {
        int n = 2 + (int)(rng() % 18);
        p.resize(n);
        for (Point& point : p) {
            point.x = (long long)(rng() % 201) - 100;
            point.y = (long long)(rng() % 201) - 100;
        }
        vector<Point> original = p;
        sort(p.begin(), p.end(), [](Point a, Point b) {
            return a.x < b.x || (a.x == b.x && a.y < b.y);
        });
        long double actual = closest(0, n);
        long double expected = brute_closest(original);
        if (actual != expected) {
            cerr << "seed=" << seed << " round=" << round
                 << " expected=" << expected << " actual=" << actual << '\n';
            return 1;
        }
    }
    cout << "rounds=20000 seed=" << seed << '\n';
    return 0;
}
