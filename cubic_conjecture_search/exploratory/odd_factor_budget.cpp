// Test the relaxed edge budget h(M)=|E(M)|+number_of_K2_components.
// All outputs are finite computations, not universal assertions.
#define ODD_FACTOR_LIBRARY
#include "odd_factor_enumerate.cpp"

int main(int argc,char**argv){try{
    if(argc<2)throw std::runtime_error("usage: odd_factor_budget input.g6 [...]");
    U graphs=0,factors=0,strict_bad_minima=0,tied_bad_minima=0;
    for(int file=1;file<argc;file++){
        std::ifstream in(argv[file]);if(!in)throw std::runtime_error("cannot open input");
        std::string code;
        while(std::getline(in,code)){
            Graph g(code);auto bs=g.cycle_basis();U factor=(U(1)<<g.edges.size())-1,total=U(1)<<bs.size();
            int good_min=1000000,bad_min=1000000;U good_f=0,bad_f=0;
            for(U s=0;s<total;s++){
                if(s)factor^=bs[__builtin_ctzll(s)];
                U leaves=0;for(int v=0;v<g.n;v++)if(__builtin_popcountll(g.incident[v]&factor)==1)leaves|=U(1)<<v;
                int bad_vertices=0;for(int v=0;v<g.n;v++)if((leaves>>v&1)&&((g.adjacent[v]&leaves)==g.adjacent[v]))bad_vertices++;
                int j=bad_vertices/2,h=__builtin_popcountll(factor)+j;
                if(j&&h<bad_min){bad_min=h;bad_f=factor;}
                if(!j&&h<good_min){good_min=h;good_f=factor;}
            }
            graphs++;factors+=total;
            if(bad_min<good_min){
                strict_bad_minima++;
                std::cout<<"STRICT_BAD_MINIMUM "<<code<<" bad_h="<<bad_min<<" good_h="<<good_min<<" bad_factor="<<bad_f<<" good_factor="<<good_f<<std::endl;
                return 1;
            }
            if(bad_min==good_min)tied_bad_minima++;
        }
        std::cout<<"DONE_FILE "<<argv[file]<<" graphs="<<graphs<<" factors="<<factors<<" strict_bad_minima="<<strict_bad_minima<<" tied_bad_minima="<<tied_bad_minima<<std::endl;
    }
    return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}}
