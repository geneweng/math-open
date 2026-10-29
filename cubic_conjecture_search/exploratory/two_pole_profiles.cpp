#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
using namespace std;
constexpr int NEG=-1000000;
using Sig=array<int,5>; // 00,01,10,11,22, with the first endpoint first.
struct Rec{Sig a;string code;int u,v;};
bool le(const Sig&a,const Sig&b){for(int i=0;i<5;i++)if(a[i]>b[i])return false;return true;}
int main(int argc,char**argv){
 if(argc<3)return 2;vector<Rec>pool;long long graphs=0,cases=0;
 for(int fi=2;fi<argc;fi++){
  ifstream in(argv[fi]);if(!in){cerr<<"input unavailable\n";return 2;}string code;
  while(getline(in,code)){
   if(code.empty()){cerr<<"empty graph6 record\n";return 2;}
   int n=code[0]-63,bit=0;if(n<4||n>24||code.size()!=1+(n*(n-1)/2+5)/6){cerr<<"unsupported graph6\n";return 2;}
   vector<unsigned>a(n);vector<pair<int,int>>es;vector<vector<int>>eid(n,vector<int>(n,-1));
   for(int v=1;v<n;v++)for(int u=0;u<v;u++,bit++)if((code[1+bit/6]-63)&(1<<(5-bit%6))){a[u]|=1u<<v;a[v]|=1u<<u;eid[u][v]=es.size();es.push_back({u,v});}
   for(auto x:a)if(__builtin_popcount(x)!=3){cerr<<"input is not cubic\n";return 2;}
   vector<Sig>scores(es.size());for(auto&s:scores){s.fill(NEG);s[0]=-n;}
   for(unsigned s=1;s<(1u<<n);s++){
    unsigned rem=s,defects=0;bool ok=true;
    while(rem){int v=__builtin_ctz(rem);rem&=rem-1;int d=__builtin_popcount(s&a[v]);if(d<2){ok=false;break;}if(d==3){defects|=1u<<v;if(__builtin_popcount(defects)>2){ok=false;break;}}}
    if(!ok)continue;int value=2*__builtin_popcount(s)-n;
    if(!defects){for(int i=0;i<(int)es.size();i++){auto[u,v]=es[i];int k=(s>>u&1)*2+(s>>v&1);if(k==3)k=4;scores[i][k]=max(scores[i][k],value);}}
    else if(__builtin_popcount(defects)==2){int u=__builtin_ctz(defects),v=__builtin_ctz(defects&(defects-1));if(eid[u][v]>=0)scores[eid[u][v]][3]=max(scores[eid[u][v]][3],value);}
   }
   for(int i=0;i<(int)es.size();i++){
    cases++;auto s=scores[i];auto[u,v]=es[i];if(s[1]>s[2]){swap(s[1],s[2]);swap(u,v);}
    bool dominated=false;for(auto&r:pool){Sig flip=r.a;swap(flip[1],flip[2]);if(le(r.a,s)||le(flip,s)){dominated=true;break;}}
    if(dominated)continue;Sig flip=s;swap(flip[1],flip[2]);pool.erase(remove_if(pool.begin(),pool.end(),[&](auto&r){return le(s,r.a)||le(flip,r.a);}),pool.end());pool.push_back({s,code,u,v});
   }
   graphs++;if(graphs%5000==0)cerr<<"graphs "<<graphs<<" profiles "<<pool.size()<<endl;
  }
 }
 ofstream out(argv[1]);for(auto&r:pool){out<<r.code<<" "<<r.u<<" "<<r.v;for(int x:r.a)out<<" "<<x;out<<"\n";}
 cout<<"DONE graphs="<<graphs<<" edge_cases="<<cases<<" profiles="<<pool.size()<<endl;
}
