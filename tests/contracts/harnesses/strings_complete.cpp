#include <bits/stdc++.h>
using namespace std;

namespace booth_case {
// @@@BOOTH@@@
}
namespace pam_case {
constexpr int MAXN = 4096;
// @@@PAM@@@
}
namespace sam_case {
constexpr int MAXN = 8192;
// @@@SAM@@@
}
namespace ac_case {
constexpr int MAXN = 8192;
// @@@AC@@@
}

int main(){
    mt19937 rng(20260829);
    for(int round=0;round<5000;++round){
        int n=1+rng()%30;string s;while((int)s.size()<n)s+=char('a'+rng()%4);
        int got=booth_case::booth(s),want=0;
        for(int i=1;i<n;++i)if(s.substr(i)+s.substr(0,i)<s.substr(want)+s.substr(0,want))want=i;
        if(s.substr(got)+s.substr(0,got)!=s.substr(want)+s.substr(0,want))return 1;
    }
    for(int round=0;round<500;++round){
        int n=1+rng()%120;string s;while((int)s.size()<n)s+=char('a'+rng()%4);
        pam_case::PAM pam{};pam.init();map<int,string> represented;
        for(int i=0;i<n;++i){int node=pam.add(s[i]);int best=0;string b;
            for(int l=1;l<=i+1;++l){string q=s.substr(i-l+1,l);string r=q;reverse(r.begin(),r.end());if(q==r&&l>best)best=l,b=q;}
            if(pam.len[node]!=best)return 2;represented[node]=b;
        }
        set<string> distinct;map<string,int> occ;
        for(int l=0;l<n;++l)for(int r=l;r<n;++r){string q=s.substr(l,r-l+1),z=q;reverse(z.begin(),z.end());if(q==z)distinct.insert(q),++occ[q];}
        if(pam.tot-1!=(int)distinct.size())return 3;
        pam.count_occurrence();for(auto [node,q]:represented)if(pam.occ[node]!=occ[q])return 4;
    }
    for(int round=0;round<1000;++round){
        int n=1+rng()%100;string s;while((int)s.size()<n)s+=char('a'+rng()%5);
        sam_case::SAM sam{};for(char c:s)sam.extend(c-'a');
        long long got=0;for(int i=2;i<=sam.tot;++i)got+=sam.len[i]-sam.len[sam.link[i]];
        set<string> subs;for(int l=0;l<n;++l)for(int r=l;r<n;++r)subs.insert(s.substr(l,r-l+1));
        if(got!=(long long)subs.size())return 5;
    }
    for(int round=0;round<300;++round){
        int k=1+rng()%30,n=1+rng()%200;vector<string> pats;ac_case::AC ac{};vector<int>end;
        for(int i=0;i<k;++i){string p;int len=1+rng()%12;while((int)p.size()<len)p+=char('a'+rng()%4);pats.push_back(p);end.push_back(ac.insert(p));}
        string text;while((int)text.size()<n)text+=char('a'+rng()%4);ac.build();ac.scan(text);ac.dfs_fail(0);
        for(int i=0;i<k;++i){int want=0;for(int pos=0;pos+(int)pats[i].size()<=n;++pos)want+=text.compare(pos,pats[i].size(),pats[i])==0;if(ac.out[end[i]]!=want)return 6;}
    }
    cout<<"string complete contracts: PASS\n";
}
