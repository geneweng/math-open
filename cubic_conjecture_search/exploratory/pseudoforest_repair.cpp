// Test the proposed repair lemma on every odd spanning pseudoforest.
// Default potential: maximize edge count, then minimize isolated edges.
// With --k2, only the number of isolated-edge components is minimized.
// A permitted move toggles the edge set of one simple cycle and remains
// an odd spanning pseudoforest. This is an exhaustive finite test, not a proof.
#define ODD_FACTOR_LIBRARY
#include "odd_factor_enumerate.cpp"

struct DSU {
    int parent[42],size[42],cycles[42];
    explicit DSU(int n) {for(int i=0;i<n;i++){parent[i]=i;size[i]=1;cycles[i]=0;}}
    int root(int u) {while(parent[u]!=u){parent[u]=parent[parent[u]];u=parent[u];}return u;}
    bool add(int u,int v) {
        u=root(u);v=root(v);
        if(u==v) return ++cycles[u]<=1;
        if(size[u]<size[v]) std::swap(u,v);
        parent[v]=u;size[u]+=size[v];cycles[u]+=cycles[v];
        return cycles[u]<=1;
    }
};

int main(int argc,char**argv) {
    try {
        if(argc<2) throw std::runtime_error("usage: pseudoforest_repair [--k2] [--record-neutral] [--quiet] input.g6 [...]");
        bool k2_only=false,record_neutral=false,quiet=false;int first_file=1;
        while(first_file<argc) {
            std::string flag=argv[first_file];
            if(flag=="--k2")k2_only=true;
            else if(flag=="--record-neutral")record_neutral=true;
            else if(flag=="--quiet")quiet=true;
            else break;
            first_file++;
        }
        if(first_file==argc)throw std::runtime_error("missing input");
        U graphs=0,factors=0,pseudofactors=0,badfactors=0,moves=0,strict=0,plateau=0,flat_repairs=0,max_flat=0,max_repair_moves=0;
        for(int file=first_file;file<argc;file++) {
            std::ifstream in(argv[file]); if(!in) throw std::runtime_error("cannot open input");
            std::string code;
            while(std::getline(in,code)) {
                Graph g(code);auto bs=g.cycle_basis();U total=U(1)<<bs.size();
                if(g.n>18&&!quiet)std::cerr<<"start graph "<<graphs+1<<" order "<<g.n<<" factors "<<total<<std::endl;
                U full=(U(1)<<g.edges.size())-1,even=0;
                std::vector<int> potential(total,-1000000),isolated(total,-1),sizes(total,-1);
                std::vector<U> cycles,bad;
                for(U step=0;step<total;step++) {
                    if(step) even^=bs[__builtin_ctzll(step)];
                    U index=step^(step>>1),factor=full^even;
                    DSU mf(g.n),cf(g.n);bool pseudo=true;
                    for(int e=0;e<int(g.edges.size());e++) {
                        auto [u,v]=g.edges[e];
                        if(factor>>e&1) {if(!mf.add(u,v))pseudo=false;}
                        else cf.add(u,v);
                    }
                    int circuit_components=0,k2=0;
                    for(int v=0;v<g.n;v++) {
                        if(cf.root(v)==v && cf.size[v]>1)circuit_components++;
                        if(mf.root(v)==v && mf.size[v]==2)k2++;
                    }
                    if(circuit_components==1)cycles.push_back(index);
                    if(!pseudo)continue;
                    pseudofactors++;
                    potential[index]=k2_only?-k2:__builtin_popcountll(factor)*(g.n+1)-k2;
                    isolated[index]=k2;
                    sizes[index]=__builtin_popcountll(factor);
                    if(k2){bad.push_back(index);badfactors++;}
                }
                for(U index:bad) {
                    bool improved=false;
                    for(U c:cycles) {
                        moves++;
                        if(potential[index^c]>potential[index]) {
                            improved=true;
                            if(sizes[index^c]>sizes[index])strict++;
                            else plateau++;
                            break;
                        }
                    }
                    if(!improved) {
                        if(record_neutral) {
                            U factor=full;
                            for(int i=0;i<int(bs.size());i++)if(index>>i&1)factor^=bs[i];
                            std::cout<<"NEUTRAL "<<code<<" "<<factor<<" "<<isolated[index]<<std::endl;
                        }
                        std::vector<U> queue{index};std::vector<int>depth(total,-1);depth[index]=0;
                        int repair_moves=-1;
                        for(std::size_t head=0;head<queue.size()&&!improved;head++) {
                            U current=queue[head];
                            for(U c:cycles) {
                                U next=current^c;moves++;
                                if(potential[next]>potential[index]){improved=true;repair_moves=depth[current]+1;break;}
                                if(potential[next]==potential[index]&&depth[next]<0){depth[next]=depth[current]+1;queue.push_back(next);}
                            }
                        }
                        max_flat=std::max(max_flat,U(queue.size()));
                        if(improved){flat_repairs++;max_repair_moves=std::max(max_repair_moves,U(repair_moves));
                            if(record_neutral)std::cout<<"REPAIR_MOVES "<<repair_moves<<std::endl;}
                    }
                    if(!improved) {
                        U factor=full;
                        for(int i=0;i<int(bs.size());i++)if(index>>i&1)factor^=bs[i];
                        std::cout<<"TRAP "<<code<<" factor="<<factor<<" edges="
                                 <<__builtin_popcountll(factor)<<" isolated="<<isolated[index]
                                 <<" simple_cycles="<<cycles.size()<<std::endl;
                        return 1;
                    }
                }
                graphs++;factors+=total;
                if(graphs%10000==0)std::cerr<<"checked "<<graphs<<std::endl;
            }
            std::cout<<"DONE_FILE "<<argv[file]<<" graphs="<<graphs<<" factors="<<factors
                     <<" pseudofactors="<<pseudofactors<<" bad_pseudofactors="<<badfactors
                     <<" tested_moves="<<moves<<" first_strict="<<strict
                     <<" first_plateau="<<plateau<<" flat_repairs="<<flat_repairs
                     <<" max_flat_size="<<max_flat<<" max_neutral_repair_moves="<<max_repair_moves<<std::endl;
        }
    } catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}
}
