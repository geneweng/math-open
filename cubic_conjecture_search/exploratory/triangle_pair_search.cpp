// Direct search of the branch inequality after two edge-triangle expansions.
// Eulerian edge sets in a subcubic graph are disjoint cycles; their supports
// are checked for inducedness. A saved mask is a positive certificate only.
#define ODD_FACTOR_LIBRARY
#include "odd_factor_enumerate.cpp"

struct Subgraph {
    int n;
    std::vector<std::pair<int,int>> es;
    std::vector<U> adj, inc;
    Subgraph(int order, std::vector<std::pair<int,int>> edges):n(order),es(edges),adj(n),inc(n) {
        if(n>42 || es.size()>63) throw std::runtime_error("size limit");
        for(int i=0;i<int(es.size());i++) {
            auto [u,v]=es[i];
            if(u==v || (adj[u]>>v&1)) throw std::runtime_error("not simple");
            adj[u]|=U(1)<<v; adj[v]|=U(1)<<u;
            inc[u]|=U(1)<<i; inc[v]|=U(1)<<i;
        }
        for(U a:adj) if(__builtin_popcountll(a)<2 || __builtin_popcountll(a)>3)
            throw std::runtime_error("not subcubic with minimum degree two");
    }
    std::vector<U> basis() const {
        std::vector<int> p(n,-1),dep(n),pe(n),q{0};
        std::vector<bool> tree(es.size()); p[0]=0;
        for(unsigned k=0;k<q.size();k++) {
            int v=q[k]; U todo=inc[v];
            while(todo) {
                int e=__builtin_ctzll(todo);todo&=todo-1;
                auto [a,b]=es[e];int u=a^b^v;
                if(p[u]>=0)continue;
                p[u]=v;dep[u]=dep[v]+1;pe[u]=e;tree[e]=true;q.push_back(u);
            }
        }
        if(q.size()!=unsigned(n))throw std::runtime_error("not connected");
        std::vector<U> out;
        for(int e=0;e<int(es.size());e++)if(!tree[e]) {
            auto [u,v]=es[e];U c=U(1)<<e;
            while(u!=v){if(dep[u]<dep[v])std::swap(u,v);c^=U(1)<<pe[u];u=p[u];}
            out.push_back(c);
        }
        if(out.size()!=es.size()-n+1)throw std::runtime_error("cycle rank");
        return out;
    }
    std::pair<int,U> search(bool exact=false) const {
        auto bs=basis(); U branches=0,c=0,w=0;int best=0,target=int(es.size())-n;
        for(int v=0;v<n;v++)if(__builtin_popcountll(adj[v])==3)branches|=U(1)<<v;
        for(U step=1;step<(U(1)<<bs.size());step++) {
            c^=bs[__builtin_ctzll(step)]; U s=0;
            for(int v=0;v<n;v++)if(c&inc[v])s|=U(1)<<v;
            int val=__builtin_popcountll(s&branches);if(val<=best)continue;
            U todo=s;bool good=true;
            while(todo){int v=__builtin_ctzll(todo);todo&=todo-1;
                if(__builtin_popcountll(adj[v]&s)!=2){good=false;break;}}
            if(good){best=val;w=s;if(!exact && best>=target)break;}
        }
        return {best,w};
    }
};

std::vector<std::pair<int,int>> expand_pair(const Graph& g,int e,int f) {
    auto es=g.edges; auto [u,v]=es[e];auto [x,y]=es[f];int a=g.n,b=a+1,w=a+2,c=a+3,d=a+4,z=a+5;
    es[e]={u,a};es[f]={x,c};
    for(auto edge:std::vector<std::pair<int,int>>{{a,b},{b,v},{a,w},{b,w},{c,d},{d,y},{c,z},{d,z}})es.push_back(edge);
    return es;
}

#ifndef TRIANGLE_PAIR_LIBRARY
int main(int argc,char**argv) {
    try {
        if(argc<3)throw std::runtime_error("usage: triangle_pair_search OUTPUT.txt INPUT.g6 [...]");
        std::ofstream out(argv[1]);if(!out)throw std::runtime_error("output");
        unsigned long long bases=0,cases=0;
        for(int arg=2;arg<argc;arg++) {
            std::ifstream in(argv[arg]);if(!in)throw std::runtime_error("input");std::string code;
            while(std::getline(in,code)) {
                Graph g(code);bases++;
                for(int e=0;e<int(g.edges.size());e++)for(int f=e+1;f<int(g.edges.size());f++) {
                    Subgraph h(g.n+6,expand_pair(g,e,f));auto [score,w]=h.search();cases++;
                    out<<code<<' '<<e<<' '<<f<<' '<<score<<' '<<w<<'\n';
                    if(score<int(h.es.size())-h.n) {
                        out.flush();std::cout<<"COUNTEREXAMPLE_CANDIDATE "<<code<<' '<<e<<' '<<f<<' '<<score<<std::endl;return 1;
                    }
                }
                if(bases%1000==0)std::cerr<<"bases="<<bases<<" cases="<<cases<<std::endl;
            }
        }
        std::cout<<"DONE bases="<<bases<<" cases="<<cases<<std::endl;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 2;}
}
#endif
