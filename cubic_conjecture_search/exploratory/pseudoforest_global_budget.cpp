// Explore a global objective; this is not a test of the original conjecture.
#define ODD_FACTOR_LIBRARY
#include "odd_factor_enumerate.cpp"

int main(int argc, char** argv) { try {
    if(argc!=2) throw std::runtime_error("usage: pseudoforest_global_budget input.g6");
    std::ifstream in(argv[1]); if(!in)throw std::runtime_error("cannot open input");
    std::string code; U graphs=0,factors=0;
    while(std::getline(in,code)) {
        Graph g(code);auto bs=g.cycle_basis();U f=(U(1)<<g.edges.size())-1,total=U(1)<<bs.size();
        int best=-1,good=-1;U bestf=0,goodf=0;
        for(U step=0;step<total;step++) {
            if(step)f^=bs[__builtin_ctzll(step)];
            int m=__builtin_popcountll(f);if(m>g.n||m<good)continue;
            int p[42],nv[42],ne[42];for(int v=0;v<g.n;v++){p[v]=v;nv[v]=1;ne[v]=0;}
            auto root=[&](int v){while(p[v]!=v)v=p[v]=p[p[v]];return v;};
            for(int i=0;i<int(g.edges.size());i++)if(f>>i&1){auto [u,v]=g.edges[i];u=root(u);v=root(v);
                if(u==v)ne[u]++;else{p[v]=u;nv[u]+=nv[v];ne[u]+=ne[v]+1;}}
            bool pseudo=true;int j=0;
            for(int v=0;v<g.n;v++)if(p[v]==v){if(ne[v]>nv[v])pseudo=false;if(nv[v]==2)j++;}
            if(!pseudo)continue;
            if(m>best){best=m;bestf=f;}
            if(!j&&m>good){good=m;goodf=f;}
        }
        graphs++;factors+=total;
        if(best>good){std::cout<<"GLOBAL_OBSTRUCTION "<<code<<" maximum="<<best<<" good_maximum="<<good
            <<" maximum_factor="<<bestf<<" good_factor="<<goodf<<" graphs="<<graphs<<" factors="<<factors<<std::endl;return 1;}
    }
    std::cout<<"DONE graphs="<<graphs<<" factors="<<factors<<std::endl;
    return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}}
