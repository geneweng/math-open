// Check the edge-boundary sufficient condition for each input good set.
#define main edge_ball_unused_main
#include "edge_ball_enumerate.cpp"
#undef main
#include <chrono>
int main(){try{std::string code;U mask;unsigned long long count=0,checks=0;auto start=std::chrono::steady_clock::now();
 while(std::cin>>code>>mask){Graph g(code);int size=__builtin_popcountll(mask);Search s{g.n,g.n-size,(U(1)<<g.n)-1,g.adjacent};
 if(size<=g.n/2||mask>>g.n||!s.good(mask))throw std::runtime_error("invalid parent witness");
 std::vector<U> certificates;
 for(auto[u,v]:g.edges)if((mask>>u&1)&&(mask>>v&1)){
  s.adj[u]^=U(1)<<v;s.adj[v]^=U(1)<<u;
  if(!s.visit(0,0)){std::cerr<<"BOUNDARY_FAILURE "<<code<<' '<<mask<<' '<<u<<' '<<v<<std::endl;return 2;}
  if(!s.good(s.result)||__builtin_popcountll(s.result)<s.threshold)throw std::runtime_error("bad edge witness");
  certificates.push_back(s.result);checks++;s.adj[u]^=U(1)<<v;s.adj[v]^=U(1)<<u;
 }
 std::cout<<code<<' '<<mask;for(U w:certificates)std::cout<<' '<<w;std::cout<<'\n';count++;
 if(count%10000==0)std::cerr<<"PROGRESS "<<count<<" edges "<<checks<<std::endl;
 }
 auto sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();std::cerr<<"COMPLETE graphs "<<count<<" edges "<<checks<<" seconds "<<sec<<std::endl;
}catch(const std::exception&e){std::cerr<<e.what()<<std::endl;return 1;}}
