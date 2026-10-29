// Exact three-port tables for vertex-deleted cubic graphs, via cycle space.
#define TRIANGLE_PAIR_LIBRARY
#include "triangle_pair_search.cpp"
int main(int argc,char**argv){try{
 if(argc!=3)throw std::runtime_error("usage: three_pole_large INPUT.g6 OUTPUT.txt");
 std::ifstream in(argv[1]);std::ofstream out(argv[2]);std::string code;
 while(in>>code){Graph base(code);Subgraph g(base.n,base.edges);auto basis=g.basis();int n=g.n;
 std::vector<std::vector<int>> val(n,std::vector<int>(27,-1000000));
 std::vector<std::vector<U>> wit(n,std::vector<U>(27));std::vector<std::vector<int>> ports(n);
 for(int v=0;v<n;v++)for(int u=0;u<n;u++)if(g.adj[v]>>u&1)ports[v].push_back(u);
 U f=0;for(U step=0;step<(U(1)<<basis.size());step++){
  if(step)f^=basis[__builtin_ctzll(step)];U support=0;
  for(int v=0;v<n;v++)if(f&g.inc[v])support|=U(1)<<v;
  for(int removed=0;removed<n;removed++){
   U s=support&~(U(1)<<removed),todo=s;bool valid=true;int state=0,mul=1;
   while(todo){int v=__builtin_ctzll(todo);todo&=todo-1;int d=__builtin_popcountll(g.adj[v]&s);
    bool port=g.adj[removed]>>v&1;
    if((!port&&d!=2)||(port&&d!=1&&d!=2)){valid=false;break;}}
   if(!valid)continue;
   for(int p:ports[removed]){int d=__builtin_popcountll(g.adj[p]&s);state+=mul*((s>>p&1)?3-d:0);mul*=3;}
   int score=2*__builtin_popcountll(s)-(n-1);
   if(score>val[removed][state]){val[removed][state]=score;wit[removed][state]=s;}
  }
 }
 for(int v=0;v<n;v++){out<<code<<' '<<v;for(int p:ports[v])out<<' '<<p;for(int k=0;k<27;k++)out<<' '<<val[v][k]<<' '<<wit[v][k];out<<'\n';}
 out.flush();std::cerr<<"DONE "<<n<<' '<<code<<std::endl;
 }
}catch(const std::exception&e){std::cerr<<e.what()<<std::endl;return 1;}}
