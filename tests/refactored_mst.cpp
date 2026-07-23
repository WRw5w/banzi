#include <bits/stdc++.h>
#include <cassert>
using namespace std;

struct MstEdge {
    int u, v;
    long long w;
    bool operator<(const MstEdge &o) const { return w < o.w; }
};

struct KruskalDSU {
    vector<int> p, sz;
    explicit KruskalDSU(int n) : p(n + 1), sz(n + 1, 1) {
        iota(p.begin(), p.end(), 0);
    }
    int find(int x) { return p[x] == x ? x : p[x] = find(p[x]); }
    bool unite(int x, int y) {
        x = find(x);
        y = find(y);
        if (x == y) return false;
        if (sz[x] < sz[y]) swap(x, y);
        p[y] = x;
        sz[x] += sz[y];
        return true;
    }
};

struct MstResult {
    long long cost;
    int used;
    bool connected;
    vector<MstEdge> chosen;
};

MstResult kruskal(int n, vector<MstEdge> edges) {
    sort(edges.begin(), edges.end());
    KruskalDSU dsu(n);
    MstResult ans{0, 0, n <= 1, {}};
    for (auto e : edges) {
        if (!dsu.unite(e.u, e.v)) continue;
        ans.cost += e.w;
        ++ans.used;
        ans.chosen.push_back(e);
        if (ans.used == n - 1) break;
    }
    ans.connected = (n <= 1 || ans.used == n - 1);
    return ans;
}

struct KruskalTree {
    struct Edge {
        int u, v;
        long long w;
    };
    int n = 0, tot = 0, LOG = 0;
    vector<int> dsu, dep, sz;
    vector<long long> val;
    vector<vector<int>> up, child;

    int find(int x) {
        return dsu[x] == x ? x : dsu[x] = find(dsu[x]);
    }

    void build(int n_, vector<Edge> edges) {
        n = n_;
        tot = n;
        int cap = 2 * n + 5;
        LOG = 1;
        while ((1LL << LOG) <= 2 * n) ++LOG;
        dsu.resize(cap);
        iota(dsu.begin(), dsu.end(), 0);
        dep.assign(cap, 0);
        sz.assign(cap, 0);
        val.assign(cap, numeric_limits<long long>::lowest());
        up.assign(LOG, vector<int>(cap));
        child.assign(cap, {});
        for (int i = 1; i <= n; ++i) sz[i] = 1;
        sort(edges.begin(), edges.end(),
             [](const Edge &a, const Edge &b) { return a.w < b.w; });
        for (auto e : edges) {
            int x = find(e.u), y = find(e.v);
            if (x == y) continue;
            ++tot;
            val[tot] = e.w;
            sz[tot] = sz[x] + sz[y];
            child[tot] = {x, y};
            up[0][x] = up[0][y] = tot;
            dsu[x] = dsu[y] = tot;
            dsu[tot] = tot;
        }
        vector<int> st;
        for (int u = 1; u <= tot; ++u) {
            if (dsu[u] != u) continue;
            dep[u] = 1;
            st.push_back(u);
        }
        while (!st.empty()) {
            int u = st.back();
            st.pop_back();
            for (int v : child[u]) {
                dep[v] = dep[u] + 1;
                st.push_back(v);
            }
        }
        for (int j = 1; j < LOG; ++j) {
            for (int u = 1; u <= tot; ++u) {
                up[j][u] = up[j - 1][up[j - 1][u]];
            }
        }
    }

    int lca(int u, int v) const {
        if (dep[u] < dep[v]) swap(u, v);
        int d = dep[u] - dep[v];
        for (int j = 0; j < LOG; ++j) {
            if (d >> j & 1) u = up[j][u];
        }
        if (u == v) return u;
        for (int j = LOG - 1; j >= 0; --j) {
            if (up[j][u] == up[j][v]) continue;
            u = up[j][u];
            v = up[j][v];
        }
        return up[0][u];
    }

    optional<long long> bottleneck(int u, int v) {
        if (find(u) != find(v)) return nullopt;
        return val[lca(u, v)];
    }

    int component_node(int u, long long lim) const {
        for (int j = LOG - 1; j >= 0; --j) {
            int a = up[j][u];
            if (a && val[a] <= lim) u = a;
        }
        return u;
    }

    int component_size(int u, long long lim) const {
        return sz[component_node(u, lim)];
    }
};

int main() {
    vector<MstEdge> edges{{1, 2, 3}, {2, 3, 4}, {1, 3, 10}};
    auto mst = kruskal(3, edges);
    assert(mst.connected && mst.cost == 7 && mst.used == 2);

    auto forest = kruskal(4, vector<MstEdge>{{1, 2, 3}});
    assert(!forest.connected && forest.cost == 3 && forest.used == 1);

    KruskalTree tree;
    vector<KruskalTree::Edge> reconstruction_edges{
        {1, 2, 3}, {2, 3, 5}, {1, 3, 9}, {4, 5, 1}
    };
    tree.build(5, reconstruction_edges);
    assert(tree.bottleneck(1, 3).value() == 5);
    assert(!tree.bottleneck(1, 4).has_value());
    assert(tree.component_size(1, 2) == 1);
    assert(tree.component_size(1, 3) == 2);
    assert(tree.component_size(1, 5) == 3);
    assert(tree.component_size(4, 1) == 2);
    return 0;
}
