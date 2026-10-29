#include <algorithm>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
using namespace std;
int main(int argc,char**argv){long long graphs=0;for(int f=1;f<argc;f++){ifstream in(argv[f]);string s;while(getline(in,s)){
 int n=s[0]-63,bit=0;vector<unsigned>a(n);for(int v=1;v<n;v++)for(int u=0;u<v;u++,bit++)if((s[1+bit/6]-63)&(1<<(5-bit%6))){a[u]|=1u<<v;a[v]|=1u<<u;}
 bool found=false;int maxgood=0;
 for(unsigned chosen=1;chosen<(1u<<n);chosen++){int size=__builtin_popcount(chosen);if(size<n/2)continue;unsigned rem=chosen;bool good=true;
 while(rem){int v=__builtin_ctz(rem);rem&=rem-1;if(__builtin_popcount(a[v]&chosen)!=2){good=false;break;}}if(!good)continue;maxgood=max(maxgood,size);
 unsigned todo=((1u<<n)-1)^chosen;bool ok=true;
 while(todo){int first=__builtin_ctz(todo);unsigned comp=0,frontier=1u<<first;int degrees=0;
 while(frontier){int v=__builtin_ctz(frontier);frontier&=frontier-1;if(comp>>v&1)continue;comp|=1u<<v;degrees+=__builtin_popcount(a[v]&todo);frontier|=a[v]&todo&~comp;}
 if(degrees>2*__builtin_popcount(comp)){ok=false;break;}todo&=~comp;}
 if(ok){found=true;break;}}
 graphs++;if(!found){cout<<"OBSTRUCTION "<<s<<" n="<<n<<" maxgood="<<maxgood<<" checked="<<graphs<<endl;return 0;}
 if(graphs%10000==0)cerr<<graphs<<endl;
 }}cout<<"DONE graphs="<<graphs<<" all have good set with pseudoforest complement"<<endl;}
