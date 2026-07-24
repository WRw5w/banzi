#include <bits/stdc++.h>
#include <cassert>
using namespace std;

// 图论回归测试：每个测试都以“题面调用”封装接口，避免只检查数组是否初始化。

// 接口：无权图从 s 出发的最短边数；不可达点返回 -1。
vector<int> bfs(const vector<vector<int>> &g, int s) {
    vector<int> d(g.size(), -1);
    queue<int> q;
    d[s] = 0;
    q.push(s);
    while (!q.empty()) {
        int u = q.front();
        q.pop();
        for (int v : g[u]) if (d[v] == -1)
            d[v] = d[u] + 1, q.push(v);
    }
    return d;
}

// 接口：无权图中每个点到最近源点的最短边数；不可达点返回 -1。
// sources 可包含重复源点；空集合会使所有点保持 -1。
vector<int> multi_source_bfs(
    const vector<vector<int>> &g, const vector<int> &sources) {
    vector<int> d(g.size(), -1);
    queue<int> q;
    for (int s : sources) {
        if (d[s] != -1) continue;
        d[s] = 0;
        q.push(s);
    }
    while (!q.empty()) {
        int u = q.front();
        q.pop();
        for (int v : g[u]) if (d[v] == -1)
            d[v] = d[u] + 1, q.push(v);
    }
    return d;
}

// 接口：非负权图单源最短路；不可达点用 INF 表示。
vector<long long> dijkstra(
    const vector<vector<pair<int, long long>>> &g, int s) {
    const long long INF = (1LL << 60);
    vector<long long> d(g.size(), INF);
    priority_queue<pair<long long, int>,
                   vector<pair<long long, int>>,
                   greater<pair<long long, int>>> pq;
    d[s] = 0;
    pq.push({0, s});
    while (!pq.empty()) {
        auto [du, u] = pq.top();
        pq.pop();
        if (du != d[u]) continue;
        for (auto [v, w] : g[u]) if (d[v] > du + w)
            d[v] = du + w, pq.push({d[v], v});
    }
    return d;
}

// 接口：边权只能是 0/1；不可达点为大常量 INF。
vector<int> zero_one_bfs(const vector<vector<pair<int, int>>> &g, int s) {
    const int INF = 1e9;
    vector<int> d(g.size(), INF);
    deque<int> q;
    d[s] = 0;
    q.push_front(s);
    while (!q.empty()) {
        int u = q.front();
        q.pop_front();
        for (auto [v, w] : g[u]) if (d[v] > d[u] + w) {
            d[v] = d[u] + w;
            if (w == 0) q.push_front(v);
            else q.push_back(v);
        }
    }
    return d;
}

// 接口：返回任意拓扑序；有环返回 nullopt。
optional<vector<int>> topo_sort(const vector<vector<int>> &g) {
    vector<int> indeg(g.size());
    for (auto &e : g) for (int v : e) ++indeg[v];
    queue<int> q;
    for (int i = 0; i < (int)g.size(); ++i) if (!indeg[i]) q.push(i);
    vector<int> order;
    while (!q.empty()) {
        int u = q.front();
        q.pop();
        order.push_back(u);
        for (int v : g[u]) if (!--indeg[v]) q.push(v);
    }
    if ((int)order.size() != (int)g.size()) return nullopt;
    return order;
}

// 接口：无向图二分染色；孤立点允许存在，奇环返回 false。
bool is_bipartite(const vector<vector<int>> &g) {
    vector<int> color(g.size(), -1);
    for (int s = 0; s < (int)g.size(); ++s) if (color[s] < 0) {
        queue<int> q;
        q.push(s);
        color[s] = 0;
        while (!q.empty()) {
            int u = q.front();
            q.pop();
            for (int v : g[u]) {
                if (color[v] < 0) color[v] = color[u] ^ 1, q.push(v);
                else if (color[v] == color[u]) return false;
            }
        }
    }
    return true;
}

struct SCC {
    vector<vector<int>> g;
    vector<int> dfn, low, stk, comp, in;
    int timer = 0, cc = 0;
    explicit SCC(vector<vector<int>> graph)
        : g(move(graph)), dfn(g.size()), low(g.size()),
          comp(g.size()), in(g.size()) {}
    void dfs(int u) {
        dfn[u] = low[u] = ++timer;
        stk.push_back(u);
        in[u] = 1;
        for (int v : g[u]) {
            if (!dfn[v]) dfs(v), low[u] = min(low[u], low[v]);
            else if (in[v]) low[u] = min(low[u], dfn[v]);
        }
        if (low[u] != dfn[u]) return;
        ++cc;
        while (true) {
            int v = stk.back();
            stk.pop_back();
            in[v] = 0;
            comp[v] = cc;
            if (v == u) break;
        }
    }
    // 接口：run 后 comp[u] 是分量编号；每次新图需重新构造对象。
    int run() {
        for (int i = 0; i < (int)g.size(); ++i) if (!dfn[i]) dfs(i);
        return cc;
    }
};

struct BridgeFinder {
    vector<vector<pair<int, int>>> g;
    vector<int> dfn, low, bridges;
    int timer = 0;
    explicit BridgeFinder(int n) : g(n), dfn(n), low(n) {}
    void add_edge(int u, int v, int id) {
        g[u].push_back({v, id});
        g[v].push_back({u, id});
    }
    void dfs(int u, int parent_edge) {
        dfn[u] = low[u] = ++timer;
        for (auto [v, id] : g[u]) {
            if (id == parent_edge) continue;
            if (!dfn[v]) {
                dfs(v, id);
                low[u] = min(low[u], low[v]);
                if (low[v] > dfn[u]) bridges.push_back(id);
            } else {
                low[u] = min(low[u], dfn[v]);
            }
        }
    }
    // 接口：边必须带唯一 id；run 返回桥的 id，平行边由 id 区分。
    vector<int> run() {
        for (int i = 0; i < (int)g.size(); ++i) if (!dfn[i]) dfs(i, -1);
        return bridges;
    }
};

struct Kuhn {
    vector<vector<int>> g;
    vector<int> match, vis;
    int stamp = 0;
    explicit Kuhn(int n) : g(n), match(n, -1), vis(n) {}
    bool augment(int u) {
        for (int v : g[u]) if (vis[v] != stamp) {
            vis[v] = stamp;
            if (match[v] == -1 || augment(match[v]))
                return match[v] = u, true;
        }
        return false;
    }
    // 接口：g[u] 是左点 u 可连的右点；run 返回最大匹配数。
    int run() {
        int ans = 0;
        for (int u = 0; u < (int)g.size(); ++u)
            ++stamp, ans += augment(u);
        return ans;
    }
};

struct Dinic {
    struct Edge { int to, rev, cap; };
    vector<vector<Edge>> g;
    vector<int> level, it;
    explicit Dinic(int n) : g(n), level(n), it(n) {}
    void add_edge(int u, int v, int cap) {
        Edge a{v, (int)g[v].size(), cap};
        Edge b{u, (int)g[u].size(), 0};
        g[u].push_back(a);
        g[v].push_back(b);
    }
    bool bfs(int s, int t) {
        fill(level.begin(), level.end(), -1);
        queue<int> q;
        level[s] = 0;
        q.push(s);
        while (!q.empty()) {
            int u = q.front();
            q.pop();
            for (auto &e : g[u]) if (e.cap && level[e.to] < 0)
                level[e.to] = level[u] + 1, q.push(e.to);
        }
        return level[t] >= 0;
    }
    int dfs(int u, int t, int f) {
        if (u == t) return f;
        for (int &i = it[u]; i < (int)g[u].size(); ++i) {
            Edge &e = g[u][i];
            if (!e.cap || level[e.to] != level[u] + 1) continue;
            int got = dfs(e.to, t, min(f, e.cap));
            if (got) {
                e.cap -= got;
                g[e.to][e.rev].cap += got;
                return got;
            }
        }
        return 0;
    }
    // 接口：add_edge 加有向容量边；max_flow 返回 s-t 最大流。
    int max_flow(int s, int t) {
        int ans = 0;
        while (bfs(s, t)) {
            fill(it.begin(), it.end(), 0);
            while (int f = dfs(s, t, INT_MAX)) ans += f;
        }
        return ans;
    }
};

struct LCA {
    int n, LOG;
    vector<vector<int>> g, up;
    vector<int> dep;
    explicit LCA(int n_) : n(n_), g(n), dep(n) {
        LOG = 1;
        while ((1 << LOG) <= n) ++LOG;
        up.assign(LOG, vector<int>(n));
    }
    void add_edge(int u, int v) { g[u].push_back(v), g[v].push_back(u); }
    void dfs(int u, int p) {
        up[0][u] = p;
        for (int j = 1; j < LOG; ++j)
            up[j][u] = up[j - 1][up[j - 1][u]];
        for (int v : g[u]) if (v != p)
            dep[v] = dep[u] + 1, dfs(v, u);
    }
    // 接口：先 dfs(root,root)，再查询任意两点 LCA；树必须连通。
    int lca(int u, int v) const {
        if (dep[u] < dep[v]) swap(u, v);
        int d = dep[u] - dep[v];
        for (int j = 0; j < LOG; ++j) if (d >> j & 1) u = up[j][u];
        if (u == v) return u;
        for (int j = LOG - 1; j >= 0; --j)
            if (up[j][u] != up[j][v]) u = up[j][u], v = up[j][v];
        return up[0][u];
    }
};

int main() {
    vector<vector<int>> g(4);
    g[0] = {1, 2};
    g[1] = {3};
    assert((bfs(g, 0) == vector<int>{0, 1, 1, 2}));

    vector<vector<int>> mg(6);
    for (int u = 0; u < 4; ++u)
        mg[u].push_back(u + 1), mg[u + 1].push_back(u);
    assert((multi_source_bfs(mg, {0, 4, 4})
            == vector<int>{0, 1, 2, 1, 0, -1}));

    vector<vector<pair<int, long long>>> wg(4);
    wg[0] = {{1, 5}, {2, 1}};
    wg[2] = {{1, 1}, {3, 4}};
    wg[1] = {{3, 1}};
    assert(dijkstra(wg, 0)[3] == 3);
    assert(dijkstra(wg, 0)[0] == 0);
    vector<vector<pair<int, int>>> zg(3);
    zg[0] = {{1, 1}, {2, 0}};
    zg[2] = {{1, 0}};
    assert(zero_one_bfs(zg, 0)[1] == 0);

    vector<vector<int>> dag(3);
    dag[0] = {1};
    dag[1] = {2};
    assert(topo_sort(dag).has_value());
    dag[2] = {0};
    assert(!topo_sort(dag).has_value());
    assert(is_bipartite({{1}, {0, 2}, {1}}));
    assert(!is_bipartite({{1, 2}, {0, 2}, {0, 1}}));

    SCC scc({{1}, {2}, {0, 3}, {}});
    assert(scc.run() == 2);

    BridgeFinder bf(3);
    bf.add_edge(0, 1, 0);
    bf.add_edge(0, 1, 1); // 平行边不能互相误判为桥。
    bf.add_edge(1, 2, 2);
    auto bridges = bf.run();
    assert(bridges.size() == 1 && bridges[0] == 2);

    Kuhn kuhn(3);
    kuhn.g[0] = {0, 1};
    kuhn.g[1] = {1};
    kuhn.g[2] = {2};
    assert(kuhn.run() == 3);

    Dinic flow(4);
    flow.add_edge(0, 1, 3);
    flow.add_edge(0, 2, 2);
    flow.add_edge(1, 3, 3);
    flow.add_edge(2, 3, 2);
    assert(flow.max_flow(0, 3) == 5);

    LCA lca(5);
    lca.add_edge(0, 1);
    lca.add_edge(0, 2);
    lca.add_edge(2, 3);
    lca.add_edge(2, 4);
    lca.dfs(0, 0);
    assert(lca.lca(1, 3) == 0 && lca.lca(3, 4) == 2);
    cout << "graph templates: PASS\n";
}
