// Exact classification of equality candidates, with positive witnesses saved.
// Every graph not listed as exact exits after certifying c_ind >= n/2+1.
#define TRIANGLE_PAIR_LIBRARY
#include "triangle_pair_search.cpp"

int main(int argc,char**argv) {try {
    if(argc<3)throw std::runtime_error("usage: tight_census OUTPUT INPUT.g6 [...]");
    std::ofstream out(argv[1]);if(!out)throw std::runtime_error("output");
    U count=0,tight=0;
    for(int file=2;file<argc;file++) {
        std::ifstream in(argv[file]);if(!in)throw std::runtime_error("input");
        std::string code;
        while(std::getline(in,code)) {
            Graph g(code);Subgraph h(g.n,g.edges);auto bs=h.basis();
            int best=0;U witness=0,c=0;bool exact=true;
            for(U step=1;step<(U(1)<<bs.size());step++) {
                c^=bs[__builtin_ctzll(step)];U s=0;
                for(int v=0;v<h.n;v++)if(c&h.inc[v])s|=U(1)<<v;
                int size=__builtin_popcountll(s);if(size<=best)continue;
                U todo=s;bool good=true;
                while(todo){int v=__builtin_ctzll(todo);todo&=todo-1;
                    if(__builtin_popcountll(h.adj[v]&s)!=2){good=false;break;}}
                if(!good)continue;
                best=size;witness=s;
                if(best>h.n/2){exact=false;break;}
            }
            out<<code<<' '<<best<<' '<<witness<<' '<<exact<<'\n';count++;
            if(exact){tight++;std::cerr<<"EXACT "<<code<<" order="<<h.n<<" maximum="<<best<<std::endl;}
            if(best<h.n/2)throw std::runtime_error("ORIGINAL COUNTEREXAMPLE CANDIDATE");
            if(count%100000==0)std::cerr<<"graphs="<<count<<" exact="<<tight<<std::endl;
        }
    }
    std::cout<<"DONE graphs="<<count<<" exact="<<tight<<std::endl;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}}
