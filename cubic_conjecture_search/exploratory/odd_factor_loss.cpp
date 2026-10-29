// Test the auxiliary inequality c_ind(G) >= leaves(M)-2*j(M).
// A failure is NOT a counterexample to the original conjecture.
#define ODD_FACTOR_LIBRARY
#include "odd_factor_enumerate.cpp"

int main(int argc,char**argv) { try {
    U graphs=0,states=0;
    for(int arg=1;arg<argc;arg++) {
        std::ifstream in(argv[arg]);if(!in)throw std::runtime_error("input");std::string code;
        while(std::getline(in,code)) {
            Graph g(code);auto bs=g.cycle_basis();U f=(U(1)<<g.edges.size())-1;
            int best=0,bound=0;U fw=0,sw=0;
            for(U k=0;k<(U(1)<<bs.size());k++) {
                if(k)f^=bs[__builtin_ctzll(k)];U s=0;
                for(int v=0;v<g.n;v++)if(__builtin_popcountll(f&g.incident[v])==1)s|=U(1)<<v;
                int bad=0;
                for(int v=0;v<g.n;v++)if(s>>v&1)bad+=((g.adjacent[v]&s)==g.adjacent[v]);
                int size=__builtin_popcountll(s),b=size-bad;
                if(b>bound){bound=b;fw=f;}
                if(!bad&&size>best){best=size;sw=s;}
            }
            graphs++;states+=U(1)<<bs.size();
            if(bound>best) {
                std::cout<<"AUXILIARY_FAILURE "<<code<<" n="<<g.n<<" c_ind="<<best<<" proposed_lower_bound="<<bound<<" factor="<<fw<<" good_witness="<<sw<<" graphs="<<graphs<<" states="<<states<<std::endl;
                return 1;
            }
        }
    }
    std::cout<<"DONE graphs="<<graphs<<" states="<<states<<std::endl;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}}
