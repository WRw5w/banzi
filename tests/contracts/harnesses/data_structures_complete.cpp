#include <bits/stdc++.h>
using namespace std;

namespace treap_case {
constexpr int MAXN = 10000;
// @@@TREAP@@@
}

namespace cdq_case {
constexpr int MAX_Z = 128;
// @@@CDQ@@@
}

namespace lichao_case {
constexpr int MAXX = 101;
// @@@LICHAO@@@
}

namespace persistent_dsu_case {
constexpr int MAXNODE = 2000000;
int n;
// @@@PERSISTENT_DSU@@@
}
namespace block_add_case {
constexpr int n=257;
// @@@BLOCK_ADD@@@
}

int main() {
    mt19937 rng(20260829);
    {
        using namespace treap_case;
        vector<int> values;
        for (int i=0;i<300;++i) {
            int key=(int)(rng()%1000); int node=++tot;
            tr[node]={0,0,key,(int)rng(),1};
            int x,y; split(root,key,x,y); root=merge(merge(x,node),y); values.push_back(key);
        }
        vector<int> got; function<void(int)> dfs=[&](int u){if(!u)return;dfs(tr[u].l);got.push_back(tr[u].key);dfs(tr[u].r);}; dfs(root);
        sort(values.begin(),values.end()); if(got!=values || size(root)!=(int)values.size()) return 1;
        for(int key=0;key<=1000;key+=17){int x,y;split(root,key,x,y);if(size(x)!=(int)(upper_bound(values.begin(),values.end(),key)-values.begin()))return 2;root=merge(x,y);}
    }
    for(int round=0;round<300;++round){
        using namespace cdq_case;
        int n=1+rng()%50; vector<Point>a; set<tuple<int,int,int>> used;
        while((int)a.size()<n){int x=rng()%30,y=rng()%30,z=1+rng()%60;if(used.emplace(x,y,z).second)a.push_back({x,y,z,1,0});}
        sort(a.begin(),a.end(),[](auto&A,auto&B){return tie(A.x,A.y,A.z)<tie(B.x,B.y,B.z);});
        map<tuple<int,int,int>,long long>want;
        for(auto&p:a){long long c=0;for(auto&q:a)c+=q.x<=p.x&&q.y<=p.y&&q.z<=p.z;want[{p.x,p.y,p.z}]=c-1;}
        bit=Fenwick(MAX_Z); cdq(a,0,n-1);
        for(auto&p:a)if(p.ans!=want[{p.x,p.y,p.z}])return 3;
    }
    for(int round=0;round<300;++round){
        using namespace lichao_case;
        fill(begin(tree),end(tree),Line{}); vector<Line> lines;
        for(int i=0;i<100;++i){Line z{(int)(rng()%101)-50,(int)(rng()%1001)-500};lines.push_back(z);add_line(z,1,0,MAXX-1);}
        for(int x=0;x<MAXX;++x){__int128 want=-((__int128)1<<126);for(auto z:lines)want=max(want,z.get(x));if(query(x,1,0,MAXX-1)!=want)return 4;}
    }
    {using namespace lichao_case;fill(begin(tree),end(tree),Line{});if(query(2,1,0,MAXX-1)!=-((__int128)1<<126))return 7;Line z{LLONG_MAX,LLONG_MAX};add_line(z,1,0,MAXX-1);if(query(2,1,0,MAXX-1)!=(__int128)LLONG_MAX*3)return 8;}
    for(int round=0;round<100;++round){
        using namespace persistent_dsu_case;
        n=30;tot=0;vector<int> roots{build(1,n)};vector<vector<int>> parent(1,vector<int>(n+1));iota(parent[0].begin(),parent[0].end(),0);
        auto nf=[&](const vector<int>&p,int x){while(p[x]!=x)x=p[x];return x;};
        for(int op=0;op<100;++op){int base=rng()%roots.size(),x=1+rng()%n,y=1+rng()%n;int nr=merge_version(roots[base],x,y);auto np=parent[base];int fx=nf(np,x),fy=nf(np,y);if(fx!=fy)np[fx]=fy;roots.push_back(nr);parent.push_back(np);for(int q=0;q<20;++q){int u=1+rng()%n,v=1+rng()%n;if((find_root(nr,u)==find_root(nr,v))!=(nf(np,u)==nf(np,v)))return 5;}}
    }
    {
        using namespace block_add_case;vector<long long>want(n);
        for(int op=0;op<10000;++op){int l=rng()%n,r=rng()%n;if(l>r)swap(l,r);long long v=(int)(rng()%201)-100;add(l,r,v);for(int i=l;i<=r;++i)want[i]+=v;for(int q=0;q<20;++q){int i=rng()%n;if(a[i]+tag[i/B]!=want[i])return 6;}}
    }
    cout << "data-structure complete contracts: PASS\n";
}
