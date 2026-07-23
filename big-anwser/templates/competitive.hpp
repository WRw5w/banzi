// 区域赛银牌 / Codeforces <= 2200 常用模板（C++17）
#pragma once
#include <bits/stdc++.h>
using namespace std;
using i64 = long long;
using i128 = __int128_t;
const i64 INF64 = (1LL << 62);

// ==================== 基础数学 ====================
inline i64 mod_pow(i64 a, i64 e, i64 mod) {
    a %= mod; i64 r = 1 % mod;
    while (e) { if (e & 1) r = (i128)r * a % mod; a = (i128)a * a % mod; e >>= 1; }
    return r;
}
inline i64 exgcd(i64 a, i64 b, i64 &x, i64 &y) {
    if (!b) { x = 1; y = 0; return a; }
    i64 x1, y1, g = exgcd(b, a % b, x1, y1);
    x = y1; y = x1 - (a / b) * y1; return g;
}
inline i64 inv_mod(i64 a, i64 mod) {
    i64 x, y, g = exgcd(a, mod, x, y);
    assert(g == 1); x %= mod; if (x < 0) x += mod; return x;
}

struct LinearSieve {
    vector<int> primes, lp, phi;
    LinearSieve(int n = 0) { if (n) init(n); }
    void init(int n) {
        lp.assign(n + 1, 0); phi.assign(n + 1, 0); primes.clear();
        if (n >= 1) phi[1] = 1;
        for (int i = 2; i <= n; ++i) {
            if (!lp[i]) lp[i] = i, primes.push_back(i), phi[i] = i - 1;
            for (int p : primes) {
                if (p > lp[i] || 1LL * i * p > n) break;
                lp[i * p] = p;
                phi[i * p] = (p == lp[i] ? phi[i] * p : phi[i] * (p - 1));
            }
        }
    }
};

struct DSU {
    vector<int> p, sz;
    DSU(int n = 0) { init(n); }
    void init(int n) { p.resize(n + 1); sz.assign(n + 1, 1); iota(p.begin(), p.end(), 0); }
    int find(int x) { return p[x] == x ? x : p[x] = find(p[x]); }
    bool unite(int a, int b) {
        a = find(a); b = find(b); if (a == b) return false;
        if (sz[a] < sz[b]) swap(a, b); p[b] = a; sz[a] += sz[b]; return true;
    }
};

struct Fenwick {
    int n; vector<i64> bit;
    Fenwick(int n = 0) { init(n); }
    void init(int n_) { n = n_; bit.assign(n + 1, 0); }
    void add(int x, i64 v) { for (; x <= n; x += x & -x) bit[x] += v; }
    i64 sum(int x) const { i64 r = 0; for (; x; x -= x & -x) r += bit[x]; return r; }
    i64 rangeSum(int l, int r) const { return sum(r) - sum(l - 1); }
    // bit 上二进制提升：返回最小的 idx，使 sum(idx) >= k（k>=1）
    int kth(i64 k) const {
        int x = 0; for (int d = 1 << (31 - __builtin_clz(n)); d; d >>= 1)
            if (x + d <= n && bit[x + d] < k) x += d, k -= bit[x + d];
        return x + 1;
    }
};

// 区间加、区间和
struct LazySegTree {
    int n; vector<i64> sum, tag;
    LazySegTree(int n = 0) { init(n); }
    void init(int n_) { n = n_; sum.assign(4 * n + 4, 0); tag.assign(4 * n + 4, 0); }
    void apply(int p, int l, int r, i64 v) { sum[p] += v * (r - l + 1); tag[p] += v; }
    void push(int p, int l, int r) {
        if (!tag[p] || l == r) return; int m = (l + r) >> 1;
        apply(p << 1, l, m, tag[p]); apply(p << 1 | 1, m + 1, r, tag[p]); tag[p] = 0;
    }
    void add(int p, int l, int r, int ql, int qr, i64 v) {
        if (ql <= l && r <= qr) return apply(p, l, r, v);
        push(p, l, r); int m = (l + r) >> 1;
        if (ql <= m) add(p << 1, l, m, ql, qr, v);
        if (qr > m) add(p << 1 | 1, m + 1, r, ql, qr, v);
        sum[p] = sum[p << 1] + sum[p << 1 | 1];
    }
    i64 query(int p, int l, int r, int ql, int qr) {
        if (ql <= l && r <= qr) return sum[p];
        push(p, l, r); int m = (l + r) >> 1; i64 ans = 0;
        if (ql <= m) ans += query(p << 1, l, m, ql, qr);
        if (qr > m) ans += query(p << 1 | 1, m + 1, r, ql, qr); return ans;
    }
    void add(int l, int r, i64 v) { if (l <= r) add(1, 1, n, l, r, v); }
    i64 query(int l, int r) { return l <= r ? query(1, 1, n, l, r) : 0; }
};

struct SparseTable {
    int n, K; vector<int> lg; vector<vector<i64>> st;
    SparseTable() = default;
    explicit SparseTable(const vector<i64>& a) { init(a); }
    void init(const vector<i64>& a) {
        n = (int)a.size(); K = 1; while ((1 << K) <= n) ++K;
        lg.assign(n + 1, 0); for (int i = 2; i <= n; ++i) lg[i] = lg[i >> 1] + 1;
        st.assign(K, vector<i64>(n)); st[0] = a;
        for (int j = 1; j < K; ++j) for (int i = 0; i + (1 << j) <= n; ++i)
            st[j][i] = min(st[j - 1][i], st[j - 1][i + (1 << (j - 1))]);
    }
    i64 query(int l, int r) const { int k = lg[r - l + 1]; return min(st[k][l], st[k][r - (1 << k) + 1]); }
};

struct LinearBasis {
    static constexpr int LOG = 63; unsigned long long b[LOG]{};
    bool insert(unsigned long long x) {
        for (int i = LOG - 1; i >= 0; --i) if ((x >> i) & 1) {
            if (!b[i]) { b[i] = x; return true; } x ^= b[i];
        } return false;
    }
    unsigned long long maxXor(unsigned long long x = 0) const {
        for (int i = LOG - 1; i >= 0; --i) x = max(x, x ^ b[i]); return x;
    }
    bool represent(unsigned long long x) const {
        for (int i = LOG - 1; i >= 0; --i) if ((x >> i) & 1) x ^= b[i]; return x == 0;
    }
};

// ==================== 图论 ====================
struct WEdge { int to; i64 w; };

inline vector<i64> dijkstra(int n, const vector<vector<WEdge>>& g, int s) {
    vector<i64> d(n + 1, INF64); priority_queue<pair<i64,int>, vector<pair<i64,int>>, greater<>> pq;
    d[s] = 0; pq.push({0, s});
    while (!pq.empty()) {
        auto [du, u] = pq.top(); pq.pop(); if (du != d[u]) continue;
        for (auto e : g[u]) if (d[e.to] > du + e.w) d[e.to] = du + e.w, pq.push({d[e.to], e.to});
    } return d;
}

inline vector<i64> zero_one_bfs(int n, const vector<vector<WEdge>>& g, int s) {
    vector<i64> d(n + 1, INF64); deque<int> q; d[s] = 0; q.push_front(s);
    while (!q.empty()) { int u = q.front(); q.pop_front();
        for (auto e : g[u]) if (d[e.to] > d[u] + e.w) {
            d[e.to] = d[u] + e.w; if (e.w == 0) q.push_front(e.to); else q.push_back(e.to);
        }
    } return d;
}

inline i64 kruskal(int n, vector<tuple<i64,int,int>> edges) {
    sort(edges.begin(), edges.end()); DSU dsu(n); i64 ans = 0; int cnt = 0;
    for (auto [w,u,v] : edges) if (dsu.unite(u,v)) ans += w, ++cnt;
    return cnt == n - 1 ? ans : INF64;
}

inline vector<int> topo_sort(int n, const vector<vector<int>>& g) {
    vector<int> deg(n+1); for(int u=1;u<=n;++u)for(int v:g[u])++deg[v]; queue<int>q;for(int i=1;i<=n;++i)if(!deg[i])q.push(i);vector<int>ord;
    while(!q.empty()){int u=q.front();q.pop();ord.push_back(u);for(int v:g[u])if(!--deg[v])q.push(v);}return ord; // size<n 表示有环
}

// 无向图欧拉路：边 id 从 0 开始；返回点序列，空表示不存在
inline vector<int> euler_path_undirected(int n, const vector<pair<int,int>>& edges) {
    vector<vector<pair<int,int>>> g(n+1);for(int i=0;i<(int)edges.size();++i){auto [u,v]=edges[i];g[u].push_back({v,i});g[v].push_back({u,i});}
    int s=1,odd=0;for(int i=1;i<=n;++i){if(g[i].size()&1)s=i,++odd;if(!g[i].empty()&&s==1)s=i;}if(odd!=0&&odd!=2)return{};vector<char>used(edges.size());vector<int>it(n+1),st,ans;st.push_back(s);
    while(!st.empty()){int u=st.back();while(it[u]<(int)g[u].size()&&used[g[u][it[u]].second])++it[u];if(it[u]==(int)g[u].size())ans.push_back(u),st.pop_back();else{auto [v,id]=g[u][it[u]++];if(!used[id])used[id]=1,st.push_back(v);}}
    if(ans.size()!=edges.size()+1)return{};reverse(ans.begin(),ans.end());return ans;
}

struct SCC {
    int n, timer = 0, cc = 0; vector<vector<int>> g; vector<int> dfn, low, stk, in, comp;
    SCC(int n=0): n(n), g(n+1), dfn(n+1), low(n+1), in(n+1), comp(n+1,-1) {}
    void addEdge(int u,int v){g[u].push_back(v);}
    void dfs(int u){
        dfn[u]=low[u]=++timer; stk.push_back(u); in[u]=1;
        for(int v:g[u]) if(!dfn[v]) dfs(v), low[u]=min(low[u],low[v]); else if(in[v]) low[u]=min(low[u],dfn[v]);
        if(low[u]==dfn[u]){ while(1){int v=stk.back();stk.pop_back();in[v]=0;comp[v]=cc;if(v==u)break;} ++cc; }
    }
    int run(){for(int i=1;i<=n;++i)if(!dfn[i])dfs(i);return cc;}
};

struct BridgeFinder {
    int n, timer=0; vector<vector<pair<int,int>>> g; vector<int> dfn,low,isCut; vector<pair<int,int>> bridges;
    BridgeFinder(int n=0):n(n),g(n+1),dfn(n+1),low(n+1),isCut(n+1){}
    void addEdge(int u,int v){int id=bridges.size(); g[u].push_back({v,id});g[v].push_back({u,id});bridges.push_back({-1,-1});}
    void dfs(int u,int pe=-1){
        dfn[u]=low[u]=++timer; int child=0;
        for(auto [v,id]:g[u]){if(id==pe)continue; if(!dfn[v]){++child;dfs(v,id);low[u]=min(low[u],low[v]);
                if(low[v]>=dfn[u])isCut[u]=(pe!=-1||child>1); if(low[v]>dfn[u])bridges[id]={u,v};}
            else low[u]=min(low[u],dfn[v]);}
    }
    void run(){for(int i=1;i<=n;++i)if(!dfn[i])dfs(i);}
};

struct Dinic {
    struct E { int to, rev; i64 cap; };
    int n; vector<vector<E>> g; vector<int> level, it;
    Dinic(int n=0):n(n),g(n+1),level(n+1),it(n+1){}
    void addEdge(int u,int v,i64 c){E a{v,(int)g[v].size(),c},b{u,(int)g[u].size(),0};g[u].push_back(a);g[v].push_back(b);}
    bool bfs(int s,int t){fill(level.begin(),level.end(),-1);queue<int>q;q.push(s);level[s]=0;while(!q.empty()){int u=q.front();q.pop();for(auto&e:g[u])if(e.cap&&level[e.to]<0)level[e.to]=level[u]+1,q.push(e.to);}return level[t]>=0;}
    i64 dfs(int u,int t,i64 f){if(u==t)return f;for(int &i=it[u];i<(int)g[u].size();++i){E&e=g[u][i];if(e.cap&&level[e.to]==level[u]+1){i64 z=dfs(e.to,t,min(f,e.cap));if(z){e.cap-=z;g[e.to][e.rev].cap+=z;return z;}}}return 0;}
    i64 maxflow(int s,int t){i64 ans=0,z;while(bfs(s,t)){fill(it.begin(),it.end(),0);while((z=dfs(s,t,INF64)))ans+=z;}return ans;}
};

struct MinCostMaxFlow {
    struct E { int to, rev; i64 cap, cost; };
    int n; vector<vector<E>> g;
    MinCostMaxFlow(int n=0):n(n),g(n+1){}
    void addEdge(int u,int v,i64 cap,i64 cost){E a{v,(int)g[v].size(),cap,cost},b{u,(int)g[u].size(),0,-cost};g[u].push_back(a);g[v].push_back(b);}
    pair<i64,i64> run(int s,int t){i64 flow=0,cost=0;vector<i64>d(n+1),pot(n+1),f(n+1);vector<int>pv(n+1),pe(n+1);
        while(1){fill(d.begin(),d.end(),INF64);d[s]=0;priority_queue<pair<i64,int>,vector<pair<i64,int>>,greater<>>q;q.push({0,s});
            while(!q.empty()){auto [du,u]=q.top();q.pop();if(du!=d[u])continue;for(int i=0;i<(int)g[u].size();++i){auto&e=g[u][i];if(e.cap&&d[e.to]>du+e.cost+pot[u]-pot[e.to])d[e.to]=du+e.cost+pot[u]-pot[e.to],pv[e.to]=u,pe[e.to]=i,q.push({d[e.to],e.to});}}
            if(d[t]==INF64)break;for(int i=1;i<=n;++i)if(d[i]<INF64)pot[i]+=d[i];i64 add=INF64;for(int v=t;v!=s;v=pv[v])add=min(add,g[pv[v]][pe[v]].cap);
            for(int v=t;v!=s;v=pv[v]){E&e=g[pv[v]][pe[v]];cost+=add*e.cost;e.cap-=add;g[v][e.rev].cap+=add;}flow+=add;
        }return {flow,cost};}
};

struct LCA {
    int n, K; vector<int> dep; vector<vector<int>> up; vector<vector<i64>> mx;
    vector<vector<pair<int,i64>>> g;
    LCA(int n=0):n(n),K(0),dep(n+1),g(n+1){while((1<<K)<=max(1,n))++K;up.assign(K,vector<int>(n+1));mx.assign(K,vector<i64>(n+1,-INF64));}
    void addEdge(int u,int v,i64 w=0){g[u].push_back({v,w});g[v].push_back({u,w});}
    void dfs(int u,int p){for(auto [v,w]:g[u])if(v!=p){dep[v]=dep[u]+1;up[0][v]=u;mx[0][v]=w;dfs(v,u);}}
    void build(int root=1){dep[root]=0;up[0][root]=root;mx[0][root]=-INF64;dfs(root,0);for(int j=1;j<K;++j)for(int i=1;i<=n;++i)up[j][i]=up[j-1][up[j-1][i]],mx[j][i]=max(mx[j-1][i],mx[j-1][up[j-1][i]]);}
    int lca(int a,int b)const{if(dep[a]<dep[b])swap(a,b);int d=dep[a]-dep[b];for(int j=0;j<K;++j)if(d>>j&1)a=up[j][a];if(a==b)return a;for(int j=K-1;j>=0;--j)if(up[j][a]!=up[j][b])a=up[j][a],b=up[j][b];return up[0][a];}
    i64 pathMax(int a,int b)const{ i64 r=-INF64;if(dep[a]<dep[b])swap(a,b);int d=dep[a]-dep[b];for(int j=0;j<K;++j)if(d>>j&1)r=max(r,mx[j][a]),a=up[j][a];if(a==b)return r;for(int j=K-1;j>=0;--j)if(up[j][a]!=up[j][b])r=max({r,mx[j][a],mx[j][b]}),a=up[j][a],b=up[j][b];return max({r,mx[0][a],mx[0][b]});}
};

// 重链剖分：路径加/路径和的线段树接口需按题目替换
struct HLD {
    int n, timer=0; vector<vector<int>> g; vector<int> sz,dep,fa,son,top,dfn,rnk;
    HLD(int n=0):n(n),g(n+1),sz(n+1),dep(n+1),fa(n+1),son(n+1),top(n+1),dfn(n+1),rnk(n+1){}
    void addEdge(int u,int v){g[u].push_back(v);g[v].push_back(u);}
    void dfs1(int u,int p){sz[u]=1;fa[u]=p;dep[u]=dep[p]+1;for(int v:g[u])if(v!=p){dfs1(v,u);sz[u]+=sz[v];if(!son[u]||sz[v]>sz[son[u]])son[u]=v;}}
    void dfs2(int u,int tp){top[u]=tp;dfn[u]=++timer;rnk[timer]=u;if(son[u])dfs2(son[u],tp);for(int v:g[u])if(v!=fa[u]&&v!=son[u])dfs2(v,v);}
    void build(int root=1){dfs1(root,0);dfs2(root,root);}
    template<class F> void pathApply(int u,int v,F apply){while(top[u]!=top[v]){if(dep[top[u]]<dep[top[v]])swap(u,v);apply(dfn[top[u]],dfn[u]);u=fa[top[u]];}if(dep[u]>dep[v])swap(u,v);apply(dfn[u],dfn[v]);}
    template<class F> void subtreeApply(int u,F apply){apply(dfn[u],dfn[u]+sz[u]-1);}
};

// 虚树：传入关键点、DFS 序 tin/tout、LCA 函数，返回虚树父子边（节点数 O(k)）
template<class LcaFn>
vector<pair<int,int>> build_virtual_tree(vector<int> nodes,const vector<int>& tin,const vector<int>& tout,LcaFn lca){
    auto anc=[&](int u,int v){return tin[u]<=tin[v]&&tout[v]<=tout[u];};
    sort(nodes.begin(),nodes.end(),[&](int a,int b){return tin[a]<tin[b];});int old=nodes.size();for(int i=1;i<old;++i)nodes.push_back(lca(nodes[i-1],nodes[i]));
    sort(nodes.begin(),nodes.end(),[&](int a,int b){return tin[a]<tin[b];});nodes.erase(unique(nodes.begin(),nodes.end()),nodes.end());vector<pair<int,int>> edges;
    vector<int> stk;for(int v:nodes){while(!stk.empty()&&!anc(stk.back(),v))stk.pop_back();if(!stk.empty())edges.push_back({stk.back(),v});stk.push_back(v);}return edges;
}

struct RollbackDSU {
    vector<int> p,sz; vector<pair<int,int>> hist;
    RollbackDSU(int n=0){init(n);} void init(int n){p.resize(n+1);sz.assign(n+1,1);iota(p.begin(),p.end(),0);hist.clear();}
    int find(int x){while(p[x]!=x)x=p[x];return x;} int snapshot()const{return hist.size();}
    bool unite(int a,int b){a=find(a);b=find(b);if(a==b){hist.push_back({-1,-1});return false;}if(sz[a]<sz[b])swap(a,b);hist.push_back({b,sz[a]});p[b]=a;sz[a]+=sz[b];return true;}
    void rollback(int snap){while((int)hist.size()>snap){auto [b,old]=hist.back();hist.pop_back();if(b==-1)continue;int a=p[b];p[b]=b;sz[a]=old;}}
};

// 线段树分治时间：边在 [ql,qr) 存活，solve 回调当前时间点答案
struct DynamicConnectivity {
    int q; vector<vector<pair<int,int>>> seg; RollbackDSU dsu;
    DynamicConnectivity(int n,int q):q(q),seg(4*q+4),dsu(n){}
    void add(int p,int l,int r,int ql,int qr,pair<int,int> e){if(ql>=r||qr<=l)return;if(ql<=l&&r<=qr){seg[p].push_back(e);return;}int m=(l+r)>>1;add(p<<1,l,m,ql,qr,e);add(p<<1|1,m,r,ql,qr,e);}
    void add(int l,int r,pair<int,int> e){if(l<r)add(1,0,q,l,r,e);}
    template<class F> void dfs(int p,int l,int r,F answer){int snap=dsu.snapshot();for(auto [u,v]:seg[p])dsu.unite(u,v);if(r-l==1)answer(l,dsu);else{int m=(l+r)>>1;dfs(p<<1,l,m,answer);dfs(p<<1|1,m,r,answer);}dsu.rollback(snap);}
};

// 可持久化权值线段树：静态区间第 k 小。值域 [1,V]。
struct PersistentSegTree {
    struct Node{int l=0,r=0,sum=0;}; vector<Node> tr; vector<int> root;
    PersistentSegTree(int maxNodes=1){tr.reserve(maxNodes+1);tr.push_back({});}
    int update(int old,int l,int r,int pos){int cur=tr.size();tr.push_back(tr[old]);tr[cur].sum++;if(l<r){int m=(l+r)>>1;if(pos<=m)tr[cur].l=update(tr[old].l,l,m,pos);else tr[cur].r=update(tr[old].r,m+1,r,pos);}return cur;}
    int kth(int a,int b,int l,int r,int k){if(l==r)return l;int left=tr[tr[b].l].sum-tr[tr[a].l].sum,m=(l+r)>>1;return k<=left?kth(tr[a].l,tr[b].l,l,m,k):kth(tr[a].r,tr[b].r,m+1,r,k-left);}
};

// FHQ Treap：按 key 维护有序集合；需要序列时把 key 改为隐式 size
struct FHQTreap {
    struct Node{int l=0,r=0,sz=1; i64 key=0; unsigned pri=0;}; vector<Node> t{Node()}; mt19937 rng{(unsigned)chrono::steady_clock::now().time_since_epoch().count()};
    int size(int p){return p?t[p].sz:0;} void pull(int p){if(p)t[p].sz=1+size(t[p].l)+size(t[p].r);}
    int newNode(i64 k){t.push_back({0,0,1,k,(unsigned)rng()});return t.size()-1;}
    void split(int p,i64 key,int &a,int &b){if(!p){a=b=0;return;}if(t[p].key<=key)a=p,split(t[p].r,key,t[p].r,b);else b=p,split(t[p].l,key,a,t[p].l);pull(p);}
    int merge(int a,int b){if(!a||!b)return a?a:b;if(t[a].pri>t[b].pri){t[a].r=merge(t[a].r,b);pull(a);return a;}t[b].l=merge(a,t[b].l);pull(b);return b;}
    void insert(int &root,i64 key){int a,b;split(root,key,a,b);root=merge(merge(a,newNode(key)),b);}
    void erase(int &root,i64 key){int a,b,c;split(root,key,a,c);split(a,key-1,a,b);if(b)b=merge(t[b].l,t[b].r);root=merge(merge(a,b),c);}
    int kth(int p,int k){if(!p||k<1||k>size(p))return 0;int ls=size(t[p].l);return k==ls+1?p:k<=ls?kth(t[p].l,k):kth(t[p].r,k-ls-1);}
};

// 树的点分治骨架：collect 中按题意统计经过重心的贡献
struct CentroidDecomposition {
    int n; vector<vector<pair<int,i64>>> g; vector<int> sz; vector<char> dead;
    CentroidDecomposition(int n=0):n(n),g(n+1),sz(n+1),dead(n+1){}
    void addEdge(int u,int v,i64 w=1){g[u].push_back({v,w});g[v].push_back({u,w});}
    void getsz(int u,int p){sz[u]=1;for(auto [v,w]:g[u])if(v!=p&&!dead[v])getsz(v,u),sz[u]+=sz[v];}
    int getcen(int u,int p,int all){for(auto [v,w]:g[u])if(v!=p&&!dead[v]&&sz[v]>all/2)return getcen(v,u,all);return u;}
    void collect(int u,int p,i64 d,vector<i64>& ds){ds.push_back(d);for(auto [v,w]:g[u])if(v!=p&&!dead[v])collect(v,u,d+w,ds);}
    void solve(int entry){getsz(entry,0);int c=getcen(entry,0,sz[entry]);dead[c]=1;
        // 在 c 处处理所有子树，再递归；把题目逻辑写在这里
        for(auto [v,w]:g[c])if(!dead[v])solve(v); }
};

// ==================== 字符串 ====================
inline vector<int> prefix_function(const string& s) {
    vector<int> pi(s.size());
    for (int i=1;i<(int)s.size();++i){int j=pi[i-1];while(j&&s[i]!=s[j])j=pi[j-1];if(s[i]==s[j])++j;pi[i]=j;}return pi;
}
inline vector<int> kmp_find(const string& text,const string& pat){
    if(pat.empty())return {}; string s=pat+'#'+text;auto pi=prefix_function(s);vector<int> ans;
    for(int i=(int)pat.size()+1;i<(int)s.size();++i)if(pi[i]==(int)pat.size())ans.push_back(i-2*(int)pat.size());return ans;
}
inline vector<int> z_function(const string& s){
    int n=s.size();vector<int> z(n);for(int i=1,l=0,r=0;i<n;++i){if(i<r)z[i]=min(r-i,z[i-l]);while(i+z[i]<n&&s[z[i]]==s[i+z[i]])++z[i];if(i+z[i]>r)l=i,r=i+z[i];}return z;
}

struct RollingHash {
    using ull=unsigned long long; ull base; vector<ull> h,pw;
    RollingHash(const string& s,ull b=911382323){base=b;h.resize(s.size()+1);pw.resize(s.size()+1);pw[0]=1;for(int i=0;i<(int)s.size();++i)h[i+1]=h[i]*base+(unsigned char)s[i]+1,pw[i+1]=pw[i]*base;}
    ull get(int l,int r)const{return h[r]-h[l]*pw[r-l];} // [l,r)
};

inline vector<int> manacher(const string& s){
    string t="^";for(char c:s)t+="#"+string(1,c);t+="#$"; int n=t.size();vector<int> p(n);int c=0,r=0;
    for(int i=1;i<n-1;++i){int mir=2*c-i;if(i<r)p[i]=min(r-i,p[mir]);while(t[i+1+p[i]]==t[i-1-p[i]])++p[i];if(i+p[i]>r)c=i,r=i+p[i];}return p;
}

struct AhoCorasick {
    static constexpr int SIG=26; struct Node{int ch[SIG],fail,out;Node():fail(0),out(0){fill(ch,ch+SIG,0);}};vector<Node> t{Node()};
    int insert(const string&s){int u=0;for(char c:s){int x=c-'a';if(!t[u].ch[x])t[u].ch[x]=t.size(),t.emplace_back();u=t[u].ch[x];}return ++t[u].out;}
    void build(){queue<int>q;for(int c=0;c<SIG;++c)if(t[0].ch[c])q.push(t[0].ch[c]);for(int c=0;c<SIG;++c)if(!t[0].ch[c])t[0].ch[c]=0;
        while(!q.empty()){int u=q.front();q.pop();t[u].out+=t[t[u].fail].out;for(int c=0;c<SIG;++c){int v=t[u].ch[c];if(v)t[v].fail=t[t[u].fail].ch[c],q.push(v);else t[u].ch[c]=t[t[u].fail].ch[c];}}
    }
    long long query(const string&s){long long ans=0;int u=0;for(char c:s)u=t[u].ch[c-'a'],ans+=t[u].out;return ans;}
};

struct SuffixAutomaton {
    struct State{int next[26],link,len;long long occ;State():link(-1),len(0),occ(0){fill(next,next+26,-1);}};vector<State> st;int last=0;
    SuffixAutomaton(int n=0){st.reserve(2*n+1);st.emplace_back();}
    void extend(char cc){int c=cc-'a',cur=st.size();st.emplace_back();st[cur].len=st[last].len+1;st[cur].occ=1;int p=last;
        while(p!=-1&&st[p].next[c]==-1)st[p].next[c]=cur,p=st[p].link;
        if(p==-1)st[cur].link=0;else{int q=st[p].next[c];if(st[p].len+1==st[q].len)st[cur].link=q;else{int clone=st.size();st.push_back(st[q]);st[clone].len=st[p].len+1;st[clone].occ=0;while(p!=-1&&st[p].next[c]==q)st[p].next[c]=clone,p=st[p].link;st[q].link=st[cur].link=clone;}}
        last=cur;
    }
    void buildOcc(){int mx=0;for(auto&s:st)mx=max(mx,s.len);vector<int>cnt(mx+1);for(auto&s:st)cnt[s.len]++;for(int i=1;i<=mx;++i)cnt[i]+=cnt[i-1];vector<int>ord(st.size());for(int i=st.size()-1;i>=0;--i)ord[--cnt[st[i].len]]=i;for(int i=ord.size()-1;i>0;--i)st[st[ord[i]].link].occ+=st[ord[i]].occ;}
    long long differentSubstrings()const{long long ans=0;for(int v=1;v<(int)st.size();++v)ans+=st[v].len-st[st[v].link].len;return ans;}
};

struct SuffixArray {
    vector<int> sa,rk,lcp; // lcp[i]=LCP(sa[i],sa[i-1])
    explicit SuffixArray(const string&s){build(s);}
    void build(const string&s){int n=s.size();sa.resize(n);rk.resize(n);vector<int> y(n),tmp(n),x(n);for(int i=0;i<n;++i)sa[i]=i,x[i]=(unsigned char)s[i];
        for(int k=1;;k<<=1){int m=max(256,n)+1;vector<int>cnt(m);auto key=[&](int i){return i<n?x[i]+1:0;};for(int i=0;i<n;++i)cnt[key(i)]++;for(int i=1;i<m;++i)cnt[i]+=cnt[i-1];
            auto counting=[&](bool second){fill(cnt.begin(),cnt.end(),0);for(int i=0;i<n;++i){int id=second?sa[i]-k:sa[i];if(id>=0)cnt[key(id)]++;}for(int i=1;i<m;++i)cnt[i]+=cnt[i-1];for(int i=n-1;i>=0;--i){int id=second?sa[i]-k:sa[i];if(id>=0)y[--cnt[key(id)]]=id;}};
            vector<int> first(n);iota(first.begin(),first.end(),0);sa=first;counting(true);sa=y;counting(false);tmp[sa[0]]=0;for(int i=1;i<n;++i)tmp[sa[i]]=tmp[sa[i-1]]+(key(sa[i])!=key(sa[i-1])||key(sa[i]+k)!=key(sa[i-1]+k));x=tmp;if(x[sa[n-1]]==n-1)break;}
        rk.resize(n);for(int i=0;i<n;++i)rk[sa[i]]=i;lcp.assign(n,0);for(int i=0,h=0;i<n;++i){int r=rk[i];if(r==0)continue;int j=sa[r-1];while(i+h<n&&j+h<n&&s[i+h]==s[j+h])++h;lcp[r]=h;if(h)--h;}
    }
};

// ==================== 几何 ====================
struct Point { long double x,y; Point operator+(Point o)const{return{x+o.x,y+o.y};} Point operator-(Point o)const{return{x-o.x,y-o.y};} Point operator*(long double k)const{return{x*k,y*k};} };
inline long double cross(Point a,Point b){return a.x*b.y-a.y*b.x;}
inline long double dot(Point a,Point b){return a.x*b.x+a.y*b.y;}
inline long double norm2(Point a){return dot(a,a);}
inline int sgn(long double x){const long double EPS=1e-12L;return (x>EPS)-(x<-EPS);}
inline vector<Point> convexHull(vector<Point> p){sort(p.begin(),p.end(),[](Point a,Point b){return a.x!=b.x?a.x<b.x:a.y<b.y;});p.erase(unique(p.begin(),p.end(),[](Point a,Point b){return !sgn(a.x-b.x)&&!sgn(a.y-b.y);}),p.end());if(p.size()<=1)return p;vector<Point> h;
    for(auto q:p){while(h.size()>=2&&sgn(cross(h.back()-h[h.size()-2],q-h.back()))<=0)h.pop_back();h.push_back(q);}size_t low=h.size();for(int i=(int)p.size()-2;i>=0;--i){auto q=p[i];while(h.size()>low&&sgn(cross(h.back()-h[h.size()-2],q-h.back()))<=0)h.pop_back();h.push_back(q);}h.pop_back();return h;}

// ==================== NTT（998244353） ====================
namespace NTT998 {
    const int mod=998244353,g=3;
    int qpow(int a,int e){long long r=1;for(;e;e>>=1,a=(long long)a*a%mod)if(e&1)r=r*a%mod;return(int)r;}
    void transform(vector<int>&a,bool inv){int n=a.size();for(int i=1,j=0;i<n;++i){int b=n>>1;for(;j&b;b>>=1)j^=b;j^=b;if(i<j)swap(a[i],a[j]);}
        for(int len=2;len<=n;len<<=1){int wlen=qpow(g,(mod-1)/len);if(inv)wlen=qpow(wlen,mod-2);for(int i=0;i<n;i+=len){long long w=1;for(int j=0;j<len/2;++j){int u=a[i+j],v=(long long)a[i+j+len/2]*w%mod;a[i+j]=(u+v)%mod;a[i+j+len/2]=(u-v+mod)%mod;w=w*wlen%mod;}}}if(inv){int z=qpow(n,mod-2);for(int&x:a)x=(long long)x*z%mod;}}
    vector<int> multiply(vector<int>a,vector<int>b){int need=a.size()+b.size()-1,n=1;while(n<need)n<<=1;a.resize(n);b.resize(n);transform(a,0);transform(b,0);for(int i=0;i<n;++i)a[i]=(long long)a[i]*b[i]%mod;transform(a,1);a.resize(need);return a;}
}

// ==================== 高斯消元 ====================
// 返回秩；a 是 n 行 m+1 列增广矩阵，解写在主元列
inline int gauss(vector<vector<long double>>& a, vector<long double>& ans){int n=a.size(),m=a[0].size()-1,row=0;const long double EPS=1e-12L;vector<int>where(m,-1);
    for(int col=0;col<m&&row<n;++col){int sel=row;for(int i=row;i<n;++i)if(fabsl(a[i][col])>fabsl(a[sel][col]))sel=i;if(fabsl(a[sel][col])<EPS)continue;swap(a[sel],a[row]);where[col]=row;long double z=a[row][col];for(int j=col;j<=m;++j)a[row][j]/=z;for(int i=0;i<n;++i)if(i!=row&&fabsl(a[i][col])>EPS){z=a[i][col];for(int j=col;j<=m;++j)a[i][j]-=z*a[row][j];}++row;}
    for(int i=0;i<n;++i){bool all=1;for(int j=0;j<m;++j)if(fabsl(a[i][j])>EPS)all=0;if(all&&fabsl(a[i][m])>EPS)return -1;}ans.assign(m,0);for(int i=0;i<m;++i)if(where[i]!=-1)ans[i]=a[where[i]][m];return row;}

// ==================== 2-SAT ====================
struct TwoSAT {
    int n; vector<vector<int>> g; vector<int> dfn,low,stk,comp; vector<char> in; int timer=0,cc=0;
    TwoSAT(int n=0):n(n),g(2*n),dfn(2*n),low(2*n),comp(2*n,-1),in(2*n){}
    int id(int x,bool val){return 2*x+(int)val;} int neg(int x){return x^1;}
    void imply(int a,int b){g[a].push_back(b);} // a -> b
    void either(int x,bool xv,int y,bool yv){int a=id(x,xv),b=id(y,yv);imply(neg(a),b);imply(neg(b),a);}
    void dfs(int u){dfn[u]=low[u]=++timer;stk.push_back(u);in[u]=1;for(int v:g[u])if(!dfn[v])dfs(v),low[u]=min(low[u],low[v]);else if(in[v])low[u]=min(low[u],dfn[v]);if(low[u]==dfn[u]){while(1){int v=stk.back();stk.pop_back();in[v]=0;comp[v]=cc;if(v==u)break;}++cc;}}
    bool solve(vector<int>& val){for(int i=0;i<2*n;++i)if(!dfn[i])dfs(i);val.resize(n);for(int i=0;i<n;++i){if(comp[2*i]==comp[2*i+1])return false;val[i]=comp[2*i]<comp[2*i+1];}return true;}
};

// Hopcroft-Karp：左部 1..n，右部 1..m，返回最大匹配数
struct HopcroftKarp {
    int n,m; vector<vector<int>> g; vector<int> ml,mr,dist;
    HopcroftKarp(int n,int m):n(n),m(m),g(n+1),ml(n+1),mr(m+1),dist(n+1){}
    void addEdge(int u,int v){g[u].push_back(v);}
    bool bfs(){queue<int>q;bool ok=false;for(int u=1;u<=n;++u)if(!ml[u])dist[u]=0,q.push(u);else dist[u]=-1;while(!q.empty()){int u=q.front();q.pop();for(int v:g[u])if(mr[v]&&dist[mr[v]]<0)dist[mr[v]]=dist[u]+1,q.push(mr[v]);else if(!mr[v])ok=true;}return ok;}
    bool dfs(int u){for(int v:g[u])if(!mr[v]||(dist[mr[v]]==dist[u]+1&&dfs(mr[v]))){ml[u]=v;mr[v]=u;return true;}dist[u]=-1;return false;}
    int maxMatching(){int ans=0;while(bfs())for(int u=1;u<=n;++u)if(!ml[u]&&dfs(u))++ans;return ans;}
};

// ==================== 64 位质数判定/整数分解（可选） ====================
inline unsigned long long mod_pow_u64(unsigned long long a,unsigned long long e,unsigned long long mod){unsigned long long r=1%mod;for(;e;e>>=1,a=(i128)a*a%mod)if(e&1)r=(i128)r*a%mod;return r;}
inline bool isPrime64(unsigned long long n){
    if(n<2)return false;for(unsigned long long p:{2ULL,3ULL,5ULL,7ULL,11ULL,13ULL,17ULL,19ULL,23ULL,29ULL,31ULL,37ULL}){if(n%p==0)return n==p;}
    unsigned long long d=n-1,s=0;while(!(d&1))d>>=1,++s;for(unsigned long long a:{2ULL,325ULL,9375ULL,28178ULL,450775ULL,9780504ULL,1795265022ULL}){if(a%n==0)continue;unsigned long long x=mod_pow_u64(a%n,d,n);if(x==1||x==n-1)continue;bool ok=false;for(unsigned long long r=1;r<s;++r){x=(i128)x*x%n;if(x==n-1){ok=true;break;}}if(!ok)return false;}return true;
}
inline unsigned long long pollardRho(unsigned long long n){if(n%2==0)return 2;static mt19937_64 rng(chrono::steady_clock::now().time_since_epoch().count());while(1){unsigned long long c=rng()%(n-1)+1,x=rng()%(n-1)+1,y=x,d=1;auto f=[&](unsigned long long v){return ((i128)v*v+c)%n;};while(d==1){x=f(x);y=f(f(y));unsigned long long z=x>y?x-y:y-x;d=gcd(z,n);}if(d!=n)return d;}}
inline void factor64(unsigned long long n,vector<unsigned long long>& fac){if(n==1)return;if(isPrime64(n)){fac.push_back(n);return;}auto d=pollardRho(n);factor64(d,fac);factor64(n/d,fac);}

// 中国剩余定理（模数两两互质）；返回最小非负解，溢出时请改为 __int128 版本
inline i64 crt(const vector<i64>& a,const vector<i64>& m){i64 M=1;for(i64 x:m)M*=x; i128 ans=0;for(int i=0;i<(int)a.size();++i){i64 Mi=M/m[i],inv=inv_mod((Mi%m[i]+m[i])%m[i],m[i]);ans+=(i128)a[i]*Mi*inv;}return (i64)(ans%M);}

// SOS DP：f[mask] 聚合所有 submask/supermask。把 op 改成 +/max 等。
template<class T> void sosSubmask(vector<T>& f,int n){for(int b=0;b<n;++b)for(int mask=0;mask<(1<<n);++mask)if(mask>>b&1)f[mask]+=f[mask^(1<<b)];}
template<class T> void sosSupermask(vector<T>& f,int n){for(int b=0;b<n;++b)for(int mask=0;mask<(1<<n);++mask)if(!(mask>>b&1))f[mask]+=f[mask^(1<<b)];}
