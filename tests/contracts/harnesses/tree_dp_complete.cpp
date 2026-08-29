#include <bits/stdc++.h>
using namespace std;
namespace first_case { long long tree[2048]; // @@@FIRST_AT_LEAST@@@
}
namespace first_detail_case {struct Node{long long mx;};Node tr[2048];void push(int,int,int){} // @@@FIRST_DETAIL@@@
}
namespace euler_case {constexpr int n=256;vector<int>tree[n]; // @@@EULER@@@
}
namespace diff_case {constexpr int N=256;vector<int>tree[N];long long diff[N];int up[N][1];int parent[N],depth[N];int lca(int a,int b){while(depth[a]>depth[b])a=parent[a];while(depth[b]>depth[a])b=parent[b];while(a!=b)a=parent[a],b=parent[b];return a;} // @@@TREE_DIFF@@@
}
namespace indep_case {constexpr int N=256;vector<int>tree[N];long long dp[N][2],weight[N]; // @@@TREE_DP@@@
}
namespace hld_case {constexpr int N=256;vector<int>tree[N];int parent[N],size[N],heavy[N],dep[N],top[N],dfn[N],timer;long long flat[N];struct Seg{long long query(int l,int r){long long s=0;for(int i=l;i<=r;++i)s+=flat[i];return s;}}seg; // @@@HLD@@@
}
namespace long_case {constexpr int n=256;vector<int>tree[n+1]; // @@@LONG_CHAIN@@@
}
namespace reroot_case {int n;vector<int>tree[256];long long sz[256],down[256],ans[256]; // @@@REROOT@@@
}
namespace memo_case {constexpr int MAXN=256;vector<vector<int>> next;vector<vector<int>>gain; // @@@MEMO_DAG@@@
}
namespace grundy_case {constexpr int MAXG=256;int memo[256];vector<int>moves[256]; // @@@GRUNDY@@@
}
namespace long_detail_case {vector<int>g[256];int up[256],len[256],son[256],chain_top[256],chain_pos[256],timer; // @@@LONG_CHAIN_DETAIL@@@
}
int main(){mt19937 rng(20260829);
 for(int round=0;round<500;++round){int n=1+rng()%100;vector<long long>a(n);for(auto&x:a)x=(int)(rng()%201)-100;fill(begin(first_case::tree),end(first_case::tree),LLONG_MIN);function<void(int,int,int)>build=[&](int p,int l,int r){if(l==r){first_case::tree[p]=a[l];return;}int m=(l+r)/2;build(p*2,l,m);build(p*2+1,m+1,r);first_case::tree[p]=max(first_case::tree[p*2],first_case::tree[p*2+1]);};build(1,0,n-1);for(int x=-110;x<=110;++x){int want=-1;for(int i=0;i<n;++i)if(a[i]>=x){want=i;break;}if(first_case::first_at_least(1,0,n-1,x)!=want)return 1;}for(int i=0;i<2048;++i)first_detail_case::tr[i].mx=first_case::tree[i];for(int x=-110;x<=110;++x)if(first_detail_case::first_at_least(1,0,n-1,x)!=first_case::first_at_least(1,0,n-1,x))return 2;}
 for(int round=0;round<300;++round){int n=1+rng()%200;vector<int>p(n);for(int i=0;i<256;++i)euler_case::tree[i].clear();for(int v=1;v<n;++v){p[v]=rng()%v;euler_case::tree[v].push_back(p[v]);euler_case::tree[p[v]].push_back(v);}euler_case::timer=0;fill(euler_case::tin.begin(),euler_case::tin.end(),0);fill(euler_case::tout.begin(),euler_case::tout.end(),0);fill(euler_case::depth.begin(),euler_case::depth.end(),0);euler_case::dfs(0,-1);for(int u=0;u<n;++u){if(euler_case::tin[u]>euler_case::tout[u])return 3;for(int v=0;v<n;++v){int x=v;while(x&&x!=u)x=p[x];bool desc=x==u;if(desc!=(euler_case::tin[u]<=euler_case::tin[v]&&euler_case::tin[v]<=euler_case::tout[u]))return 4;}}}
 for(int round=0;round<300;++round){using namespace diff_case;int used=1+rng()%150;for(auto&v:tree)v.clear();memset(diff,0,sizeof(diff));parent[1]=0;depth[1]=0;for(int v=2;v<=used;++v){parent[v]=1+rng()%(v-1);depth[v]=depth[parent[v]]+1;tree[v].push_back(parent[v]);tree[parent[v]].push_back(v);}for(int i=1;i<=used;++i)up[i][0]=parent[i];vector<long long>want(used+1);for(int q=0;q<300;++q){int u=1+rng()%used,v=1+rng()%used;add_path(u,v);int a=u,b=v,l=lca(a,b);while(a!=l)++want[a],a=parent[a];while(b!=l)++want[b],b=parent[b];++want[l];}collect(1,0);for(int i=1;i<=used;++i)if(diff[i]!=want[i])return 5;}
 for(int round=0;round<300;++round){using namespace indep_case;int n=1+rng()%20;for(auto&v:tree)v.clear();for(int i=0;i<n;++i)weight[i]=(int)(rng()%41)-20;for(int v=1;v<n;++v){int p=rng()%v;tree[v].push_back(p);tree[p].push_back(v);}tree_dp(0,-1);long long want=LLONG_MIN;for(int mask=0;mask<(1<<n);++mask){bool ok=1;long long s=0;for(int u=0;u<n;++u)if(mask>>u&1){s+=weight[u];for(int v:tree[u])if(mask>>v&1)ok=0;}if(ok)want=max(want,s);}if(max(dp[0][0],dp[0][1])!=want)return 6;}
 for(int round=0;round<300;++round){using namespace hld_case;int n=1+rng()%200;for(auto&v:tree)v.clear();memset(parent,0,sizeof(parent));memset(hld_case::size,0,sizeof(hld_case::size));memset(heavy,0,sizeof(heavy));memset(dep,0,sizeof(dep));memset(top,0,sizeof(top));memset(dfn,0,sizeof(dfn));timer=0;vector<long long>w(n);for(auto&x:w)x=(int)(rng()%101)-50;for(int v=1;v<n;++v){int p=rng()%v;tree[v].push_back(p);tree[p].push_back(v);}dfs1(0,0);dfs2(0,0);for(int i=0;i<n;++i)flat[dfn[i]]=w[i];for(int q=0;q<500;++q){int u=rng()%n,v=rng()%n,a=u,b=v;set<int>anc;while(1){anc.insert(a);if(a==0)break;a=parent[a];}while(!anc.count(b))b=parent[b];long long want=0;for(a=u;a!=b;a=parent[a])want+=w[a];for(a=v;a!=b;a=parent[a])want+=w[a];want+=w[b];if(path_sum(u,v)!=want)return 7;}}
 for(int round=0;round<300;++round){using namespace long_case;for(auto&v:tree)v.clear();fill(parent2.begin(),parent2.end(),0);fill(depth2.begin(),depth2.end(),0);fill(heavy_len.begin(),heavy_len.end(),0);fill(heavy2.begin(),heavy2.end(),0);fill(top2.begin(),top2.end(),0);int used=1+rng()%200;for(int v=2;v<=used;++v){int p=1+rng()%(v-1);tree[v].push_back(p);tree[p].push_back(v);}long_chain_dfs1(1,0);long_chain_dfs2(1,1);for(int u=1;u<=used;++u){if(heavy2[u]&&top2[heavy2[u]]!=top2[u])return 8;for(int v:tree[u])if(parent2[v]==u&&v!=heavy2[u]&&top2[v]!=v)return 9;}}
 for(int round=0;round<300;++round){using namespace reroot_case;int used=1+rng()%200;n=used;for(auto&v:tree)v.clear();for(int v=1;v<used;++v){int p=rng()%v;tree[v].push_back(p);tree[p].push_back(v);}fill(begin(sz),end(sz),0);fill(begin(down),end(down),0);fill(begin(ans),end(ans),0);reroot1(0,-1);ans[0]=down[0];reroot2(0,-1);for(int s=0;s<used;++s){vector<int>d(used,-1);queue<int>q;q.push(s);d[s]=0;while(!q.empty()){int u=q.front();q.pop();for(int v:tree[u])if(d[v]<0)d[v]=d[u]+1,q.push(v);}if(ans[s]!=accumulate(d.begin(),d.end(),0LL))return 10;}}
 for(int round=0;round<300;++round){using namespace memo_case;int n=1+rng()%150;memo_case::next.assign(n,{});gain.assign(n,vector<int>(n));for(int u=0;u<n;++u)for(int v=u+1;v<n;++v)if(rng()%5==0)memo_case::next[u].push_back(v),gain[u][v]=(int)(rng()%31)-10;fill(begin(memo),end(memo),-1);vector<int>w(n);for(int u=n-1;u>=0;--u)for(int v:memo_case::next[u])w[u]=max(w[u],w[v]+gain[u][v]);for(int u=0;u<n;++u)if(solve(u)!=w[u])return 11;}
 for(int round=0;round<300;++round){using namespace grundy_case;int n=1+rng()%150;for(auto&v:moves)v.clear();for(int u=0;u<n;++u)for(int v=u+1;v<n;++v)if(rng()%5==0)moves[u].push_back(v);fill(begin(memo),end(memo),-1);vector<int>w(n);for(int u=n-1;u>=0;--u){set<int>s;for(int v:moves[u])s.insert(w[v]);while(s.count(w[u]))++w[u];if(grundy(u)!=w[u])return 12;}}
 for(int round=0;round<300;++round){using namespace long_detail_case;for(auto&v:g)v.clear();memset(up,0,sizeof(up));memset(len,0,sizeof(len));memset(son,0,sizeof(son));memset(chain_top,0,sizeof(chain_top));memset(chain_pos,0,sizeof(chain_pos));timer=0;int n=1+rng()%200;for(int v=2;v<=n;++v){int p=1+rng()%(v-1);g[v].push_back(p);g[p].push_back(v);}dfs_len(1,0);dfs_chain(1,1);for(int u=1;u<=n;++u){if(son[u]&&chain_top[son[u]]!=chain_top[u])return 13;for(int v:g[u])if(up[v]==u&&v!=son[u]&&chain_top[v]!=v)return 14;}}
 cout<<"tree/dp complete contracts: PASS\n";
}
