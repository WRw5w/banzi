#include <bits/stdc++.h>
using namespace std;

struct SeedArc {
    int from;
    int to;
    long long weight;
};

vector<SeedArc> seeded_arcs;

template<class T, class = void>
struct has_value_type : false_type {};

template<class T>
struct has_value_type<T, void_t<typename T::value_type>> : true_type {};

template<class T>
class SeedVector : public vector<T> {
    using Base = vector<T>;
public:
    using Base::Base;
    using value_type = T;

    explicit SeedVector(size_t count) : Base(count) {
        if constexpr (has_value_type<T>::value) {
            using Edge = typename T::value_type;
            for (const auto& arc : seeded_arcs)
                (*this)[arc.from].push_back(Edge{arc.to, arc.weight});
        }
    }
};

bool template_reports_feasible(int n) {
#define vector SeedVector
// @@@TEMPLATE@@@
#undef vector
    return ok;
}

bool brute_has_no_negative_cycle(int n, const vector<SeedArc>& arcs) {
    vector<__int128> distance(n, 0);
    for (int iteration = 0; iteration < n; ++iteration) {
        bool changed = false;
        for (const auto& arc : arcs) {
            if (distance[arc.to] > distance[arc.from] + (__int128)arc.weight) {
                distance[arc.to] = distance[arc.from] + (__int128)arc.weight;
                changed = true;
            }
        }
        if (!changed) return true;
        if (iteration == n - 1) return false;
    }
    return true;
}

int main(int argc, char** argv) {
    for (int file_index = 1; file_index < argc; ++file_index) {
        ifstream input(argv[file_index]);
        if (!input) {
            cerr << "cannot open regression file: " << argv[file_index] << '\n';
            return 2;
        }
        int n, edge_count, expected;
        while (input >> n >> edge_count >> expected) {
            seeded_arcs.resize(edge_count);
            for (auto& arc : seeded_arcs)
                input >> arc.from >> arc.to >> arc.weight;
            bool oracle = brute_has_no_negative_cycle(n, seeded_arcs);
            if (oracle != bool(expected)) {
                cerr << "invalid regression oracle expected=" << expected
                     << " brute=" << oracle << '\n';
                return 2;
            }
            bool actual = template_reports_feasible(n);
            if (actual != oracle) {
                cerr << "n=" << n << " edges=" << edge_count
                     << " expected=" << oracle << " actual=" << actual << '\n';
                return 1;
            }
        }
    }
    cout << "difference-constraints regressions: PASS\n";
    return 0;
}
