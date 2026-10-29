// Exact four-port profiles after deleting adjacent vertices with no common
// neighbour. Every feasible partial cycle system closes through the deleted
// edge and its ends, so the original graph's cycle space is exhaustive.
#define TRIANGLE_PAIR_LIBRARY
#include "triangle_pair_search.cpp"
int main(int argc,char**argv){try{
 if(argc!=3)throw std::runtime_error("usage: four_pole_large INPUT OUTPUT");
 std::ifstream in(argv[1]);std::ofstream out(argv[2]);std::string code;
 while(in>>code){Graph base(code);Subgraph g(base.n,base.edges);auto basis=g.basis();
 struct Pole{int u,v;U removed,pm;std::vector<int> ports,val;std::vector<U>wit;};
 std::vector<Pole> poles;
 for(auto [u,v]:g.es){if(g.adj[u]&g.adj[v])continue;
  U removed=(U(1)<<u)|(U(1)<<v), pm=(g.adj[u]|g.adj[v])&~removed;
  Pole p{u,v,removed,pm,{},std::vector<int>(81,-1000000),std::vector<U>(81)};
  for(int w=0;w<g.n;w++)if(pm>>w&1)p.ports.push_back(w);
  if(p.ports.size()!=4)throw std::runtime_error("four distinct ports required");
  poles.push_back(p);
 }
 U f=0;for(U step=0;step<(U(1)<<basis.size());step++){
  if(step)f^=basis[__builtin_ctzll(step)];U support=0;
  for(int v=0;v<g.n;v++)if(f&g.inc[v])support|=U(1)<<v;
  for(auto &p:poles){U s=support&~p.removed,todo=s;bool valid=true;
   while(todo){int v=__builtin_ctzll(todo);todo&=todo-1;
    int d=__builtin_popcountll(g.adj[v]&s);
    if((!(p.pm>>v&1)&&d!=2)||((p.pm>>v&1)&&d!=1&&d!=2)){valid=false;break;}}
   if(!valid)continue;int state=0,mul=1;
   for(int v:p.ports){int d=__builtin_popcountll(g.adj[v]&s);
    state+=mul*((s>>v&1)?3-d:0);mul*=3;}
   int score=2*__builtin_popcountll(s)-(g.n-2);
   if(score>p.val[state]){p.val[state]=score;p.wit[state]=s;}
  }
 }
 for(auto&p:poles){out<<code<<' '<<p.u<<' '<<p.v;
  for(int v:p.ports)out<<' '<<v;
  for(int s=0;s<81;s++)out<<' '<<p.val[s]<<' '<<p.wit[s];out<<'\n';}
 out.flush();std::cerr<<"DONE "<<g.n<<" poles "<<poles.size()<<std::endl;
 }
}catch(const std::exception&e){std::cerr<<e.what()<<std::endl;return 1;}}
