// Subdivide two disjoint edges and join the subdivision vertices.
// Test the original half-bound directly on each resulting cubic graph.
#define main edge_ball_unused_main
#include "edge_ball_enumerate.cpp"
#undef main
int main(int argc,char**argv){try{
 if(argc!=3)throw std::runtime_error("usage: two_edge_extension INPUT EXCEPTIONS");
 std::ifstream in(argv[1]);std::ofstream exc(argv[2]);std::string code;U count=0;int parents=0;
 while(in>>code){int n=int(code[0])-63;if(n<4||n>60||int(code.size())!=1+(n*(n-1)/2+5)/6)throw std::runtime_error("encoding");
  std::vector<U>a(n+2);std::vector<std::pair<int,int>>es;int bit=0;
  for(int v=1;v<n;v++)for(int u=0;u<v;u++,bit++)if((code[1+bit/6]-63)>>(5-bit%6)&1){a[u]|=U(1)<<v;a[v]|=U(1)<<u;es.push_back({u,v});}
  for(int v=0;v<n;v++)if(__builtin_popcountll(a[v])!=3)throw std::runtime_error("not cubic");
  U before=count;
  for(int i=0;i<int(es.size());i++)for(int j=i+1;j<int(es.size());j++){
   auto[u,v]=es[i];auto[w,z]=es[j];if(u==w||u==z||v==w||v==z)continue;
   auto b=a;auto del=[&](int x,int y){b[x]&=~(U(1)<<y);b[y]&=~(U(1)<<x);};
   auto add=[&](int x,int y){b[x]|=U(1)<<y;b[y]|=U(1)<<x;};
   del(u,v);del(w,z);add(u,n);add(v,n);add(w,n+1);add(z,n+1);add(n,n+1);
   Search s{n+2,(n+2)/2,(U(1)<<(n+2))-1,b};
   if(!s.visit(0,0)){exc<<"CANDIDATE "<<parents<<' '<<i<<' '<<j<<' '<<s.encode()<<std::endl;throw std::runtime_error("candidate requires independent verification");}
   if(!s.good(s.result)||__builtin_popcountll(s.result)<s.threshold)throw std::runtime_error("invalid witness");
   std::cout<<parents<<' '<<i<<' '<<j<<' '<<s.result<<'\n';count++;
  }
  std::cerr<<"PARENT "<<parents<<" order "<<n<<" cases "<<count-before<<std::endl;parents++;
 }
 std::cerr<<"COMPLETE parents "<<parents<<" cases "<<count<<std::endl;
}catch(const std::exception&e){std::cerr<<e.what()<<std::endl;return 1;}}
