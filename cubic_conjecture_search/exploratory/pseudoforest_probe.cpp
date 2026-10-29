// Exhaust every simple-cycle exchange from specified odd pseudoforests.
// Input lines: graph6 followed by the decimal factor edge mask.
#define ODD_FACTOR_LIBRARY
#include "odd_factor_enumerate.cpp"
#include <sstream>
#include <functional>

struct UnionFind {
    int p[42],sz[42],ec[42];
    explicit UnionFind(int n) {for(int i=0;i<n;i++){p[i]=i;sz[i]=1;ec[i]=0;}}
    int root(int u){while(p[u]!=u)u=p[u]=p[p[u]];return u;}
    void add(int u,int v){u=root(u);v=root(v);if(u==v){ec[u]++;return;}
        if(sz[u]<sz[v])std::swap(u,v);p[v]=u;sz[u]+=sz[v];ec[u]+=ec[v]+1;}
};

int isolated_if_pseudo(const Graph&g,U f) {
    UnionFind d(g.n);int k=0;
    for(int e=0;e<int(g.edges.size());e++)if(f>>e&1)d.add(g.edges[e].first,g.edges[e].second);
    for(int v=0;v<g.n;v++)if(d.root(v)==v){if(d.ec[v]>d.sz[v])return -1;if(d.sz[v]==2)k++;}
    return k;
}

int main(int argc,char**argv){try{
    if(argc<2||argc>3)throw std::runtime_error("usage: pseudoforest_probe input.txt [--first]");
    bool first=argc==3&&std::string(argv[2])=="--first";
    if(argc==3&&!first)throw std::runtime_error("unknown argument");
    std::ifstream in(argv[1]);if(!in)throw std::runtime_error("cannot open input");
    std::string code;U factor;
    while(in>>code>>factor){
        Graph g(code);auto bs=g.cycle_basis();int old=isolated_if_pseudo(g,factor);
        if(old<0)throw std::runtime_error("input is not a pseudoforest");
        for(U inc:g.incident)if(__builtin_popcountll(inc&factor)%2!=1)
            throw std::runtime_error("input factor is not odd");
        U even=0,total=U(1)<<bs.size(),nc=0,valid=0,better=0,neutral=0,best=0;
        int minimum=old,min_edges=__builtin_popcountll(factor),max_edges=min_edges;
        auto check_cycle=[&](U cycle){
            nc++;U next=factor^cycle;int k=isolated_if_pseudo(g,next);if(k<0)return;valid++;
            if(k<old)better++;if(k==old)neutral++;
            if(k<minimum){minimum=k;best=cycle;}
            min_edges=std::min(min_edges,__builtin_popcountll(next));
            max_edges=std::max(max_edges,__builtin_popcountll(next));
        };
        if(first){
            std::function<void(int,int,int,U,U)> dfs=[&](int start,int second,int v,U seen,U edges){
                if(better)return;
                U todo=g.adjacent[v];
                while(todo&&!better){int u=__builtin_ctzll(todo);todo&=todo-1;
                    U e=g.incident[u]&g.incident[v];
                    if(u==start&&second<v)check_cycle(edges|e);
                    else if(u>start&&!(seen>>u&1))dfs(start,second,u,seen|(U(1)<<u),edges|e);
                }
            };
            for(int s=0;s<g.n&&!better;s++)for(int u=s+1;u<g.n&&!better;u++)if(g.adjacent[s]>>u&1)
                dfs(s,u,u,(U(1)<<s)|(U(1)<<u),g.incident[s]&g.incident[u]);
        }else for(U s=1;s<total;s++){
            even^=bs[__builtin_ctzll(s)];UnionFind d(g.n);
            for(int e=0;e<int(g.edges.size());e++)if(even>>e&1)d.add(g.edges[e].first,g.edges[e].second);
            int components=0;for(int v=0;v<g.n;v++)if(d.root(v)==v&&d.sz[v]>1)components++;
            if(components!=1)continue;check_cycle(even);
        }
        std::cout<<"{\"graph6\":\"";for(char c:code){if(c=='\\'||c=='\"')std::cout<<'\\';std::cout<<c;}
        std::cout<<"\",\"factor\":"<<factor<<",\"isolated\":"<<old<<",\"cycles\":"<<nc
                 <<",\"valid_moves\":"<<valid<<",\"improving\":"<<better<<",\"neutral\":"<<neutral
                 <<",\"minimum_after_one_move\":"<<minimum<<",\"best_cycle\":"<<best
                 <<",\"all_cycles_exhausted\":"<<((!first||!better)?"true":"false")
                 <<",\"min_edges_after_one_move\":"<<min_edges<<",\"max_edges_after_one_move\":"<<max_edges<<"}"<<std::endl;
    }
    return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}}
