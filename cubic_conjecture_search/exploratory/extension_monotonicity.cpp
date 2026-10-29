// Exact search for failures of additive monotonicity under two-edge extension.
#define main edge_ball_unused_main
#include "edge_ball_enumerate.cpp"
#undef main
int optimum(Search &s) {
 for(int k=s.n;k>=0;--k){s.threshold=k;if(s.visit(0,0))return k;}
 throw std::runtime_error("empty set missing");
}
int main(){std::string code;unsigned long long count=0;int low=100;while(std::cin>>code){
 Graph g(code);std::vector<U>a(g.n);for(auto[u,v]:g.edges){a[u]|=U(1)<<v;a[v]|=U(1)<<u;}
 Search base{g.n,0,(U(1)<<g.n)-1,a};int before=optimum(base);
 for(int i=0;i<int(g.edges.size());i++)for(int j=i+1;j<int(g.edges.size());j++){
 auto[u,v]=g.edges[i];auto[w,z]=g.edges[j];if(u==w||u==z||v==w||v==z)continue;
 auto b=a;b.resize(g.n+2);b[u]^=U(1)<<v;b[v]^=U(1)<<u;b[w]^=U(1)<<z;b[z]^=U(1)<<w;
 for(auto[x,y]:std::vector<std::pair<int,int>>{{u,g.n},{v,g.n},{w,g.n+1},{z,g.n+1},{g.n,g.n+1}}){b[x]|=U(1)<<y;b[y]|=U(1)<<x;}
 Search h{g.n+2,before+1,(U(1)<<(g.n+2))-1,b};count++;
 if(h.visit(0,0))continue;
 int after=optimum(h);std::cout<<code<<' '<<u<<' '<<v<<' '<<w<<' '<<z<<' '<<before<<' '<<after<<' '<<h.result<<'\n';
 if(after-before<low){low=after-before;std::cerr<<"LOW "<<low<<" n="<<g.n<<" cases="<<count<<std::endl;}
 }
 }std::cerr<<"COMPLETE cases="<<count<<" minimum_failed_delta="<<low<<std::endl;}
