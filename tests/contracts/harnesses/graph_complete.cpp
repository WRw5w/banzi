#include <bits/stdc++.h>
using namespace std;

namespace mst_case {
// @@@KRUSKAL@@@
}
namespace scc_case {
constexpr int n=64; vector<vector<int>> g(n);
// @@@SCC@@@
}
namespace bridge_case {
constexpr int n=64; vector<vector<pair<int,int>>> g(n);
// @@@BRIDGES@@@
}
namespace mcmf_case {
constexpr int n=20;
// @@@MCMF@@@
}
namespace lca_case {
constexpr int MAXN=256; vector<int> tree[MAXN];
// @@@LCA@@@
}
namespace farthest_case {
int n; vector<vector<pair<int,long long>>> weighted_tree;
// @@@FARTHEST@@@
}

pair<int,long long> reference_mcmf(int n, vector<tuple<int,int,int,int>> edges,int s,int t,int need){
    struct E{int v,rev,cap,cost;};vector<vector<E>>g(n);
    auto add=[&](int u,int v,int cap,int cost){E a{v,(int)g[v].size(),cap,cost},b{u,(int)g[u].size(),0,-cost};g[u].push_back(a);g[v].push_back(b);};
    for(auto [u,v,c,w]:edges)add(u,v,c,w);int flow=0;long long cost=0;
    while(flow<need){vector<long long>d(n,4e18);vector<int>pv(n),pe(n);vector<char>in(n);queue<int>q;d[s]=0;q.push(s);in[s]=1;
        while(!q.empty()){int u=q.front();q.pop();in[u]=0;for(int i=0;i<(int)g[u].size();++i){auto&e=g[u][i];if(e.cap&&d[e.v]>d[u]+e.cost){d[e.v]=d[u]+e.cost;pv[e.v]=u;pe[e.v]=i;if(!in[e.v])in[e.v]=1,q.push(e.v);}}}
        if(d[t]>3e18)break;int addf=need-flow;for(int v=t;v!=s;v=pv[v])addf=min(addf,g[pv[v]][pe[v]].cap);for(int v=t;v!=s;v=pv[v]){auto&e=g[pv[v]][pe[v]];e.cap-=addf;g[v][e.rev].cap+=addf;}flow+=addf;cost+=1LL*addf*d[t];}
    return {flow,cost};
}

int main(){mt19937 rng(20260829);
    for(int round=0;round<1000;++round){int n=1+rng()%7;vector<mst_case::MstEdge>e;for(int u=1;u<=n;++u)for(int v=u+1;v<=n;++v)if(rng()%2)e.push_back({u,v,(int)(rng()%31)-15});auto got=mst_case::kruskal(n,e);long long best=LLONG_MAX;int m=e.size();
        if(m<=20)for(int mask=0;mask<(1<<m);++mask)if(__builtin_popcount((unsigned)mask)==n-1){vector<int>p(n+1);iota(p.begin(),p.end(),0);function<int(int)>f=[&](int x){return p[x]==x?x:p[x]=f(p[x]);};long long c=0;bool ok=1;for(int i=0;i<m;++i)if(mask>>i&1){int a=f(e[i].u),b=f(e[i].v);if(a==b){ok=0;break;}p[a]=b;c+=e[i].w;}if(ok)best=min(best,c);}
        bool connected=n<=1||best!=LLONG_MAX;if(got.connected!=connected||connected&&got.cost!=best)return 1;}
    for(int round=0;round<1000;++round){using namespace scc_case;for(auto&v:g)v.clear();fill(dfn.begin(),dfn.end(),0);fill(low.begin(),low.end(),0);fill(in.begin(),in.end(),0);fill(comp.begin(),comp.end(),0);stk.clear();timer=cc=0;int used=1+rng()%25;for(int u=0;u<used;++u)for(int v=0;v<used;++v)if(rng()%5==0)g[u].push_back(v);for(int u=0;u<used;++u)if(!dfn[u])tarjan(u);vector<vector<char>>r(used,vector<char>(used));for(int s=0;s<used;++s){queue<int>q;q.push(s);r[s][s]=1;while(!q.empty()){int u=q.front();q.pop();for(int v:g[u])if(!r[s][v])r[s][v]=1,q.push(v);}}for(int u=0;u<used;++u)for(int v=0;v<used;++v)if((comp[u]==comp[v])!=(r[u][v]&&r[v][u]))return 2;}
    for(int round=0;round<1000;++round){using namespace bridge_case;for(auto&v:g)v.clear();fill(dfn.begin(),dfn.end(),0);fill(low.begin(),low.end(),0);bridges.clear();timer=0;int used=1+rng()%20,id=0;vector<pair<int,int>>es;for(int u=0;u<used;++u)for(int v=u+1;v<used;++v)if(rng()%5==0){es.push_back({u,v});g[u].push_back({v,id});g[v].push_back({u,id++});}for(int u=0;u<used;++u)if(!dfn[u])dfs(u,-1);set<pair<int,int>>got;for(auto [u,v]:bridges)got.insert(minmax(u,v));set<pair<int,int>>want;for(int ban=0;ban<id;++ban){auto [s,t]=es[ban];vector<char>vis(used);queue<int>q;q.push(s);vis[s]=1;while(!q.empty()){int u=q.front();q.pop();for(auto [v,eid]:g[u])if(eid!=ban&&!vis[v])vis[v]=1,q.push(v);}if(!vis[t])want.insert({s,t});}if(got!=want)return 3;}
    for(int round=0;round<800;++round){using namespace mcmf_case;for(auto&v:mg)v.clear();vector<tuple<int,int,int,int>>es;int used=2+rng()%9;for(int u=0;u<used;++u)for(int v=u+1;v<used;++v)if(rng()%3==0){int cap=1+rng()%4,cost=(int)(rng()%21)-5;es.push_back({u,v,cap,cost});add_edge(u,v,cap,cost);}int need=rng()%10;auto got=min_cost_flow(0,used-1,need),want=reference_mcmf(used,es,0,used-1,need);if(got!=want)return 4;}
    for(int round=0;round<1000;++round){using namespace lca_case;int n=1+rng()%200;for(auto&v:tree)v.clear();memset(up,0,sizeof(up));memset(dep,0,sizeof(dep));vector<int>par(n+1);for(int v=2;v<=n;++v){par[v]=1+rng()%(v-1);tree[v].push_back(par[v]);tree[par[v]].push_back(v);}init_lca(1,0);for(int q=0;q<500;++q){int u=1+rng()%n,v=1+rng()%n,a=u,b=v;set<int>anc;while(a)anc.insert(a),a=par[a];while(!anc.count(b))b=par[b];if(lca(u,v)!=b)return 5;}}
    for(int round=0;round<1000;++round){using namespace farthest_case;n=1+rng()%100;weighted_tree.assign(n,{});for(int v=1;v<n;++v){int p=rng()%v,w=rng()%50;weighted_tree[v].push_back({p,w});weighted_tree[p].push_back({v,w});}int s=rng()%n;auto got=farthest(s);vector<long long>d(n,-1);d[s]=0;queue<int>q;q.push(s);while(!q.empty()){int u=q.front();q.pop();for(auto[v,w]:weighted_tree[u])if(d[v]<0)d[v]=d[u]+w,q.push(v);}long long best=*max_element(d.begin(),d.end());if(got.second!=best||d[got.first]!=best)return 6;}
    cout<<"graph complete contracts: PASS\n";
}
