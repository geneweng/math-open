// Direct independent checker. Uses no search routines or producer Graph class.
#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
int main(){try{
 std::string code;std::uint64_t s,t,graphs=0,edges=0,implicit=0;const int n=22;
 while(std::cin>>code){if(!(std::cin>>s))throw std::runtime_error("missing parent mask");
 if(code.size()!=1+(n*(n-1)/2+5)/6||int(code[0])-63!=n)throw std::runtime_error("encoding");
 for(char c:code)if(c<63||c>126)throw std::runtime_error("character");
 std::array<std::array<int,3>,22>nb{};std::array<int,22>deg{};
 std::array<std::pair<int,int>,33>es{};int m=0,pos=0;
 for(int v=1;v<n;v++)for(int u=0;u<v;u++,pos++)if(((code[1+pos/6]-63)>>(5-pos%6))&1){
  if(deg[u]>=3||deg[v]>=3||m>=33)throw std::runtime_error("degree overflow");
  nb[u][deg[u]++]=v;nb[v][deg[v]++]=u;es[m++]={u,v};
 }
 if(pos%6&&((code.back()-63)&((1<<(6-pos%6))-1)))throw std::runtime_error("padding");
 if(m!=33)throw std::runtime_error("edge count");for(int d:deg)if(d!=3)throw std::runtime_error("degree");
 std::array<bool,22>seen{};std::array<int,22>queue{};queue[0]=0;seen[0]=true;int tail=1;
 for(int head=0;head<tail;head++)for(int v:nb[queue[head]])if(!seen[v]){seen[v]=true;queue[tail++]=v;}
 if(tail!=22)throw std::runtime_error("connectivity");
 auto check=[&](std::uint64_t mask,int u,int v,int target){if(mask>>n)throw std::runtime_error("mask bounds");int size=0;
  for(int x=0;x<n;x++)if(mask>>x&1){size++;int degree=0;for(int y:nb[x])if(mask>>y&1){if((x==u&&y==v)||(x==v&&y==u))continue;degree++;}
   if(degree!=2)throw std::runtime_error("induced degree");}
  if(size<target)throw std::runtime_error("too small");return size;};
 int size=check(s,-1,-1,12);
 for(auto[u,v]:es)if((s>>u&1)&&(s>>v&1)){
  if(!(std::cin>>t))throw std::runtime_error("missing edge mask");check(t,u,v,n-size);edges++;
 }else implicit++;
 graphs++;
 }
 std::cout<<"GRAPHS "<<graphs<<" EXPLICIT "<<edges<<" IMPLICIT "<<implicit<<'\n';
}catch(const std::exception&e){std::cerr<<e.what()<<std::endl;return 1;}}
