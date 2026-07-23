#include <bits/stdc++.h>
using namespace std;
#define int long long
#define endl '\n'
const int inf = 2e18;
// const int inf=0x3f3f3f3f;
const int N = 1e6 + 10;

void solve()
{
    int n;
    cin>>n;
    unorder_maped<int,int> mp;
    for(int i=0;i<n;i++){
        int x;
        cin>>x;
        if(!mp[x]){
            cout<<x<<' ';
        }
        mp[x]++;
    }
    cout<<endl;
}

signed main()
{
    ios::sync_with_stdio(0);
    cin.tie(0);
    int t = 1;
    cin >> t;
    while (t--)
    {
        solve();
    }
    return 0;
}
