#define main edge_ball_unused_main
#include "edge_ball_enumerate.cpp"
#undef main
int main(){try{std::string code;unsigned long long graphs=0,tests=0;while(std::cin>>code){Graph g(code);std::cout<<code;
 for(auto[u,v]:g.edges)for(int type=0;type<2;type++){
  int q=g.n+(type?3:1),r=q-1;auto a=g.adjacent;a.resize(q);a[u]^=U(1)<<v;a[v]^=U(1)<<u;
  std::vector<std::pair<int,int>> add;
  if(type)add={{u,g.n},{g.n,g.n+1},{g.n+1,v},{g.n,r},{g.n+1,r}};
  else add={{u,r},{v,r}};
  for(auto[x,y]:add){a[x]|=U(1)<<y;a[y]|=U(1)<<x;}
  Search s{q,(q+1)/2,(U(1)<<q)-1,a};U b=0,in=0;
  if(s.visit(0,U(1)<<r))b=s.result;
  else{
   for(s.threshold=(q-1)/2;s.threshold>=0;--s.threshold)if(s.visit(0,U(1)<<r)){b=s.result;break;}
   s.threshold=q-__builtin_popcountll(b);
   if(!s.visit(U(1)<<r,0)){std::cerr<<"COUNTEREXAMPLE_CANDIDATE "<<code<<' '<<u<<' '<<v<<' '<<type<<std::endl;return 2;}
   in=s.result;
  }
  std::cout<<' '<<b<<' '<<in;tests++;
 }
 std::cout<<'\n';graphs++;if(graphs%10000==0)std::cerr<<"PROGRESS "<<graphs<<' '<<tests<<std::endl;
 }std::cerr<<"COMPLETE "<<graphs<<' '<<tests<<std::endl;
}catch(const std::exception&e){std::cerr<<e.what()<<std::endl;return 1;}}
