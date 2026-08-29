#include <bits/stdc++.h>
using namespace std;

namespace centroid_case {
constexpr int MAXN=256;vector<int>tree[MAXN];int sz[MAXN];bool removed[MAXN];
// @@@CENTROID_DECOMPOSITION@@@
}
namespace dsu_case {
constexpr int n=255,MAXC=64;vector<vector<int>>tree(n+1);
// @@@DSU_ON_TREE@@@
}

int main(){mt19937 rng(20260829);
    for(int round=0;round<1000;++round){using namespace centroid_case;int used=1+rng()%200;for(auto&v:tree)v.clear();memset(removed,0,sizeof(removed));for(int v=2;v<=used;++v){int p=1+rng()%(v-1);tree[p].push_back(v);tree[v].push_back(p);}int total=get_size(1,0),c=get_centroid(1,0,total);removed[c]=1;int largest=used-1;for(int v:tree[c])if(!removed[v])largest=max(largest,0);removed[c]=0;for(int v:tree[c]){int part=get_size(v,c);if(part*2>total)return 1;}divide(1);for(int v=1;v<=used;++v)if(!removed[v])return 2;}
    for(int round=0;round<500;++round){using namespace dsu_case;int used=1+rng()%200;for(auto&v:tree)v.clear();fill(sz.begin(),sz.end(),0);fill(heavy.begin(),heavy.end(),0);fill(freq.begin(),freq.end(),0);fill(answer.begin(),answer.end(),0);distinct=0;vector<int>parent(used+1);for(int v=2;v<=used;++v){parent[v]=1+rng()%(v-1);tree[v].push_back(parent[v]);tree[parent[v]].push_back(v);}for(int v=1;v<=used;++v)color[v]=rng()%MAXC;dfs_size(1,0);dsu_on_tree(1,0,true);for(int u=1;u<=used;++u){set<int>colors;for(int v=u;v<=used;++v){int x=v;while(x&&x!=u)x=parent[x];if(x==u)colors.insert(color[v]);}if(answer[u]!=(int)colors.size())return 3;}add_subtree(1,0,-1);if(distinct!=0)return 4;}
    cout<<"tree framework contracts: PASS\n";
}
