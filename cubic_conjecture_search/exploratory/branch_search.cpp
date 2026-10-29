#include <algorithm>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
using namespace std;
int main(int argc,char**argv){
 if(argc<2){cerr<<"usage: branch_search INPUT.g6 [...]"<<endl;return 2;}
 long long graphs=0;int tight=0;
 for(int fi=1;fi<argc;fi++){
  ifstream in(argv[fi]);string code;
  if(!in){cerr<<"cannot open "<<argv[fi]<<endl;return 2;}
  while(getline(in,code)){
   if(code.empty()){cerr<<"empty graph6 record"<<endl;return 2;}
   int order=code[0]-63;
   if(order<3||order>24||code.size()!=1+(order*(order-1)/2+5)/6||
      any_of(code.begin(),code.end(),[](unsigned char c){return c<63||c>126;})){
    cerr<<"unsupported graph6 record"<<endl;return 2;
   }
   int n=code[0]-63,bit=0,m=0;vector<unsigned>a(n);unsigned branches=0;
   for(int v=1;v<n;v++)for(int u=0;u<v;u++,bit++)if((code[1+bit/6]-63)&(1<<(5-bit%6))){a[u]|=1u<<v;a[v]|=1u<<u;m++;}
   if(any_of(a.begin(),a.end(),[](unsigned mask){int d=__builtin_popcount(mask);return d<2||d>3;})){
    cerr<<"input must have minimum degree two and maximum degree three"<<endl;return 2;
   }
   for(int v=0;v<n;v++)if(__builtin_popcount(a[v])==3)branches|=1u<<v;
   int best=0;unsigned witness=0;
   for(unsigned s=1;s<(1u<<n);s++){
    int score=__builtin_popcount(s&branches);if(score<=best)continue;
    unsigned rem=s;bool ok=true;
    while(rem){int v=__builtin_ctz(rem);rem&=rem-1;if(__builtin_popcount(s&a[v])!=2){ok=false;break;}}
    if(ok){best=score;witness=s;if(best>m-n)break;}
   }
   graphs++;
   if(best<m-n){cout<<"COUNTEREXAMPLE graph6="<<code<<" n="<<n<<" m="<<m<<" beta="<<best<<" target="<<m-n<<" witness="<<witness<<" completion_order="<<n+13*(3*n-2*m)<<endl;return 0;}
   if(best==m-n)tight++;
   if(graphs%100000==0)cerr<<"graphs="<<graphs<<" tight="<<tight<<endl;
  }
 }
 cout<<"DONE graphs="<<graphs<<" tight="<<tight<<endl;
}
