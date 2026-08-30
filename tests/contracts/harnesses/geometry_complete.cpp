#include <bits/stdc++.h>
using namespace std;
namespace geo {
constexpr int MAXN=4096;
// @@@GEOMETRY_CORE@@@
// @@@GEOMETRY_VECTORS@@@
// @@@SEGMENT_INTERSECTION@@@
// @@@POLYGON_AREA@@@
// @@@POLAR_SORT@@@
// @@@CIRCLES@@@
// @@@CONVEX_HULL@@@
// @@@CLIP@@@
// @@@HPI@@@
namespace hpi_helpers {
// @@@HPI_HELPERS@@@
}
bool inside(Circle c,Point p){return c.r>=0&&dist2(c.o,p)<=c.r*c.r+1e-10L;}
Circle circle_diameter(Point a,Point b){Point o=(a+b)*0.5L;return{o,sqrtl(dist2(o,a))};}
Circle circle_three_points(Point a,Point b,Point c){
    Real d=2*cross(b-a,c-a);if(fabsl(d)<EPS)return{{0,0},-1};
    Real aa=dot(a,a),bb=dot(b,b),cc=dot(c,c);
    Point o{(aa*(b.y-c.y)+bb*(c.y-a.y)+cc*(a.y-b.y))/d,
            (aa*(c.x-b.x)+bb*(a.x-c.x)+cc*(b.x-a.x))/d};
    return{o,sqrtl(dist2(o,a))};
}
// @@@MIN_CIRCLE@@@
// @@@UNION_AREA@@@
}
int main(){using namespace geo;mt19937 rng(20260829);
    if(sgn(cross({1,0},{0,1})-1)!=0||sgn(dot({1,2},{3,4})-11)!=0)return 1;
    if(!left_of({0,0},{1,0},{0,1})||!intersect({0,0},{2,0},{1,-1},{1,1})||intersect({0,0},{1,0},{2,0},{3,0}))return 12;
    if(fabsl(area2({{0,0},{3,0},{3,2},{0,2}})-12)>1e-9)return 13;
    vector<Point> dirs{{0,-1},{-1,0},{0,1},{1,0}};sort(dirs.begin(),dirs.end(),polar_cmp);vector<Point>wantdirs{{1,0},{0,1},{-1,0},{0,-1}};for(int i=0;i<4;++i)if(dirs[i].x!=wantdirs[i].x||dirs[i].y!=wantdirs[i].y)return 14;
    auto lc=line_circle({-2,0},{2,0},{{0,0},1});if(lc.size()!=2||fabsl(lc[0].x+1)>1e-9||fabsl(lc[1].x-1)>1e-9)return 2;
    auto cc=circle_circle({{0,0},1},{{1,0},1});if(cc.size()!=2) return 3;for(auto p:cc)if(fabsl(dist2(p,{0,0})-1)>1e-9||fabsl(dist2(p,{1,0})-1)>1e-9)return 4;
    for(int round=0;round<1000;++round){vector<Point>p;int n=1+rng()%100;for(int i=0;i<n;++i)p.push_back({(int)(rng()%41)-20,(int)(rng()%41)-20});auto h=convex_hull(p);for(auto q:p){for(int i=0;i<(int)h.size();++i)if(h.size()>2&&cross(h[(i+1)%h.size()]-h[i],q-h[i])<-EPS)return 5;}if(h.size()>2)for(int i=0;i<(int)h.size();++i)if(cross(h[(i+1)%h.size()]-h[i],h[(i+2)%h.size()]-h[(i+1)%h.size()])<=0)return 6;}
    vector<Point>sq{{0,0},{4,0},{4,4},{0,4}};auto clipped=clip(sq,{2,-1},{2,5});Real area=0;for(int i=0;i<(int)clipped.size();++i)area+=cross(clipped[i],clipped[(i+1)%clipped.size()]);if(fabsl(area/2-8)>1e-9)return 7;
    vector<HalfPlane>hs{{{0,0},{1,0},0},{{4,0},{0,1},0},{{4,4},{-1,0},0},{{0,4},{0,-1},0}};auto hp=half_plane_intersection(hs);area=0;for(int i=0;i<(int)hp.size();++i)area+=cross(hp[i],hp[(i+1)%hp.size()]);if(hp.size()!=4||fabsl(area/2-16)>1e-9)return 8;
    {hpi_helpers::HalfPlane a{{0,0},{1,0}},b{{2,-1},{0,1}};if(!hpi_helpers::outside(a,{0,-1})||hpi_helpers::outside(a,{0,1}))return 15;auto p=hpi_helpers::intersection(a,b);if(fabsl(p.x-2)>1e-9||fabsl(p.y)>1e-9)return 16;}
    for(int round=0;round<500;++round){vector<Point>p;int n=1+rng()%30;for(int i=0;i<n;++i)p.push_back({(int)(rng()%101)-50,(int)(rng()%101)-50});Circle got=min_circle(p);for(auto q:p)if(!inside(got,q))return 9;Real best=1e100;vector<Circle>cand;for(auto a:p)cand.push_back({a,0});for(int i=0;i<n;++i)for(int j=0;j<i;++j)cand.push_back(circle_diameter(p[i],p[j]));for(int i=0;i<n;++i)for(int j=0;j<i;++j)for(int k=0;k<j;++k){auto c=circle_three_points(p[i],p[j],p[k]);if(c.r>=0)cand.push_back(c);}for(auto c:cand){bool ok=1;for(auto q:p)ok&=inside(c,q);if(ok)best=min(best,c.r);}if(fabsl(got.r-best)>1e-7)return 10;}
    for(int round=0;round<1000;++round){vector<Event>e;xs.clear();memset(seg,0,sizeof(seg));bool grid[20][20]{};int k=1+rng()%20;for(int z=0;z<k;++z){int x1=rng()%19,x2=x1+1+rng()%(20-x1-1),y1=rng()%19,y2=y1+1+rng()%(20-y1-1);e.push_back({y1,x1,x2,1});e.push_back({y2,x1,x2,-1});xs.push_back(x1);xs.push_back(x2);for(int x=x1;x<x2;++x)for(int y=y1;y<y2;++y)grid[x][y]=1;}sort(xs.begin(),xs.end());xs.erase(unique(xs.begin(),xs.end()),xs.end());long long want=0;for(auto&r:grid)for(bool x:r)want+=x;if(union_area(e)!=want)return 11;}
    xs.clear();memset(seg,0,sizeof(seg));if(union_area({})!=optional<long long>(0))return 17;
    xs={0,LLONG_MAX};memset(seg,0,sizeof(seg));if(union_area({{0,0,LLONG_MAX,1},{1,0,LLONG_MAX,-1}})!=optional<long long>(LLONG_MAX))return 18;
    xs={LLONG_MIN,LLONG_MAX};memset(seg,0,sizeof(seg));if(union_area({{0,LLONG_MIN,LLONG_MAX,1},{1,LLONG_MIN,LLONG_MAX,-1}}))return 19;
    xs={0,LLONG_MAX};memset(seg,0,sizeof(seg));if(union_area({{0,0,LLONG_MAX,1},{2,0,LLONG_MAX,-1}}))return 20;
    cout<<"geometry complete contracts: PASS\n";
}
