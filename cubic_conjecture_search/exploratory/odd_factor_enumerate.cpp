// Exhaustive cycle-space enumeration, independent of the vertex-degree solver.
// Input: one connected simple cubic graph6 graph per line, order at most 42.
// Output: exact size histogram, maximum witness, and all edge-deletion profiles.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
using U = std::uint64_t;

struct Graph {
    int n;
    std::vector<std::pair<int,int>> edges;
    std::vector<U> adjacent, incident;
    explicit Graph(const std::string& code) {
        if (code.empty()) throw std::runtime_error("empty graph6 line");
        n = static_cast<unsigned char>(code[0])-63;
        if (n<4 || n>42 || n%2 || code.size()!=1+(n*(n-1)/2+5)/6)
            throw std::runtime_error("expected graph6 of even order 4..42");
        for (unsigned char c:code) if(c<63 || c>126)
            throw std::runtime_error("invalid graph6 character");
        adjacent.resize(n); incident.resize(n);
        int bit=0;
        for(int v=1;v<n;v++) for(int u=0;u<v;u++,bit++)
            if ((code[1+bit/6]-63)&(1<<(5-bit%6))) {
                if(edges.size()>=63) throw std::runtime_error("too many edges");
                U e=U(1)<<edges.size(); edges.emplace_back(u,v);
                adjacent[u]|=U(1)<<v; adjacent[v]|=U(1)<<u;
                incident[u]|=e; incident[v]|=e;
            }
        for(U a:adjacent) if(__builtin_popcountll(a)!=3)
            throw std::runtime_error("graph is not cubic");
    }
    std::vector<U> cycle_basis() const {
        std::vector<int> parent(n,-1),depth(n),parent_edge(n,-1),queue{0};
        std::vector<bool> tree_edge(edges.size()); parent[0]=0;
        for(std::size_t i=0;i<queue.size();i++) {
            int v=queue[i]; U todo=incident[v];
            while(todo) {
                int e=__builtin_ctzll(todo); todo&=todo-1;
                auto [a,b]=edges[e]; int u=a^b^v;
                if(parent[u]>=0) continue;
                parent[u]=v; depth[u]=depth[v]+1; parent_edge[u]=e;
                tree_edge[e]=true; queue.push_back(u);
            }
        }
        if(queue.size()!=std::size_t(n)) throw std::runtime_error("graph is disconnected");
        std::vector<U> basis;
        for(int e=0;e<int(edges.size());e++) if(!tree_edge[e]) {
            auto [u,v]=edges[e]; U cycle=U(1)<<e;
            while(u!=v) {
                if(depth[u]<depth[v]) std::swap(u,v);
                cycle^=U(1)<<parent_edge[u]; u=parent[u];
            }
            for(U inc:incident) {
                int d=__builtin_popcountll(inc&cycle);
                if(d!=0 && d!=2) throw std::runtime_error("invalid fundamental cycle");
            }
            basis.push_back(cycle);
        }
        if(basis.size()!=std::size_t(n/2+1)) throw std::runtime_error("wrong cycle rank");
        return basis;
    }
};

void enumerate(const std::string& code) {
    Graph g(code); auto basis=g.cycle_basis();
    U factor=(U(1)<<g.edges.size())-1, total=U(1)<<basis.size();
    std::vector<U> histogram(g.n+1); int maximum=0; U witness=0;
    std::vector<int> deleted(g.edges.size()),through(g.edges.size(),-1);
    std::vector<U> deleted_witness(g.edges.size()),through_witness(g.edges.size());
    for(U step=0;step<total;step++) {
        if(step) factor^=basis[__builtin_ctzll(step)];
        U leaves=0;
        for(int v=0;v<g.n;v++)
            if(__builtin_popcountll(factor&g.incident[v])==1) leaves|=U(1)<<v;
        U bad=0, todo=leaves;
        while(todo) {
            int v=__builtin_ctzll(todo); todo&=todo-1;
            // An isolated factor edge is exactly an extra edge among leaves.
            if((g.adjacent[v]&leaves)==g.adjacent[v]) {
                bad|=U(1)<<v;
                if(__builtin_popcountll(bad)>2) break;
            }
        }
        int size=__builtin_popcountll(leaves);
        if(__builtin_popcountll(bad)==2) {
            int u=__builtin_ctzll(bad); bad&=bad-1; int v=__builtin_ctzll(bad);
            U chord=g.incident[u]&g.incident[v]&factor;
            if(!chord) throw std::runtime_error("unpaired degree-one vertices");
            int e=__builtin_ctzll(chord);
            if(size>deleted[e]) {deleted[e]=size; deleted_witness[e]=leaves;}
            continue;
        }
        if(bad) continue;
        histogram[size]++;
        if(size>maximum) {maximum=size;witness=leaves;}
        for(int e=0;e<int(g.edges.size());e++) {
            if(factor>>e&1) {
                if(size>deleted[e]) {deleted[e]=size; deleted_witness[e]=leaves;}
            } else if(size>through[e]) {through[e]=size; through_witness[e]=leaves;}
        }
    }
    std::cout<<"{\"graph6\":\"";
    for(char c:code) {if(c=='\\' || c=='\"') std::cout<<'\\'; std::cout<<c;}
    std::cout<<"\",\"order\":"<<g.n<<",\"factors_checked\":"<<total
             <<",\"maximum\":"<<maximum<<",\"witness\":"<<witness<<",\"histogram\":[";
    for(int s=0;s<=g.n;s++) {if(s) std::cout<<','; std::cout<<histogram[s];}
    std::cout<<"],\"edge_profiles\":[";
    for(int e=0;e<int(g.edges.size());e++) {
        if(e) std::cout<<',';
        auto [u,v]=g.edges[e];
        std::cout<<"["<<u<<','<<v<<','<<deleted[e]<<','<<through[e]<<','
                 <<deleted_witness[e]<<','<<through_witness[e]<<"]";
    }
    std::cout<<"]}"<<std::endl;
}

#ifndef ODD_FACTOR_LIBRARY
int main(int argc,char**argv) {
    try {
        if(argc<2) throw std::runtime_error("usage: odd_factor_enumerate graphs.g6 [...]");
        for(int i=1;i<argc;i++) {
            std::ifstream in(argv[i]);
            if(!in) throw std::runtime_error("cannot open input");
            std::string line;
            while(std::getline(in,line)) {if(!line.empty() && line.back()=='\r') line.pop_back(); enumerate(line);}
        }
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 2;}
    return 0;
}
#endif
