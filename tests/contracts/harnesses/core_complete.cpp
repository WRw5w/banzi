#include <bits/stdc++.h>
using namespace std;
#define main generator_program_main
// @@@GENERATOR@@@
#undef main
#define main interactor_program_main
// @@@INTERACTOR@@@
#undef main
namespace int128_case {
// @@@INT128@@@
}
namespace perm_case {
// @@@PERMUTATIONS@@@
}
namespace cantor_case {
// @@@CANTOR@@@
}
namespace xor_case {
// @@@XOR_RANGE@@@
}
namespace basis_case {
// @@@LINEAR_BASIS@@@
}
namespace digit_case {
constexpr int mod=11;
// @@@DIGIT_DP@@@
}
namespace nim_case {
// @@@NIM_BASH@@@
}
namespace sg_case {
vector<vector<int>> dag;
// @@@SG_DAG@@@
}
namespace subtraction_case {
int mex(vector<int> a){sort(a.begin(),a.end());a.erase(unique(a.begin(),a.end()),a.end());int g=0;for(int x:a)if(x==g)++g;else if(x>g)break;return g;}
// @@@SUBTRACTION@@@
}
namespace nim_move_case {
// @@@NIM_MOVE@@@
}
namespace misere_case {
// @@@MISERE@@@
}
namespace subtraction_table_case {
// @@@SUBTRACTION_TABLE@@@
}
namespace matrix_segment_case {
constexpr long long MOD=1000000007;
// @@@MATRIX_SEGMENT@@@
}
namespace winlose_case {
// @@@WINLOSE@@@
}
namespace sg_detail_case {
// @@@SG_DETAIL@@@
}
namespace median_case {
// @@@RUNNING_MEDIAN@@@
}
namespace dag_game_case {
vector<vector<int>> dag;
// @@@DAG_GAME@@@
}
namespace bash_detail_case {
// @@@BASH_DETAIL@@@
}
namespace staircase_case {
// @@@STAIRCASE@@@
}

int main(){mt19937_64 rng(20260829);
    for(int it=0;it<100000;++it){int a=rng()%1000000000,b=rng()%1000000000,m=1+rng()%1000000000;if(int128_case::mul_mod(a,b,m)!=(long long)a*b%m)return 16;}
    ::rng.seed(12345);for(int n=1;n<=100;++n){auto t=rand_tree(n);if((int)t.size()!=n-1)return 17;vector<int>p(n+1);iota(p.begin(),p.end(),0);function<int(int)>f=[&](int x){return p[x]==x?x:p[x]=f(p[x]);};for(auto[u,v]:t){u=f(u);v=f(v);if(u==v)return 18;p[u]=v;}auto q=rand_perm(n);sort(q.begin(),q.end());for(int i=0;i<n;++i)if(q[i]!=i+1)return 19;}auto gd=rand_distinct(100,-1000,1000);sort(gd.begin(),gd.end());if(unique(gd.begin(),gd.end())!=gd.end())return 20;
    {
        using namespace perm_case;ostringstream out;auto* old=cout.rdbuf(out.rdbuf());used.assign(5,false);dfs(4);cout.rdbuf(old);set<string> lines;istringstream in(out.str());string line;while(getline(in,line))lines.insert(line);if(lines.size()!=24)return 1;
        out.str("");out.clear();old=cout.rdbuf(out.rdbuf());nums={1,1,2,2};used2.assign(4,false);dfs2(4);cout.rdbuf(old);lines.clear();in.clear();in.str(out.str());while(getline(in,line))lines.insert(line);if(lines.size()!=6)return 2;
    }
    for(int n=1;n<=10;++n){long long fact=1;for(int i=2;i<=n;++i)fact*=i;for(int it=0;it<min(10000LL,fact);++it){int rank=rng()%fact;auto p=cantor_case::inv_cantor(rank,n);if(cantor_case::cantor(p)!=rank)return 3;}}
    int acc=0;for(int i=0;i<=100000;++i){acc^=i;if(xor_case::xor_n(i)!=acc)return 4;}for(int it=0;it<100000;++it){int l=rng()%10000,r=l+rng()%1000,w=0;for(int x=l;x<=r;++x)w^=x;if(xor_case::xor_range(l,r)!=w)return 5;}
    for(int round=0;round<1000;++round){int n=1+rng()%18;vector<long long>a(n);basis_case::LinearBasis b;for(auto&x:a)x=rng()&((1<<20)-1),b.insert(x);long long want=0;for(int mask=0;mask<(1<<n);++mask){long long x=0;for(int i=0;i<n;++i)if(mask>>i&1)x^=a[i];want=max(want,x);}if(b.maximum()!=want)return 6;}
    for(int bound=0;bound<=100000;bound+=137){digit_case::digits=to_string(bound);memset(digit_case::memo,-1,sizeof(digit_case::memo));long long got=digit_case::solve_digit(0,1,0,0),want=0;for(int x=1;x<=bound;++x)want+=x%11==0;if(got!=want)return 7;}
    for(int n=0;n<=50;++n)for(int k=1;k<=10;++k)if(nim_case::bash_first_win(n,k)!=(n%(k+1)!=0))return 8;
    for(int round=0;round<1000;++round){vector<int>a(1+rng()%20);int x=0;for(int&v:a)v=rng()%100,x^=v;if(nim_case::nim_first_win(a)!=(x!=0))return 9;}
    for(int round=0;round<500;++round){int n=1+rng()%50;sg_case::dag.assign(n,{});for(int u=0;u<n;++u)for(int v=u+1;v<n;++v)if(rng()%5==0)sg_case::dag[u].push_back(v);sg_case::sg.assign(n,0);sg_case::sg_vis.assign(n,0);vector<int>w(n);for(int u=n-1;u>=0;--u){set<int>s;for(int v:sg_case::dag[u])s.insert(w[v]);while(s.count(w[u]))++w[u];if(sg_case::grundy(u)!=w[u])return 10;}}
    for(int round=0;round<1000;++round){vector<int>moves;for(int x=1;x<=10;++x)if(rng()%2)moves.push_back(x);if(moves.empty())moves.push_back(1);auto table=subtraction_table_case::subtraction_sg(200,moves);for(int n=0;n<=200;++n)if(subtraction_case::solve_subtraction(n,moves)!=table[n])return 11;}
    for(int round=0;round<10000;++round){vector<unsigned long long>a(1+rng()%20);unsigned long long x=0;for(auto&v:a)v=rng()%100,x^=v;auto [i,to]=nim_move_case::nim_move(a);if(!x){if(i!=-1)return 12;}else{if(i<0||to>=a[i])return 13;a[i]=to;unsigned long long y=0;for(auto v:a)y^=v;if(y)return 14;}}
    for(int n=0;n<=10;++n){vector<int>a(n,1);bool want=n%2==0;if(misere_case::misere_nim_win(a)!=want)return 15;}
    for(int round=0;round<1000;++round){matrix_segment_case::Mat a{},b{};for(auto&r:a.a)for(auto&x:r)x=rng()%100;for(auto&r:b.a)for(auto&x:r)x=rng()%100;auto got=matrix_segment_case::merge_segment(a,b),want=matrix_segment_case::mul(b,a);if(memcmp(&got,&want,sizeof(got)))return 21;auto id=matrix_segment_case::identity(),left=matrix_segment_case::mul(a,id),right=matrix_segment_case::mul(id,a);if(memcmp(&left,&a,sizeof(a))||memcmp(&right,&a,sizeof(a)))return 22;}
    for(int round=0;round<500;++round){int n=1+rng()%80;winlose_case::g.assign(n,{});for(int u=0;u<n;++u)for(int v=u+1;v<n;++v)if(rng()%5==0)winlose_case::g[u].push_back(v);winlose_case::win.assign(n,0);vector<int>w(n,-1);for(int u=n-1;u>=0;--u)for(int v:winlose_case::g[u])if(w[v]==-1){w[u]=1;break;}for(int u=0;u<n;++u)if(winlose_case::solve_win(u)!=w[u])return 23;}
    for(int round=0;round<500;++round){int n=1+rng()%80;sg_detail_case::dag.assign(n,{});for(int u=0;u<n;++u)for(int v=u+1;v<n;++v)if(rng()%5==0)sg_detail_case::dag[u].push_back(v);sg_detail_case::sg.assign(n,0);sg_detail_case::vis.assign(n,0);sg_detail_case::mark.assign(n+2,0);sg_detail_case::mark_tag=0;vector<int>w(n);for(int u=n-1;u>=0;--u){set<int>s;for(int v:sg_detail_case::dag[u])s.insert(w[v]);while(s.count(w[u]))++w[u];if(sg_detail_case::grundy(u)!=w[u])return 24;}}
    {vector<int>a;for(int i=0;i<10000;++i){int x=(int)(rng()%20001)-10000;a.push_back(x);median_case::add_number(x);auto b=a;nth_element(b.begin(),b.begin()+(b.size()-1)/2,b.end());if(median_case::median()!=b[(b.size()-1)/2])return 25;}}
    for(int round=0;round<500;++round){int n=1+rng()%80;dag_game_case::dag.assign(n,{});for(int u=0;u<n;++u)for(int v=u+1;v<n;++v)if(rng()%5==0)dag_game_case::dag[u].push_back(v);dag_game_case::win.assign(n,0);vector<int>w(n,-1);for(int u=n-1;u>=0;--u)for(int v:dag_game_case::dag[u])if(w[v]==-1){w[u]=1;break;}for(int u=0;u<n;++u)if(dag_game_case::dag_game(u)!=w[u])return 26;}
    for(long long n=0;n<1000;++n)for(long long k=1;k<50;++k)if(bash_detail_case::bash_win(n,k)!=(n%(k+1)!=0))return 27;
    for(int round=0;round<10000;++round){vector<long long>a(1+rng()%20);long long x=0;for(int i=1;i<(int)a.size();i+=2)a[i]=rng()%100,x^=a[i];if(staircase_case::staircase_nim_win(a)!=(x!=0))return 28;}
    cout<<"core complete contracts: PASS\n";
}
