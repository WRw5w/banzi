#include <bits/stdc++.h>
using namespace std;

namespace bitset_knapsack_case {
vector<int> run(const vector<int>& weights) {
    constexpr int MAXV = 256;
    int n = (int)weights.size();
    const vector<int>& w = weights;
// @@@BITSET_KNAPSACK@@@
    vector<int> result;
    for (int sum = 0; sum < MAXV; ++sum) if (bs[sum]) result.push_back(sum);
    return result;
}
}

namespace bitset_closure_case {
// @@@BITSET_CLOSURE@@@
vector<vector<int>> run(int n, const vector<pair<int, int>>& edges) {
    constexpr int MAXN = 64;
    array<bitset<MAXN>, MAXN> reach{};
    for (int i = 0; i < n; ++i) reach[i][i] = 1;
    for (auto [u, v] : edges) reach[u][v] = 1;
    transitive_closure(reach, n);
    vector<vector<int>> result(n, vector<int>(n));
    for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) result[i][j] = reach[i][j];
    return result;
}
}

namespace shift_and_case {
vector<int> run(const string& text, const string& pattern) {
    constexpr int MAXM = 64;
    string t = text, p = pattern;
    int m = (int)p.size();
    if (m == 0 || m >= MAXM) return {};
// @@@SHIFT_AND@@@
    return matches;
}
}

namespace sos_case {
vector<long long> run(vector<long long> values, int n) {
    vector<long long> f = values;
// @@@SOS@@@
    return f;
}
}

namespace subset_case {
// @@@SUBSET_ENUMERATION@@@
}

namespace backtracking_case {
long long target, answer; int n; vector<long long> a;
// @@@BACKTRACKING@@@
long long run(vector<long long> values,long long wanted){a=move(values);sort(a.begin(),a.end());n=a.size();target=wanted;answer=0;dfs(0,0);return answer;}
}

namespace mitm_case {
// @@@MITM@@@
}

namespace difference_case {
pair<vector<long long>, long long> run(vector<long long> input,
                                       const vector<tuple<int, int, long long>>& ops,
                                       int ql, int qr) {
    int n = (int)input.size() - 1;
    vector<long long> a = input;
    const auto& updates = ops;
// @@@DIFFERENCE_ARRAY@@@
    return {a, range_sum(ql, qr)};
}
}

namespace scanline_case {
int run(vector<pair<int, int>> input) {
    auto intervals = input;
// @@@SCANLINE_PEAK@@@
    return peak;
}
}

namespace binary_search_case {
int run(const vector<int>& input, int target) {
    const auto& a = input;
    int n = (int)a.size(), x = target;
// @@@BINARY_SEARCH@@@
    return l;
}
}

namespace binary_answer_case {
// @@@BINARY_ANSWER@@@
}

namespace sliding_window_case {
int run(const vector<int>& input, int kinds, int alphabet_size) {
    const auto& s = input;
    int n = (int)s.size(), k = kinds, alphabet = alphabet_size;
// @@@SLIDING_WINDOW@@@
    return answer;
}
}

namespace ternary_case {
long long run(long long left, long long right, long long peak, long long offset) {
    long long l = left, r = right;
    auto f = [=](long long x) { return offset - (x - peak) * (x - peak); };
// @@@TERNARY_SEARCH@@@
    return ans;
}
}

namespace interval_case {
int run(vector<pair<int, int>> input) {
    auto intervals = input;
// @@@INTERVAL_GREEDY@@@
    return chosen;
}
}

namespace regret_case {
struct Job { int deadline, cost; };
pair<int, long long> run(vector<Job> input) {
    auto jobs = input;
// @@@REGRET_GREEDY@@@
    long long total = 0;
    int count = (int)chosen.size();
    while (!chosen.empty()) total += chosen.top(), chosen.pop();
    return {count, total};
}
}

namespace monotonic_stack_case {
vector<int> run(const vector<int>& input) {
    const auto& a = input;
    int n = (int)a.size();
// @@@MONOTONIC_STACK@@@
    return nextGreater;
}
}

namespace monotonic_queue_case {
vector<int> run(const vector<int>& input, int width) {
    const auto& a = input;
    int n = (int)a.size(), k = width;
    vector<int> answer;
// @@@MONOTONIC_QUEUE@@@
    return answer;
}
}

namespace discretization_case {
pair<vector<long long>, vector<int>> run(const vector<long long>& input) {
    auto coordinates = input;
// @@@DISCRETIZATION@@@
    vector<int> ids;
    for (long long x : input) ids.push_back(id(x));
    return {xs, ids};
}
}

namespace construction_case {
vector<int> run(int n) {
// @@@ODD_EVEN_CONSTRUCTION@@@
    return ans;
}
}

namespace randomized_case {
pair<int, vector<int>> run(vector<int> input, int order) {
    auto a = input;
    int k = order;
// @@@RANDOMIZED_SELECTION@@@
    return {answer, a};
}
}

namespace reachability_case {
// @@@REACHABILITY@@@
vector<vector<int>> run(int n, const vector<pair<int, int>>& edges) {
    array<bitset<N>, N> reach{};
    for (int i = 0; i < n; ++i) reach[i].reset();
    for (int i = 0; i < n; ++i) reach[i][i] = 1;
    for (auto [u, v] : edges) reach[u][v] = 1;
    bitset_closure(reach, n);
    vector<vector<int>> result(n, vector<int>(n));
    for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) result[i][j] = reach[i][j];
    return result;
}
}

int main() {
    mt19937 rng(20260829);
    for (int round = 0; round < 400; ++round) {
        int n = rng() % 14;
        vector<int> w(n);
        for (int& x : w) x = 1 + rng() % 30;
        auto got = bitset_knapsack_case::run(w);
        vector<char> possible(256); possible[0] = 1;
        for (int x : w) for (int s = 255; s >= x; --s) possible[s] |= possible[s - x];
        vector<int> want;
        for (int s = 0; s < 256; ++s) if (possible[s]) want.push_back(s);
        if (got != want) return 1;
    }
    for (int round = 0; round < 500; ++round) {
        int n = 1 + rng() % 30;
        vector<pair<int, int>> edges;
        vector<vector<int>> want(n, vector<int>(n));
        for (int i = 0; i < n; ++i) want[i][i] = 1;
        for (int u = 0; u < n; ++u) for (int v = 0; v < n; ++v) if (rng() % 7 == 0)
            edges.push_back({u, v}), want[u][v] = 1;
        for (int k = 0; k < n; ++k) for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j)
            want[i][j] |= want[i][k] && want[k][j];
        if (bitset_closure_case::run(n, edges) != want) return 2;
        if (reachability_case::run(n, edges) != want) return 3;
    }
    for (int round = 0; round < 1000; ++round) {
        string text, pattern;
        int n = rng() % 80, m = 1 + rng() % 20;
        for (int i = 0; i < n; ++i) text += char('a' + rng() % 4);
        for (int i = 0; i < m; ++i) pattern += char('a' + rng() % 4);
        vector<int> want;
        for (int i = 0; i + m <= n; ++i) if (text.substr(i, m) == pattern) want.push_back(i);
        if (shift_and_case::run(text, pattern) != want) return 4;
    }
    for (int n = 0; n <= 8; ++n) {
        vector<long long> f(1 << n);
        for (auto& x : f) x = rng() % 100;
        auto got = sos_case::run(f, n), want = f;
        for (int mask = 0; mask < (1 << n); ++mask) {
            long long sum = 0;
            for (int sub = mask;; sub = (sub - 1) & mask) { sum += f[sub]; if (!sub) break; }
            want[mask] = sum;
        }
        if (got != want) return 5;
        auto pairs = subset_case::enumerate_submasks(n);
        if (pairs.size() != (size_t)pow(3, n)) return 6;
        set<pair<int, int>> unique_pairs(pairs.begin(), pairs.end());
        if (unique_pairs.size() != pairs.size()) return 7;
        for (auto [mask, sub] : pairs) if ((sub & ~mask) != 0) return 8;
    }
    for(int round=0;round<1000;++round){int n=rng()%16;vector<long long>a(n);for(auto&x:a)x=1+rng()%8;long long target=rng()%40;set<vector<long long>>solutions;for(int mask=0;mask<(1<<n);++mask){vector<long long>v;long long s=0;for(int i=0;i<n;++i)if(mask>>i&1)v.push_back(a[i]),s+=a[i];sort(v.begin(),v.end());if(s==target)solutions.insert(v);}if(backtracking_case::run(a,target)!=(long long)solutions.size())return 25;}
    for (int round = 0; round < 300; ++round) {
        int n = rng() % 17; vector<long long> a(n); for (auto& x : a) x = rng() % 40;
        long long limit = rng() % 250, want = 0;
        for (int mask = 0; mask < (1 << n); ++mask) { long long sum = 0; for (int i = 0; i < n; ++i) if (mask >> i & 1) sum += a[i]; if (sum <= limit) want = max(want, sum); }
        if (mitm_case::mitm_max_subset_sum(a, limit) != want) return 9;
    }
    for (int round = 0; round < 1000; ++round) {
        int n = 1 + rng() % 30; vector<long long> a(n + 1); for (int i = 1; i <= n; ++i) a[i] = (int)(rng() % 31) - 15;
        vector<tuple<int, int, long long>> ops; auto want = a;
        for (int q = 0; q < 20; ++q) { int l = 1 + rng() % n, r = l + rng() % (n - l + 1); long long v = (int)(rng() % 21) - 10; ops.push_back({l, r, v}); for (int i = l; i <= r; ++i) want[i] += v; }
        int l = 1 + rng() % n, r = l + rng() % (n - l + 1); auto got = difference_case::run(a, ops, l, r);
        long long original_sum = accumulate(a.begin() + l, a.begin() + r + 1, 0LL);
        if (got.first != want || got.second != original_sum) return 10;
    }
    for (int round = 0; round < 400; ++round) {
        int n = rng() % 15; vector<pair<int, int>> intervals; for (int i = 0; i < n; ++i) { int l = rng() % 30, r = l + 1 + rng() % 10; intervals.push_back({l, r}); }
        int peak = 0; for (int x = 0; x < 40; ++x) { int active = 0; for (auto [l, r] : intervals) active += l <= x && x < r; peak = max(peak, active); }
        if (scanline_case::run(intervals) != peak) return 11;
        vector<int> order(n); iota(order.begin(), order.end(), 0); int best = 0;
        for (int mask = 0; mask < (1 << min(n, 20)); ++mask) { vector<pair<int,int>> chosen; bool ok = true; for (int i = 0; i < n && i < 20; ++i) if (mask >> i & 1) chosen.push_back(intervals[i]); sort(chosen.begin(), chosen.end()); for (int i = 1; i < (int)chosen.size(); ++i) ok &= chosen[i-1].second <= chosen[i].first; if (ok) best = max(best, (int)chosen.size()); }
        if (n <= 20 && interval_case::run(intervals) != best) return 12;
    }
    for (int round = 0; round < 3000; ++round) {
        vector<int> a(rng() % 50); for (int& x : a) x = (int)(rng() % 50) - 25; int x = (int)(rng() % 60) - 30;
        sort(a.begin(), a.end()); if (binary_search_case::run(a, x) != (int)(lower_bound(a.begin(), a.end(), x) - a.begin())) return 13;
        int alphabet = 8, k = rng() % 9; vector<int> s(1 + rng() % 40); for (int& v : s) v = rng() % alphabet; int want = 0;
        for (int l = 0; l < (int)s.size(); ++l) { set<int> kinds; for (int r = l; r < (int)s.size(); ++r) { kinds.insert(s[r]); if ((int)kinds.size() <= k) want = max(want, r-l+1); } }
        if (sliding_window_case::run(s, k, alphabet) != want) return 14;
    }
    for (int round = 0; round < 3000; ++round) { long long l = (int)(rng()%100)-50, r=l+rng()%100, p=l+rng()%(r-l+1), off=(int)(rng()%1000)-500; if (ternary_case::run(l,r,p,off)!=off) return 15; }
    for(int round=0;round<1000;++round){int n=1+rng()%12,k=1+rng()%n;vector<long long>a(n);for(auto&x:a)x=rng()%30;vector<vector<long long>>dp(k+1,vector<long long>(n+1,1LL<<60));dp[0][0]=0;for(int g=1;g<=k;++g)for(int i=1;i<=n;++i){long long sum=0;for(int j=i-1;j>=0;--j){sum+=a[j];dp[g][i]=min(dp[g][i],max(dp[g-1][j],sum));}}long long want=1LL<<60;for(int g=1;g<=k;++g)want=min(want,dp[g][n]);if(binary_answer_case::minimize_max_segment_sum(a,k)!=want)return 24;}
    for (int round = 0; round < 500; ++round) {
        int n = rng() % 12; vector<regret_case::Job> jobs(n); for (auto& j : jobs) j={1+(int)(rng()%max(1,n)),1+(int)(rng()%50)};
        auto got=regret_case::run(jobs); pair<int,long long>want={-1,LLONG_MAX};
        for(int mask=0;mask<(1<<n);++mask){vector<regret_case::Job>s;long long cost=0;for(int i=0;i<n;++i)if(mask>>i&1)s.push_back(jobs[i]),cost+=jobs[i].cost;sort(s.begin(),s.end(),[](auto a,auto b){return a.deadline<b.deadline;});bool ok=1;for(int i=0;i<(int)s.size();++i)ok&=i+1<=s[i].deadline;if(ok&&((int)s.size()>want.first||((int)s.size()==want.first&&cost<want.second)))want={(int)s.size(),cost};}
        if(got!=want)return 16;
    }
    for(int round=0;round<1000;++round){vector<int>a(1+rng()%60);for(int&x:a)x=(int)(rng()%31)-15;vector<int>want(a.size(),-1);for(int i=0;i<(int)a.size();++i)for(int j=i+1;j<(int)a.size();++j)if(a[j]>a[i]){want[i]=j;break;}if(monotonic_stack_case::run(a)!=want)return 17;int k=1+rng()%a.size();vector<int>mx;for(int i=0;i+k<=(int)a.size();++i)mx.push_back(*max_element(a.begin()+i,a.begin()+i+k));if(monotonic_queue_case::run(a,k)!=mx)return 18;}
    for(int round=0;round<1000;++round){vector<long long>a(1+rng()%50);for(auto&x:a)x=(int)(rng()%101)-50;auto got=discretization_case::run(a);auto xs=a;sort(xs.begin(),xs.end());xs.erase(unique(xs.begin(),xs.end()),xs.end());if(got.first!=xs)return 19;for(int i=0;i<(int)a.size();++i)if(got.second[i]!=(int)(lower_bound(xs.begin(),xs.end(),a[i])-xs.begin())+1)return 20;}
    for(int n=0;n<=100;++n){auto a=construction_case::run(n),b=a;sort(b.begin(),b.end());vector<int>w(n);iota(w.begin(),w.end(),1);if(b!=w)return 21;for(int i=1;i<(int)a.size();++i)if((a[i-1]&1)==0&&(a[i]&1))return 22;}
    for(int round=0;round<1000;++round){vector<int>a(1+rng()%100);for(int&x:a)x=(int)rng();int k=rng()%a.size();auto sorted=a;sort(sorted.begin(),sorted.end());auto got=randomized_case::run(a,k);if(got.first!=sorted[k])return 23;}
    cout << "foundation contracts: PASS\n";
}
