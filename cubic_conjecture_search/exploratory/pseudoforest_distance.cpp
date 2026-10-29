// Exact shortest monotone-j repair for specified odd pseudoforests.
// A state limit is reported as unresolved, never as an obstruction.
#define ODD_FACTOR_LIBRARY
#include "odd_factor_enumerate.cpp"
#include <functional>
#include <unordered_map>

int j_if_pseudo(const Graph&g,U f) {
    int parent[42],size[42],edge_count[42];
    for(int i=0;i<g.n;i++){parent[i]=i;size[i]=1;edge_count[i]=0;}
    auto root=[&](int v){while(v!=parent[v])v=parent[v]=parent[parent[v]];return v;};
    for(int i=0;i<int(g.edges.size());i++)if(f>>i&1) {
        auto [a,b]=g.edges[i];a=root(a);b=root(b);
        if(a==b)edge_count[a]++;
        else {parent[b]=a;size[a]+=size[b];edge_count[a]+=edge_count[b]+1;}
    }
    int isolated=0;
    for(int v=0;v<g.n;v++)if(parent[v]==v) {
        if(edge_count[v]>size[v])return -1;
        if(size[v]==2)isolated++;
    }
    return isolated;
}

int main(int argc,char**argv) {try {
    if(argc<2||argc>3)throw std::runtime_error("usage: pseudoforest_distance input.txt [state-limit]");
    std::size_t limit=argc==3?std::stoull(argv[2]):200000;
    std::ifstream in(argv[1]);if(!in)throw std::runtime_error("cannot open input");
    std::string code;U factor;int inputs=0;
    while(in>>code>>factor) {
        Graph g(code);g.cycle_basis();
        if(factor>>g.edges.size())throw std::runtime_error("factor contains a nonexistent edge");
        for(U inc:g.incident)if(__builtin_popcountll(inc&factor)%2!=1)throw std::runtime_error("factor not odd");
        int initial=j_if_pseudo(g,factor);if(initial<=0)throw std::runtime_error("expected bad pseudoforest");
        std::unordered_map<U,int> cache;
        auto state=[&](U f){auto it=cache.find(f);if(it!=cache.end())return it->second;
            int j=j_if_pseudo(g,f);cache.emplace(f,j);return j;};
        std::vector<U> cycles,queue{factor};
        std::unordered_map<U,std::pair<U,int>> parent{{factor,{factor,0}}};
        U terminal=0;bool found=false,limited=false;
        auto inspect=[&](U current,U cycle) {
            U next=current^cycle;int j=state(next);
            if(j<0||j>initial||parent.count(next))return;
            parent.emplace(next,std::make_pair(current,parent.at(current).second+1));
            if(j<initial){terminal=next;found=true;}
            else queue.push_back(next);
        };
        std::function<void(int,int,int,U,U)> dfs=[&](int start,int second,int v,U seen,U path) {
            if(found)return;
            U todo=g.adjacent[v];
            while(todo&&!found){int u=__builtin_ctzll(todo);todo&=todo-1;
                U edge=g.incident[v]&g.incident[u];
                if(u==start&&second<v){cycles.push_back(path|edge);inspect(factor,path|edge);}
                else if(u>start&&!(seen>>u&1))dfs(start,second,u,seen|(U(1)<<u),path|edge);
            }
        };
        for(int s=0;s<g.n&&!found;s++)for(int u=s+1;u<g.n&&!found;u++)if(g.adjacent[s]>>u&1)
            dfs(s,u,u,(U(1)<<s)|(U(1)<<u),g.incident[s]&g.incident[u]);
        bool exhausted=!found;
        std::size_t root_neutral=queue.size()-1;
        for(std::size_t head=1;head<queue.size()&&!found;head++) {
            if(parent.size()>limit){limited=true;break;}
            U current=queue[head];
            for(U cycle:cycles){inspect(current,cycle);if(found)break;}
        }
        std::vector<U> path;
        if(found){U f=terminal;while(f!=factor){path.push_back(f);f=parent.at(f).first;}path.push_back(factor);std::reverse(path.begin(),path.end());}
        std::cout<<"{\"graph6\":\"";for(char c:code){if(c=='\\'||c=='\"')std::cout<<'\\';std::cout<<c;}
        std::cout<<"\",\"factor\":"<<factor<<",\"order\":"<<g.n<<",\"initial_j\":"<<initial
                 <<",\"cycles_examined_at_root\":"<<cycles.size()<<",\"root_cycles_exhausted\":"<<(exhausted?"true":"false")
                 <<",\"root_neutral_discovered\":"<<root_neutral<<",\"states_discovered\":"<<parent.size()
                 <<",\"status\":\""<<(found?"repaired":limited?"state_limit":"trapped")<<"\",\"minimum_moves\":"<<(found?int(path.size())-1:-1)<<",\"path\":[";
        for(std::size_t i=0;i<path.size();i++){if(i)std::cout<<',';std::cout<<path[i];}
        std::cout<<"]}"<<std::endl;
        if(++inputs%100==0)std::cerr<<"checked "<<inputs<<std::endl;
    }
    return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}}
