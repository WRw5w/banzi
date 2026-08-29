#include <bits/stdc++.h>
using namespace std;

namespace sieve_case {
tuple<vector<int>, vector<int>, vector<int>> run(int limit) {
    constexpr int N = 512;
    if (limit >= N) abort();
// @@@LINEAR_SIEVE@@@
    primes.erase(lower_bound(primes.begin(), primes.end(), limit), primes.end());
    lp.resize(limit); phi.resize(limit);
    return {primes, lp, phi};
}
}

namespace divisor_blocks_case {
long long run(long long value) {
    long long n = value, answer = 0;
// @@@DIVISOR_BLOCKS@@@
    return answer;
}
}

namespace phi_mu_case {
pair<vector<int>, vector<int>> run(int limit) {
    constexpr int N = 512;
    if (limit >= N) abort();
// @@@PHI_MU@@@
    phi.resize(limit); mu.resize(limit);
    return {phi, mu};
}
}

namespace combinations_case {
long long qpow(long long a, long long e, long long mod) { long long r=1; for(;e;e>>=1,a=a*a%mod)if(e&1)r=r*a%mod;return r; }
vector<vector<long long>> run(int limit) {
    constexpr int N = 256;
// @@@COMBINATIONS@@@
    vector<vector<long long>> result(limit + 1);
    for (int n = 0; n <= limit; ++n) for (int k = 0; k <= n; ++k) result[n].push_back(C(n, k));
    return result;
}
}

namespace generic_inclusion_case {
int m; vector<int> divisors; int upper;
long long count_satisfying(int mask) {
    long long l = 1;
    for (int i = 0; i < m; ++i) if (mask >> i & 1) l = lcm(l, (long long)divisors[i]);
    return upper / l;
}
long long run(int n, vector<int> d) {
    upper = n; divisors = move(d); m = (int)divisors.size();
// @@@GENERIC_INCLUSION@@@
    return ans;
}
}

namespace expected_dag_case {
vector<char> vis; vector<double> E; vector<vector<pair<int,double>>> transitions;
// @@@EXPECTED_DAG@@@
double run(const vector<vector<pair<int,double>>>& graph, int source) {
    transitions = graph; vis.assign(graph.size(), 0); E.assign(graph.size(), 0);
    return expected_dag(source);
}
}

namespace permutation_case {
vector<int> run(vector<int> permutation, long long shift) {
    auto p = move(permutation); int n = (int)p.size(); long long k = shift;
// @@@PERMUTATION_CYCLES@@@
    return result;
}
}

namespace multiples_inclusion_case {
long long lcm_limit(long long a, long long b, long long limit, bool& overflow) {
    long long g = gcd(a, b);
    if ((__int128)(a / g) * b > limit) { overflow = true; return limit + 1; }
    return a / g * b;
}
long long run(long long limit, vector<long long> divisors) {
    long long n = limit; auto a = move(divisors); int m = (int)a.size();
// @@@MULTIPLES_INCLUSION@@@
    return bad;
}
}

int euler_phi(int n) { int r=n; for(int p=2;p*p<=n;++p)if(n%p==0){while(n%p==0)n/=p;r-=r/p;}if(n>1)r-=r/n;return r; }
int mobius(int n) { int r=1; for(int p=2;p*p<=n;++p)if(n%p==0){n/=p;r=-r;if(n%p==0)return 0;while(n%p==0)n/=p;}if(n>1)r=-r;return r; }

int main() {
    mt19937 rng(20260829);
    auto [primes, lp, phi] = sieve_case::run(500);
    vector<int> want_primes;
    for(int x=2;x<500;++x){bool prime=1;for(int d=2;d*d<=x;++d)if(x%d==0)prime=0;if(prime)want_primes.push_back(x);int least=0;for(int d=2;d<=x;++d)if(x%d==0){least=d;break;}if(lp[x]!=least||phi[x]!=euler_phi(x))return 1;}
    if(primes!=want_primes)return 2;
    auto [phis,mus]=phi_mu_case::run(500);for(int x=1;x<500;++x)if(phis[x]!=euler_phi(x)||mus[x]!=mobius(x))return 3;
    for(long long n=1;n<=100000;n+=137){long long want=0;for(long long i=1;i<=n;++i)want+=n/i;if(divisor_blocks_case::run(n)!=want)return 4;}
    auto comb=combinations_case::run(200);for(int n=0;n<=200;++n){long long cur=1;for(int k=0;k<=n;++k){if(comb[n][k]!=cur)return 5;cur=cur*(n-k)%998244353*combinations_case::qpow(k+1,998244351,998244353)%998244353;}}
    for(int round=0;round<1000;++round){int n=1+rng()%500;vector<int>d;for(int p:{2,3,5,7,11})if(rng()%2)d.push_back(p);long long want=0;for(int x=1;x<=n;++x){bool none=1;for(int p:d)none&=x%p!=0;want+=none;}if(generic_inclusion_case::run(n,d)!=want)return 6;long long bad=n-want;vector<long long>dl(d.begin(),d.end());if(multiples_inclusion_case::run(n,dl)!=bad)return 7;}
    for(int round=0;round<500;++round){int n=1+rng()%30;vector<vector<pair<int,double>>>g(n);vector<double>w(n,1.0);for(int u=n-2;u>=0;--u){vector<int>to;for(int v=u+1;v<n;++v)if(rng()%4==0)to.push_back(v);if(to.empty())to.push_back(u+1);double p=1.0/to.size();for(int v:to)g[u].push_back({v,p}),w[u]+=p*w[v];}if(abs(expected_dag_case::run(g,0)-w[0])>1e-9)return 8;}
    for(int round=0;round<1000;++round){int n=1+rng()%50;vector<int>p(n);iota(p.begin(),p.end(),0);shuffle(p.begin(),p.end(),rng);long long k=rng()%1000;auto got=permutation_case::run(p,k);vector<int>want(n);for(int i=0;i<n;++i){int u=i;for(int j=0;j<k;++j)u=p[u];want[i]=u;}if(got!=want)return 9;}
    cout<<"math foundation contracts: PASS\n";
}
