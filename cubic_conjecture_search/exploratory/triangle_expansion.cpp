// Exact vertex profiles for replacing one cubic vertex by a triangle.
// If D is the maximum good-set size containing v in G-e, over incident
// edges e, B the maximum avoiding v in G, and C avoiding N[v] in G,
// the expanded graph has c_ind=max(D+1,B,C+3).
#define ODD_FACTOR_LIBRARY
#include "odd_factor_enumerate.cpp"

int main(int argc,char**argv) {try {
    if(argc<2)throw std::runtime_error("usage: triangle_expansion input.g6 [...]");
    U graphs=0,vertices=0,failures=0;
    for(int file=1;file<argc;file++) {
        std::ifstream in(argv[file]);if(!in)throw std::runtime_error("cannot open input");
        std::string code;
        while(std::getline(in,code)) {
            Graph g(code);auto basis=g.cycle_basis();
            U factor=(U(1)<<g.edges.size())-1,total=U(1)<<basis.size();
            std::vector<int>a(g.n,-1000),b(g.n),c(g.n),d(g.n,-1000);
            int maximum=0;
            for(U step=0;step<total;step++) {
                if(step)factor^=basis[__builtin_ctzll(step)];
                U leaves=0;
                for(int v=0;v<g.n;v++)if(__builtin_popcountll(factor&g.incident[v])==1)leaves|=U(1)<<v;
                U bad=0,todo=leaves;
                while(todo){int v=__builtin_ctzll(todo);todo&=todo-1;
                    if((g.adjacent[v]&leaves)==g.adjacent[v])bad|=U(1)<<v;}
                int size=__builtin_popcountll(leaves);
                if(__builtin_popcountll(bad)==2) {
                    while(bad){int v=__builtin_ctzll(bad);bad&=bad-1;d[v]=std::max(d[v],size);}
                    continue;
                }
                if(bad)continue;
                maximum=std::max(maximum,size);
                for(int v=0;v<g.n;v++) {
                    if(leaves>>v&1){a[v]=std::max(a[v],size);d[v]=std::max(d[v],size);}
                    else {b[v]=std::max(b[v],size);if(!(leaves&g.adjacent[v]))c[v]=std::max(c[v],size);}
                }
            }
            for(int v=0;v<g.n;v++) {
                int expanded=std::max({d[v]+1,b[v],c[v]+3});vertices++;
                if(expanded<maximum+1) {
                    failures++;
                    std::cout<<"NO_UNIT_GAIN "<<code<<" vertex="<<v<<" original="<<maximum
                             <<" expanded="<<expanded<<" A="<<a[v]<<" B="<<b[v]<<" C="<<c[v]<<" D="<<d[v]<<'\n';
                }
                if(expanded<(g.n+2)/2)throw std::runtime_error("original conjecture candidate");
            }
            graphs++;
        }
        std::cout<<"DONE graphs="<<graphs<<" vertices="<<vertices<<" no_unit_gain="<<failures<<std::endl;
    }
    return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}}
