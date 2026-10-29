#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>
using namespace std;
struct Profile{array<int,27> a; string code; int deleted; array<int,3> ports;};
int main(int argc,char**argv){
 vector<Profile> pool;long long checked=0;
 for(int f=2;f<argc;f++){ifstream in(argv[f]);string code;while(getline(in,code)){
 int n=code[0]-63,bit=0;vector<unsigned>a(n);
 for(int v=1;v<n;v++)for(int u=0;u<v;u++,bit++)if((code[1+bit/6]-63)&(1<<(5-bit%6))){a[u]|=1u<<v;a[v]|=1u<<u;}
 for(int del=0;del<n;del++){
 array<int,3>ports;int pos=0;for(int u=0;u<n;u++)if(a[del]>>u&1)ports[pos++]=u;
 Profile p;p.a.fill(-1000);p.code=code;p.deleted=del;p.ports=ports;p.a[0]=1-n;
 for(unsigned s=1;s<(1u<<n);s++){if(s>>del&1)continue;unsigned rem=s;bool ok=true;array<int,3>state={0,0,0};
 while(rem){int v=__builtin_ctz(rem);rem&=rem-1;int d=__builtin_popcount(s&a[v]);int port=-1;for(int j=0;j<3;j++)if(v==ports[j])port=j;
 if(port<0){if(d!=2){ok=false;break;}}else{if(d<1||d>2){ok=false;break;}state[port]=3-d;}}
 if(ok){int key=state[0]+3*state[1]+9*state[2];p.a[key]=max(p.a[key],2*__builtin_popcount(s)-n+1);}}
 // Include every port orientation when testing componentwise domination.
 vector<Profile> variants;array<int,3>perm={0,1,2};do{Profile q=p;
 for(int j=0;j<3;j++)q.ports[j]=p.ports[perm[j]];
 for(int i=0;i<27;i++){array<int,3>st={i%3,i/3%3,i/9};int old=st[0]*(perm[0]==0?1:perm[0]==1?3:9)+st[1]*(perm[1]==0?1:perm[1]==1?3:9)+st[2]*(perm[2]==0?1:perm[2]==1?3:9);q.a[i]=p.a[old];}variants.push_back(q);
 }while(next_permutation(perm.begin(),perm.end()));
 bool dominated=false;for(auto&q:pool){for(auto&r:variants){bool le=true;for(int k=0;k<27;k++)if(q.a[k]>r.a[k]){le=false;break;}if(le){dominated=true;break;}}if(dominated)break;}
 if(!dominated){vector<Profile>kept;for(auto&q:pool){bool remove=false;for(auto&r:variants){bool le=true;for(int k=0;k<27;k++)if(r.a[k]>q.a[k]){le=false;break;}if(le){remove=true;break;}}if(!remove)kept.push_back(q);}p=*min_element(variants.begin(),variants.end(),[](auto&u,auto&v){return u.a<v.a;});kept.push_back(p);pool.swap(kept);}
 checked++;}
 }cerr<<"file "<<f-1<<" checked "<<checked<<" minimal "<<pool.size()<<endl;}
 ofstream out(argv[1]);for(auto&p:pool){out<<p.code<<" "<<p.deleted;for(auto v:p.ports)out<<" "<<v;for(auto v:p.a)out<<" "<<v;out<<"\n";}cout<<"DONE profiles "<<checked<<" minimal "<<pool.size()<<endl;
}
