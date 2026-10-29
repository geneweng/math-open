// Check every vertex-triangle expansion of every cubic parent in an edge ball.
// Strict parent witnesses or half-sized vertex covers certify triangle lifts.
// Exhaust all simple cubic reconnections after deleting at most R seed edges.
// Reinserted edges must not belong to the seed: each candidate has exact distance k.
// Stub pairings may repeat a labelled graph; counts are reconnection records.
#define ODD_FACTOR_LIBRARY
#include "odd_factor_enumerate.cpp"
#include <functional>
#include <map>

struct Search {
 int n,threshold; U full; std::vector<U> adj; U result=0;
 bool good(U s) const {U t=s;while(t){int v=__builtin_ctzll(t);t&=t-1;if(__builtin_popcountll(adj[v]&s)!=2)return false;}return true;}
 bool visit(U yes,U no) {
  if(n-__builtin_popcountll(no)<threshold)return false;
  while(true){U oy=yes,on=no,unknown=full^(yes|no);
   for(int v=0;v<n;v++)if(!(no>>v&1)){
    int selected=__builtin_popcountll(adj[v]&yes);U free=adj[v]&unknown;
    if(selected>2||selected+__builtin_popcountll(free)<2){if(yes>>v&1)return false;no|=U(1)<<v;}
    else if(yes>>v&1){if(selected==2)no|=free;else if(selected+__builtin_popcountll(free)==2)yes|=free;}
    if(yes&no)return false;unknown=full^(yes|no);
   }
   if(n-__builtin_popcountll(no)<threshold)return false;
   if(oy==yes&&on==no)break;
  }
  U unknown=full^(yes|no);if(!unknown){result=yes;return true;}
  int best=-1,rank=-100;U todo=unknown;
  while(todo){int v=__builtin_ctzll(todo);todo&=todo-1;int r=4*__builtin_popcountll(adj[v]&yes)-__builtin_popcountll(adj[v]&unknown);if(r>rank){best=v;rank=r;}}
  return visit(yes|(U(1)<<best),no)||visit(yes,no|(U(1)<<best));
 }
 std::string encode()const{std::string s(1,char(n+63));int bits=0,k=0;for(int v=1;v<n;v++)for(int u=0;u<v;u++){bits=(bits<<1)|int(adj[v]>>u&1);if(++k==6){s+=char(bits+63);bits=k=0;}}if(k)s+=char((bits<<(6-k))+63);return s;}
};
int main(int argc,char**argv){try{
 if(argc!=5)throw std::runtime_error("usage: triangle_edge_ball SEED.g6 MASKS.txt RADIUS OUTPUT_PREFIX");
 std::ifstream sf(argv[1]),mf(argv[2]);std::string code;sf>>code;Graph g(code);
 std::vector<U> base(g.n);for(auto[u,v]:g.edges){base[u]|=U(1)<<v;base[v]|=U(1)<<u;}
 Search s{g.n,g.n/2,(U(1)<<g.n)-1,base};
 std::vector<U> witnesses;U w;while(mf>>w){if(__builtin_popcountll(w)<s.threshold||!s.good(w))throw std::runtime_error("bad seed witness");witnesses.push_back(w);}
 int radius=std::stoi(argv[3]);std::string prefix=argv[4];std::ofstream novel(prefix+"_novel.txt"),counts(prefix+"_counts.txt");

 U total=0,oracle=0;std::vector<int> stubs;
 auto leaf=[&](){total++;U covered=0;
  for(auto it=witnesses.rbegin();it!=witnesses.rend();++it)if(s.good(*it)){
   if(__builtin_popcountll(*it)>g.n/2){covered=s.full;break;}
   covered|=*it;if(covered==s.full)break;
  }
  if(covered==s.full)return;
  s.threshold=g.n/2+1;
  if(s.visit(0,0)){
   oracle++;witnesses.push_back(s.result);novel<<"STRICT "<<s.encode()<<' '<<s.result<<'\n';s.threshold=g.n/2;return;
  }
  s.threshold=g.n/2;
  if(!covered){
   if(!s.visit(0,0)){novel<<"PARENT_COUNTEREXAMPLE "<<s.encode()<<'\n';novel.flush();throw std::runtime_error("PARENT_COUNTEREXAMPLE");}
   covered|=s.result;witnesses.push_back(s.result);oracle++;novel<<"HALF "<<s.encode()<<' '<<s.result<<'\n';
  }
  for(int v=0;v<g.n;v++)if(!(covered>>v&1)){
   if(s.visit(U(1)<<v,0)){
    covered|=s.result;witnesses.push_back(s.result);oracle++;novel<<"HALF "<<s.encode()<<' '<<s.result<<'\n';
   }else{
    std::vector<U> a=s.adj;a.resize(g.n+2);std::vector<int> ns;
    for(int u=0;u<g.n;u++)if(s.adj[v]>>u&1){ns.push_back(u);a[u]&=~(U(1)<<v);}
    a[v]=0;std::vector<int> tri{v,g.n,g.n+1};
    for(int j=0;j<3;j++){int x=tri[j],u=ns[j];a[x]|=U(1)<<u;a[u]|=U(1)<<x;}
    for(int x:tri)for(int y:tri)if(x!=y)a[x]|=U(1)<<y;
    Search h{g.n+2,g.n/2+1,(U(1)<<(g.n+2))-1,a};
    if(!h.visit(0,0)){novel<<"EXPANDED_COUNTEREXAMPLE "<<s.encode()<<' '<<v<<' '<<h.encode()<<'\n';novel.flush();throw std::runtime_error("EXPANDED_COUNTEREXAMPLE");}
    oracle++;novel<<"EXPANDED "<<s.encode()<<' '<<v<<' '<<h.encode()<<' '<<h.result<<'\n';
   }
  }
 };
 std::function<void(unsigned)> pair=[&](unsigned used){unsigned all=(1u<<stubs.size())-1;if(used==all){leaf();return;}
  int i=__builtin_ctz(all^used),u=stubs[i];
  for(int j=i+1;j<int(stubs.size());j++)if(!(used>>j&1)){
   int v=stubs[j];if(u==v||(base[u]>>v&1)||(s.adj[u]>>v&1))continue;
   s.adj[u]|=U(1)<<v;s.adj[v]|=U(1)<<u;
   pair(used|(1u<<i)|(1u<<j));
   s.adj[u]^=U(1)<<v;s.adj[v]^=U(1)<<u;
  }
 };
 std::function<void(int,int)> remove=[&](int start,int left){if(!left){pair(0);return;}
  for(int e=start;e<=int(g.edges.size())-left;e++){
   auto[u,v]=g.edges[e];s.adj[u]^=U(1)<<v;s.adj[v]^=U(1)<<u;stubs.push_back(u);stubs.push_back(v);
   remove(e+1,left-1);stubs.pop_back();stubs.pop_back();s.adj[u]|=U(1)<<v;s.adj[v]|=U(1)<<u;
  }
 };
 for(int k=0;k<=radius;k++){U before=total,bo=oracle;remove(0,k);counts<<k<<' '<<total-before<<' '<<oracle-bo<<'\n';counts.flush();std::cerr<<"DONE k="<<k<<" records="<<total-before<<" new_witnesses="<<oracle-bo<<std::endl;}
 std::ofstream cover(prefix+"_cover.txt");for(U mask:witnesses)cover<<mask<<'\n';
 std::cout<<"COMPLETE records="<<total<<" oracle="<<oracle<<" cover="<<witnesses.size()<<std::endl;
}catch(const std::exception&e){std::cerr<<e.what()<<std::endl;return 1;}}
