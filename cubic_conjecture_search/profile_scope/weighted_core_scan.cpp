// Exact cycle-space search on connected subcubic cores, all degrees 2 or 3.
// Weights are one on degree-three vertices and zero elsewhere. P13 completion
// converts these scores into exact unweighted cubic-graph scores.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using U=std::uint64_t;
constexpr int NEG=-1000000;
int main(int argc,char**argv){
 try{
  long long graphs=0,cases=0;
  for(int file=1;file<argc;file++){
   std::ifstream in(argv[file]);if(!in)throw std::runtime_error("missing input");
   std::string code;
   while(std::getline(in,code)){
    int n=code[0]-63,bit=0;
    if(n<3||n>40||code.size()!=1+(n*(n-1)/2+5)/6)throw std::runtime_error("unsupported graph6");
    std::vector<std::pair<int,int>> es;
    std::vector<U> adj(n),inc(n);
    for(int v=1;v<n;v++)for(int u=0;u<v;u++,bit++)
     if((code[1+bit/6]-63)&(1<<(5-bit%6))){
      U e=U(1)<<es.size();es.emplace_back(u,v);adj[u]|=U(1)<<v;adj[v]|=U(1)<<u;inc[u]|=e;inc[v]|=e;
     }
    if(es.size()>63)throw std::runtime_error("edge mask too large");
    U branches=0;
    for(int v=0;v<n;v++){
     int d=__builtin_popcountll(adj[v]);if(d<2||d>3)throw std::runtime_error("invalid degree");
     if(d==3)branches|=U(1)<<v;
    }
    int b=__builtin_popcountll(branches);if(b%2)throw std::runtime_error("odd branch count");
    std::vector<int> parent(n,-1),pe(n,-1),depth(n),queue{0};parent[0]=0;U tree=0;
    for(std::size_t q=0;q<queue.size();q++){
     int u=queue[q];U todo=inc[u];
     while(todo){int e=__builtin_ctzll(todo);todo&=todo-1;auto[x,y]=es[e];int v=x^y^u;
      if(parent[v]!=-1)continue;parent[v]=u;pe[v]=e;depth[v]=depth[u]+1;tree|=U(1)<<e;queue.push_back(v);
     }
    }
    if(queue.size()!=std::size_t(n))throw std::runtime_error("disconnected");
    std::vector<U> basis;
    for(int e=0;e<int(es.size());e++)if(!(tree>>e&1)){
     auto[u,v]=es[e];U cyc=U(1)<<e;
     while(u!=v){if(depth[u]<depth[v])std::swap(u,v);cyc^=U(1)<<pe[u];u=parent[u];}
     basis.push_back(cyc);
    }
    std::vector<std::array<int,5>> scores(es.size());
    std::vector<std::array<long long,5>> witnesses(es.size());
    for(auto&s:scores)s.fill(NEG);for(auto&w:witnesses)w.fill(-1);
    U chosen=0;int best=NEG;U bestmask=0;
    for(U k=0;k<(U(1)<<basis.size());k++){
     if(k)chosen^=basis[__builtin_ctzll(k)];U selected=0;
     for(int v=0;v<n;v++)if(inc[v]&chosen)selected|=U(1)<<v;
     int bad=-1,count=0;
     for(int e=0;e<int(es.size());e++){
      auto[u,v]=es[e];
      if(!(chosen>>e&1)&&(selected>>u&1)&&(selected>>v&1)){bad=e;if(++count>1)break;}
     }
     int score=__builtin_popcountll(selected&branches)-b/2;
     if(count>1)continue;
     if(count==1){if(score>scores[bad][3]){scores[bad][3]=score;witnesses[bad][3]=selected;}continue;}
     if(score>best){best=score;bestmask=selected;}
     for(int e=0;e<int(es.size());e++){
      auto[u,v]=es[e];int state=(chosen>>e&1)?4:2*(int(selected>>u&1))+int(selected>>v&1);
      if(score>scores[e][state]){scores[e][state]=score;witnesses[e][state]=selected;}
     }
    }
    bool failure=best<0;
    for(auto&s:scores){
     int u=*std::max_element(s.begin(),s.begin()+4),p=s[4],w=s[0],B=std::max(u,p+2);
     if(std::max(2*u,u+p+1)<1||std::max(2*B,w+3+B)<3)failure=true;
    }
    std::cout<<"{\"graph6\":\"";
    for(char c:code){if(c=='\\'||c=='\"')std::cout<<'\\';std::cout<<c;}
    std::cout<<"\",\"branches\":"<<b<<",\"core_witness\":"<<bestmask<<",\"states\":[";
    for(int e=0;e<int(es.size());e++){
     if(e)std::cout<<',';std::cout<<'[';
     for(int s=0;s<5;s++){if(s)std::cout<<',';std::cout<<witnesses[e][s];}std::cout<<']';
    }
    std::cout<<"],\"failure\":"<<(failure?"true":"false")<<"}\n";
    graphs++;cases+=es.size();
    if(failure){std::cerr<<"CANDIDATE requires independent verification\n";return 3;}
   }
  }
  std::cerr<<"DONE graphs="<<graphs<<" parent_edge_cases="<<cases<<"\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}
}
