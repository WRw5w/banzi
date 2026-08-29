#include <bits/stdc++.h>
using namespace std;

namespace bfs_case {
// @@@BFS@@@
}
namespace multi_bfs_case {
// @@@MULTI_BFS@@@
}
namespace topo_case {
vector<int> run(const vector<vector<pair<int,int>>>& graph) {
    auto g=graph; int n=(int)g.size(); vector<int>indeg(n);for(auto&e:g)for(auto[v,w]:e)++indeg[v];
// @@@TOPO@@@
    return topo;
}
}
namespace dijkstra_case {
vector<long long> run(const vector<vector<pair<int,int>>>& graph,int source){auto g=graph;int n=g.size(),s=source;const long long INF=(1LL<<60);
// @@@DIJKSTRA@@@
    return dist;
}
}
namespace zero_one_case {
vector<int> run(const vector<vector<pair<int,int>>>& graph,int source){auto zero_one_graph=graph;int n=graph.size(),s=source;const int INF=1e9;
// @@@ZERO_ONE_BFS@@@
    return d;
}
}
namespace zero_one_duplicate_case {
// @@@DIFFERENCE_CONSTRAINTS@@@
}
namespace bipartite_case {
pair<bool,vector<int>> run(const vector<vector<int>>& graph){auto g=graph;int n=g.size();
// @@@BIPARTITE_COLOR@@@
    return {ok,color};
}
}
namespace matching_case {
// @@@BIPARTITE_MATCHING@@@
}

vector<int> unit_reference(const vector<vector<int>>&g,const vector<int>&sources){int n=g.size();vector<int>d(n,-1);queue<int>q;for(int s:sources)if(d[s]<0)d[s]=0,q.push(s);while(!q.empty()){int u=q.front();q.pop();for(int v:g[u])if(d[v]<0)d[v]=d[u]+1,q.push(v);}return d;}
vector<long long> bellman(const vector<vector<pair<int,int>>>&g,int s){int n=g.size();const long long INF=1LL<<60;vector<long long>d(n,INF);d[s]=0;for(int it=1;it<n;++it)for(int u=0;u<n;++u)if(d[u]<INF)for(auto[v,w]:g[u])d[v]=min(d[v],d[u]+w);return d;}

int main(){mt19937 rng(20260829);
    for(int round=0;round<1000;++round){int n=1+rng()%40;vector<vector<int>>g(n);for(int u=0;u<n;++u)for(int v=0;v<n;++v)if(rng()%8==0)g[u].push_back(v);int s=rng()%n;auto want=unit_reference(g,{s});if(bfs_case::bfs_dist(g,s)!=want)return 1;vector<int>sources;for(int i=0;i<n;++i)if(rng()%7==0)sources.push_back(i);if(sources.empty())sources.push_back(s);if(multi_bfs_case::multi_source_bfs(g,sources)!=unit_reference(g,sources))return 2;}
    for(int round=0;round<1000;++round){int n=1+rng()%30;vector<vector<pair<int,int>>>g(n);for(int u=0;u<n;++u)for(int v=u+1;v<n;++v)if(rng()%5==0)g[u].push_back({v,1});auto topo=topo_case::run(g),pos=vector<int>(n);if((int)topo.size()!=n)return 3;for(int i=0;i<n;++i)pos[topo[i]]=i;for(int u=0;u<n;++u)for(auto[v,w]:g[u])if(pos[u]>=pos[v])return 4;if(n>1){g[n-1].push_back({0,1});g[0].push_back({n-1,1});bool threw=0;try{topo_case::run(g);}catch(const runtime_error&){threw=1;}if(!threw)return 5;}}
    for(int round=0;round<1000;++round){int n=1+rng()%30;vector<vector<pair<int,int>>>g(n),z(n);for(int u=0;u<n;++u)for(int v=0;v<n;++v)if(rng()%8==0){int w=rng()%30;g[u].push_back({v,w});z[u].push_back({v,w&1});}int s=rng()%n;if(dijkstra_case::run(g,s)!=bellman(g,s))return 6;auto want=bellman(z,s);auto got=zero_one_case::run(z,s);for(int i=0;i<n;++i){int w=want[i]>1e8?1000000000:(int)want[i];if(got[i]!=w)return 7;}}
    for(int round=0;round<1000;++round){int n=1+rng()%30;vector<long long>potential(n);for(auto&x:potential)x=(int)(rng()%101)-50;vector<tuple<int,int,long long>>edges;for(int u=0;u<n;++u)for(int v=0;v<n;++v)if(rng()%8==0)edges.push_back({u,v,potential[v]-potential[u]+(int)(rng()%20)});auto got=zero_one_duplicate_case::difference_constraints(n,edges);if(!got)return 11;for(auto[u,v,w]:edges)if((*got)[v]>(*got)[u]+w)return 12;edges.push_back({0,0,-1});if(zero_one_duplicate_case::difference_constraints(n,edges))return 13;}
    for(int round=0;round<1000;++round){int n=1+rng()%30;vector<vector<int>>g(n);bool want=1;vector<int>hidden(n);for(int&i:hidden)i=rng()&1;for(int u=0;u<n;++u)for(int v=u+1;v<n;++v)if(rng()%8==0&&hidden[u]!=hidden[v])g[u].push_back(v),g[v].push_back(u);if(rng()%4==0&&n>=3){g[0].push_back(1);g[1].push_back(0);g[1].push_back(2);g[2].push_back(1);g[2].push_back(0);g[0].push_back(2);want=0;}auto got=bipartite_case::run(g);if(got.first!=want)return 8;if(got.first)for(int u=0;u<n;++u)for(int v:g[u])if(got.second[u]==got.second[v])return 9;}
    for(int round=0;round<1000;++round){int l=rng()%9,r=rng()%9;vector<vector<int>>g(l);for(int u=0;u<l;++u)for(int v=0;v<r;++v)if(rng()%2)g[u].push_back(v);int want=0;for(int mask=0;mask<(1<<r);++mask){int used=__builtin_popcount((unsigned)mask);if(used<=want||used>l)continue;vector<int>rights;for(int v=0;v<r;++v)if(mask>>v&1)rights.push_back(v);bool ok=0;sort(rights.begin(),rights.end());do{vector<char>left(l);function<bool(int)>dfs=[&](int i){if(i==(int)rights.size())return true;for(int u=0;u<l;++u)if(!left[u]&&find(g[u].begin(),g[u].end(),rights[i])!=g[u].end()){left[u]=1;if(dfs(i+1))return true;left[u]=0;}return false;};if(dfs(0)){ok=1;break;}}while(next_permutation(rights.begin(),rights.end()));if(ok)want=used;}if(matching_case::max_bipartite_matching(g,r)!=want)return 10;}
    cout<<"graph foundation contracts: PASS\n";
}
