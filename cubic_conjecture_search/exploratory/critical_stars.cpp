// Search for incident edges whose deletion increases c_ind; no conjectural
// restriction on this set is assumed by the program.
#define ODD_FACTOR_LIBRARY
#include "odd_factor_enumerate.cpp"
int main(int argc,char**argv){try{
 unsigned long long graphs=0;int maxdeg=0;
 for(int file=1;file<argc;file++){std::ifstream in(argv[file]);std::string code;
 while(in>>code){Graph g(code);auto basis=g.cycle_basis();U f=0;int optimum=0;std::vector<int> chordmax(g.edges.size());
 for(U step=1;step<(U(1)<<basis.size());step++){
  f^=basis[__builtin_ctzll(step)];U s=0;for(int v=0;v<g.n;v++)if(f&g.incident[v])s|=U(1)<<v;
  U bad=0,todo=s;while(todo){int v=__builtin_ctzll(todo);todo&=todo-1;if(__builtin_popcountll(g.adjacent[v]&s)==3)bad|=U(1)<<v;}
  int sz=__builtin_popcountll(s);
  if(!bad)optimum=std::max(optimum,sz);
  else if(__builtin_popcountll(bad)==2){int u=__builtin_ctzll(bad);bad&=bad-1;int v=__builtin_ctzll(bad);U e=g.incident[u]&g.incident[v]&~f;if(e){int i=__builtin_ctzll(e);chordmax[i]=std::max(chordmax[i],sz);}}
 }
 std::vector<int> degree(g.n);for(int e=0;e<int(g.edges.size());e++)if(chordmax[e]>optimum){auto[u,v]=g.edges[e];degree[u]++;degree[v]++;}
 int d=*std::max_element(degree.begin(),degree.end());graphs++;
 if(d>maxdeg){maxdeg=d;std::cout<<"NEW "<<g.n<<' '<<d<<' '<<optimum<<' '<<code<<std::endl;}
 if(d==3){std::cout<<"FULL_STAR "<<g.n<<' '<<optimum<<' '<<code<<std::endl;return 0;}
 }}
 std::cout<<"DONE "<<graphs<<' '<<maxdeg<<std::endl;
}catch(const std::exception&e){std::cerr<<e.what()<<std::endl;return 1;}}
