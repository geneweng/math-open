// Independent certificate checker: no search code or Graph class is reused.
#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
int main(int argc,char**argv){try{
 if(argc!=2)throw std::runtime_error("usage: check_cubic_census ORDER");
 int n=std::stoi(argv[1]);if(n<4||n>42)throw std::runtime_error("order");
 std::string code;std::uint64_t mask,count=0;std::array<std::uint64_t,43>hist{};
 while(std::cin>>code){if(!(std::cin>>mask))throw std::runtime_error("missing mask");
  if(int(code[0])-63!=n||int(code.size())!=1+(n*(n-1)/2+5)/6||mask>>n)
   throw std::runtime_error("encoding");
  for(char c:code)if(c<63||c>126)throw std::runtime_error("character");
  std::array<std::array<bool,42>,42>a{};std::array<int,42>degree{};
  int pos=0;
  for(int v=1;v<n;v++)for(int u=0;u<v;u++,pos++)
   if(((code[1+pos/6]-63)>>(5-pos%6))&1){a[u][v]=a[v][u]=true;degree[u]++;degree[v]++;}
  if(pos%6 && ((code.back()-63)&((1<<(6-pos%6))-1)))throw std::runtime_error("padding");
  std::array<bool,42>seen{};std::array<int,42>queue{};seen[0]=true;int tail=1;
  for(int head=0;head<tail;head++)for(int v=0;v<n;v++)if(a[queue[head]][v]&&!seen[v]){seen[v]=true;queue[tail++]=v;}
  if(tail!=n)throw std::runtime_error("disconnected");
  int selected=0;
  for(int u=0;u<n;u++){
   if(degree[u]!=3)throw std::runtime_error("not cubic");
   if(mask>>u&1){selected++;int d=0;for(int v=0;v<n;v++)if(a[u][v]&&(mask>>v&1))d++;
    if(d!=2)throw std::runtime_error("not an induced 2-regular set");}
  }
  if(selected<n/2)throw std::runtime_error("below half");
  hist[selected]++;count++;
 }
 std::cout<<"COUNT "<<count<<'\n';for(int k=0;k<=n;k++)if(hist[k])std::cout<<"SIZE "<<k<<' '<<hist[k]<<'\n';
}catch(const std::exception&e){std::cerr<<e.what()<<std::endl;return 1;}}
