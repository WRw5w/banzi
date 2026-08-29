#include <bits/stdc++.h>
using namespace std;

namespace linear_dp_case {
pair<int,__int128> run(const vector<int>& input){const auto&a=input;int n=a.size();
// @@@LIS_MAX_SUBARRAY@@@
    return {lis,maxSubarray};
}
}
namespace lcs_case {
int run(const vector<int>&x,const vector<int>&y){const auto&a=x;const auto&b=y;int n=a.size(),m=b.size();
// @@@LCS@@@
    return lcs[n][m];
}
}
namespace knapsack_case {
// @@@KNAPSACK@@@
}
namespace tsp_case {
long long run(const vector<vector<long long>>&costs){int n=costs.size();auto w=costs;const long long INF=1LL<<60;
// @@@TSP_DP@@@
    return *min_element(dp.back().begin(),dp.back().end());
}
}
namespace rolling_case {
long long transition(long long up,long long left,int x,int y){return min(up,left)+abs(x-y);}
long long run(const vector<int>&x,const vector<int>&y){int n=x.size(),m=y.size();vector<int>a(n+1),b(m+1);copy(x.begin(),x.end(),a.begin()+1);copy(y.begin(),y.end(),b.begin()+1);
// @@@ROLLING_ARRAY@@@
    return prev[m];
}
}
namespace window_dp_case {
// @@@WINDOW_DP@@@
}
namespace cht_case {
// @@@CHT@@@
}
namespace sos_detail_case {
vector<long long> run(vector<long long> values,int bits){auto f=values;int K=bits;
// @@@SOS_DETAIL@@@
    return f;
}
}
namespace cht_detail_case {
// @@@CHT_DETAIL@@@
}

int main(){mt19937 rng(20260829);
    for(int round=0;round<2000;++round){int n=1+rng()%40;vector<int>a(n);for(int&x:a)x=(int)(rng()%51)-25;auto got=linear_dp_case::run(a);int lis=0;vector<int>d(n,1);__int128 sub=-((__int128)1<<126);for(int i=0;i<n;++i){for(int j=0;j<i;++j)if(a[j]<a[i])d[i]=max(d[i],d[j]+1);lis=max(lis,d[i]);__int128 s=0;for(int j=i;j<n;++j)s+=a[j],sub=max(sub,s);}if(got!=pair<int,__int128>{lis,sub})return 1;}
    for(int round=0;round<1000;++round){vector<int>a(rng()%20),b(rng()%20);for(int&x:a)x=rng()%6;for(int&x:b)x=rng()%6;vector<vector<int>>d(a.size()+1,vector<int>(b.size()+1));for(int i=1;i<=(int)a.size();++i)for(int j=1;j<=(int)b.size();++j)d[i][j]=a[i-1]==b[j-1]?d[i-1][j-1]+1:max(d[i-1][j],d[i][j-1]);if(lcs_case::run(a,b)!=d.back().back())return 2;}
    for(int round=0;round<1000;++round){int n=rng()%10,W=rng()%40;vector<pair<int,int>>items(n);for(auto&[w,v]:items)w=1+rng()%10,v=rng()%30;auto z=knapsack_case::zero_one_knapsack(items,W),c=knapsack_case::complete_knapsack(items,W);vector<long long>zw(W+1),cw(W+1);for(int mask=0;mask<(1<<n);++mask){int sw=0,sv=0;for(int i=0;i<n;++i)if(mask>>i&1)sw+=items[i].first,sv+=items[i].second;if(sw<=W)for(int j=sw;j<=W;++j)zw[j]=max<long long>(zw[j],sv);}for(int j=1;j<=W;++j)for(auto[w,v]:items)if(w<=j)cw[j]=max(cw[j],cw[j-w]+v);if(z!=zw||c!=cw)return 3;}
    for(int round=0;round<300;++round){int n=1+rng()%8;vector<vector<long long>>w(n,vector<long long>(n));for(auto&r:w)for(auto&x:r)x=rng()%40;long long want=1LL<<60;vector<int>p;for(int i=1;i<n;++i)p.push_back(i);do{long long s=0;int u=0;for(int v:p)s+=w[u][v],u=v;want=min(want,s);}while(next_permutation(p.begin(),p.end()));if(n==1)want=0;if(tsp_case::run(w)!=want)return 4;}
    for(int round=0;round<1000;++round){vector<int>a(1+rng()%20),b(1+rng()%20);for(int&x:a)x=rng()%20;for(int&x:b)x=rng()%20;vector<vector<long long>>d(a.size()+1,vector<long long>(b.size()+1));for(int i=1;i<=(int)a.size();++i)for(int j=1;j<=(int)b.size();++j)d[i][j]=rolling_case::transition(d[i-1][j],d[i][j-1],a[i-1],b[j-1]);if(rolling_case::run(a,b)!=d.back().back())return 5;}
    for(int round=0;round<1000;++round){int n=1+rng()%100,k=1+rng()%20;vector<long long>base(n);for(auto&x:base)x=(int)(rng()%31)-15;auto got=window_dp_case::window_min_dp(base,k);vector<__int128>want(base.begin(),base.end());for(int i=1;i<n;++i){__int128 best=(__int128)1<<126;for(int j=max(0,i-k);j<i;++j)best=min(best,want[j]);want[i]+=best;}if(got!=want)return 6;}
    {auto got=window_dp_case::window_min_dp({LLONG_MAX,LLONG_MAX,LLONG_MAX},1);if(got[2]!=(__int128)LLONG_MAX*3)return 9;}
    for(int bits=0;bits<=10;++bits){vector<long long>f(1<<bits);for(auto&x:f)x=rng()%100;auto got=sos_detail_case::run(f,bits),want=f;for(int m=0;m<(1<<bits);++m){long long s=0;for(int sub=m;;sub=(sub-1)&m){s+=f[sub];if(!sub)break;}want[m]=s;}if(got!=want)return 7;}
    for(int round=0;round<1000;++round){cht_case::hull.clear();cht_detail_case::hull.clear();vector<cht_case::Line>lines;long long slope=50;for(int i=0;i<20;++i){slope-=1+rng()%3;long long b=(int)(rng()%201)-100;lines.push_back({slope,b});cht_case::add_line(lines.back());cht_detail_case::add_line({slope,b});}for(long long x=-50;x<=50;++x){__int128 want=(__int128)1<<126,got=want,got2=want;for(auto l:lines)want=min(want,l.get(x));for(auto l:cht_case::hull)got=min(got,l.get(x));for(auto l:cht_detail_case::hull)got2=min(got2,l.value(x));if(got!=want||got2!=want)return 8;}}
    {cht_case::Line a{1,LLONG_MIN},b{0,LLONG_MAX},c{-1,LLONG_MIN};bool want=((__int128)b.b-a.b)*((__int128)b.k-c.k)>=((__int128)c.b-b.b)*((__int128)a.k-b.k);if(cht_case::bad(a,b,c)!=want)return 10;cht_detail_case::Line x{a.k,a.b},y{b.k,b.b},z{c.k,c.b};if(cht_detail_case::useless(x,y,z)!=want)return 11;cht_case::Line extreme{LLONG_MAX,LLONG_MIN};if(extreme.get(LLONG_MAX)!=(__int128)LLONG_MAX*LLONG_MAX+LLONG_MIN)return 12;}
    cout<<"dp foundation contracts: PASS\n";
}
