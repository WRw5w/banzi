#include <bits/stdc++.h>
using namespace std;

namespace stl_case {
vector<int> run(vector<int> input_values){vector<int>input=input_values;int n=input.size();vector<int>value(n),version(n);iota(value.begin(),value.end(),0);
// @@@STL_COMPONENTS@@@
    return a;
}
}
namespace affine_case {
constexpr long long MOD=1000000007;
// @@@AFFINE_TAGS@@@
}
namespace beats_case {
// @@@SEGMENT_BEATS@@@
void build(int p,int l,int r,const vector<long long>&a){if((int)tr.size()<=p)tr.resize(p+1);if(l==r){tr[p]={a[l],a[l],NEG,1};return;}int m=(l+r)/2;build(p*2,l,m,a);build(p*2+1,m+1,r,a);push_up(p);}
void collect(int p,int l,int r,vector<long long>&a){if(l==r){a[l]=tr[p].mx1;return;}push_down(p);int m=(l+r)/2;collect(p*2,l,m,a);collect(p*2+1,m+1,r,a);}
}
namespace hash_case {
vector<unsigned long long> run(const string&input,const vector<pair<int,int>>&queries){string s=input;int n=s.size();
// @@@STRING_HASH@@@
    vector<unsigned long long>result;for(auto[l,r]:queries)result.push_back(get_hash(l,r));return result;
}
}
namespace random_geometry_case {
pair<int,vector<int>> run(vector<int>input,int order){auto a=input;int k=order;
// @@@GEOMETRY_RANDOM@@@
    return {answer,a};
}
}
namespace geometry_closure_case {
// @@@GEOMETRY_CLOSURE@@@
vector<vector<int>>run(int n,const vector<pair<int,int>>&edges){array<bitset<N>,N>r{};for(int i=0;i<n;++i)r[i][i]=1;for(auto[u,v]:edges)r[u][v]=1;geometry_bitset_closure(r,n);vector<vector<int>>out(n,vector<int>(n));for(int i=0;i<n;++i)for(int j=0;j<n;++j)out[i][j]=r[i][j];return out;}
}
namespace direction_case {
// @@@DIRECTION_NORMALIZATION@@@
}
namespace scanline_geometry_case {
// @@@GEOMETRY_SCANLINE@@@
long long run(const vector<array<int,4>>&rects){vector<Event>events;for(auto r:rects){events.push_back({r[0],r[1],r[3],1});events.push_back({r[2],r[1],r[3],-1});}array<int,32>cover{};auto length=[&](){long long s=0;for(int i=0;i<31;++i)s+=cover[i]>0;return s;};auto update=[&](int l,int r,int d){for(int i=l;i<=r;++i)cover[i]+=d;};auto id=[](long long y){return(int)y;};return sweep_area(events,length,update,id);}
}

int main(){mt19937 rng(20260829);
    for(int round=0;round<1000;++round){vector<int>a(rng()%100);for(int&x:a)x=(int)(rng()%31)-15;auto got=stl_case::run(a);sort(a.begin(),a.end());a.erase(unique(a.begin(),a.end()),a.end());if(got!=a)return 1;}
    for(int round=0;round<10000;++round){using namespace affine_case;tr.assign(4,{});long long x=rng()%MOD;tr[1].sum=x;long long m1=rng()%MOD,a1=rng()%MOD,m2=rng()%MOD,a2=rng()%MOD;apply(1,0,0,m1,a1);apply(1,0,0,m2,a2);long long want=((__int128)x*m1+a1)%MOD;want=((__int128)want*m2+a2)%MOD;if(tr[1].sum!=want||tr[1].tag.mul!=(__int128)m1*m2%MOD||tr[1].tag.add!=((__int128)a1*m2+a2)%MOD)return 2;tr.assign(8,{});tr[1].sum=3;tr[2].sum=1;tr[3].sum=2;apply(1,0,1,m1,a1);push(1,0,1);if(tr[2].sum!=((__int128)m1+a1)%MOD||tr[3].sum!=((__int128)2*m1+a1)%MOD)return 3;}
    for(int round=0;round<1000;++round){using namespace beats_case;int n=1+rng()%80;vector<long long>a(n+1);for(int i=1;i<=n;++i)a[i]=(int)(rng()%101)-50;tr.clear();tr.resize(4*n+8);build(1,1,n,a);for(int q=0;q<100;++q){int l=1+rng()%n,r=l+rng()%(n-l+1);long long x=(int)(rng()%121)-60;range_chmin(1,1,n,l,r,x);for(int i=l;i<=r;++i)a[i]=min(a[i],x);if(tr[1].sum!=accumulate(a.begin()+1,a.end(),0LL))return 4;}vector<long long>got(n+1);collect(1,1,n,got);if(got!=a)return 5;}
    for(int round=0;round<1000;++round){string s;int n=rng()%100;for(int i=0;i<n;++i)s+=char('a'+rng()%5);vector<pair<int,int>>q;for(int i=0;i<100;++i){int l=rng()%(n+1),r=l+rng()%(n-l+1);q.push_back({l,r});}auto h=hash_case::run(s,q);for(int i=0;i<100;++i)for(int j=0;j<100;++j)if(q[i].second-q[i].first==q[j].second-q[j].first&&(h[i]==h[j])!=(s.substr(q[i].first,q[i].second-q[i].first)==s.substr(q[j].first,q[j].second-q[j].first)))return 6;}
    for(int round=0;round<1000;++round){vector<int>a(1+rng()%100);for(int&x:a)x=(int)rng();int k=rng()%a.size();auto sorted=a;sort(sorted.begin(),sorted.end());if(random_geometry_case::run(a,k).first!=sorted[k])return 7;}
    for(int round=0;round<300;++round){int n=1+rng()%30;vector<pair<int,int>>e;vector<vector<int>>want(n,vector<int>(n));for(int i=0;i<n;++i)want[i][i]=1;for(int u=0;u<n;++u)for(int v=0;v<n;++v)if(rng()%8==0)e.push_back({u,v}),want[u][v]=1;for(int k=0;k<n;++k)for(int i=0;i<n;++i)for(int j=0;j<n;++j)want[i][j]|=want[i][k]&&want[k][j];if(geometry_closure_case::run(n,e)!=want)return 8;}
    for(int round=0;round<10000;++round){long long dx=(int)(rng()%2001)-1000,dy=(int)(rng()%2001)-1000;if(!dx&&!dy)dx=1;auto [x,y]=direction_case::normalize_direction(dx,dy);if(gcd(llabs(x),llabs(y))!=1||x<0||(x==0&&y<0)||(__int128)x*dy!=(__int128)y*dx)return 9;long long a=(int)(rng()%2001)-1000,b=(int)(rng()%2001)-1000;long long want=a==0||b==0?0:llabs(a/gcd(a,b)*b);if(direction_case::safe_lcm(a,b)!=want)return 10;}
    bool threw=0;try{direction_case::normalize_direction(0,0);}catch(const invalid_argument&){threw=1;}if(!threw)return 11;
    for(int round=0;round<1000;++round){vector<array<int,4>>rects;bool grid[30][30]{};int n=rng()%30;for(int i=0;i<n;++i){int x1=rng()%29,x2=x1+1+rng()%(30-x1-1),y1=rng()%29,y2=y1+1+rng()%(30-y1-1);rects.push_back({x1,y1,x2,y2});for(int x=x1;x<x2;++x)for(int y=y1;y<y2;++y)grid[x][y]=1;}long long want=0;for(auto&r:grid)for(bool v:r)want+=v;if(scanline_geometry_case::run(rects)!=want)return 12;}
    cout<<"structure/string/geometry contracts: PASS\n";
}
