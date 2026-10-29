#include <algorithm>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
using namespace std;
int main(int argc,char**argv){long long count=0;for(int f=1;f<argc;f++){ifstream in(argv[f]);string code;while(getline(in,code)){
 int n=code[0]-63,bit=0,root=-1;vector<unsigned>a(n);for(int v=1;v<n;v++)for(int u=0;u<v;u++,bit++)if((code[1+bit/6]-63)&(1<<(5-bit%6))){a[u]|=1u<<v;a[v]|=1u<<u;}
 for(int v=0;v<n;v++)if(__builtin_popcount(a[v])==2){if(root>=0){cerr<<"more than one root"<<endl;return 2;}root=v;}
 if(root<0){cerr<<"missing root"<<endl;return 2;}int A=-1000,B=0;unsigned wa=0,wb=0;
 for(unsigned s=1;s<(1u<<n);s++){
  int size=__builtin_popcount(s);bool inside=s>>root&1;if(size<=(inside?A:B))continue;unsigned rem=s;bool ok=true;
  while(rem){int v=__builtin_ctz(rem);rem&=rem-1;if(__builtin_popcount(a[v]&s)!=2){ok=false;break;}}
  if(ok){if(inside){A=size;wa=s;}else{B=size;wb=s;}if(B>=(n-1)/2&&max(A,B)>=(n+1)/2)break;}
 }
 count++;if(B<(n-1)/2||max(A,B)<(n+1)/2){cout<<"CAP_OUTSIDE_BASELINE "<<code<<" n="<<n<<" root="<<root<<" A="<<A<<" B="<<B<<" doubled_surplus="<<2*max(A+B,2*B)-2*n<<" checked="<<count<<endl;return 0;}
 if(count%100000==0)cerr<<"checked="<<count<<endl;
 }}cout<<"DONE caps="<<count<<" all satisfy C>=ceil(n/2), B>=floor(n/2)"<<endl;}
