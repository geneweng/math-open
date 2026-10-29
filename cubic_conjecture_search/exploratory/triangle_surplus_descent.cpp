// Search the ORIGINAL half-order conjecture via exact branch-surplus descent.
// An edge-triangle replacement has optimum max(B,T+2,C+2), with the
// ORIGINAL branch weights used in every boundary state. The default follows
// strict surplus decreases; --neutral-depth also permits neutral steps to
// the given depth. Neither mode is a census of all constructions.
#define TRIANGLE_PAIR_LIBRARY
#include "triangle_pair_search.cpp"
#include <map>
#include <set>

struct EP {int b=0,t=-1000,c=0;U wb=0,wt=0,wc=0;};
struct Profile {int maximum=0;U witness=0;bool exact=true;std::vector<EP> edge;};

std::string code_of(const Subgraph&g) {
    std::string out(1,char(g.n+63));int bits=0,k=0;
    for(int v=1;v<g.n;v++)for(int u=0;u<v;u++) {
        bits=(bits<<1)|int(g.adj[u]>>v&1);k++;
        if(k==6){out+=char(bits+63);bits=k=0;}
    }
    if(k)out+=char((bits<<(6-k))+63);
    return out;
}

Profile analyze(const Subgraph&g,int stop_above=-1) {
    Profile p;p.edge.resize(g.es.size());auto bs=g.basis();U c=0,branches=0;
    for(int v=0;v<g.n;v++)if(__builtin_popcountll(g.adj[v])==3)branches|=U(1)<<v;
    for(U step=1;step<(U(1)<<bs.size());step++) {
        c^=bs[__builtin_ctzll(step)];U s=0,bad=0;
        for(int v=0;v<g.n;v++)if(c&g.inc[v])s|=U(1)<<v;
        U todo=s;
        while(todo){int v=__builtin_ctzll(todo);todo&=todo-1;
            if(__builtin_popcountll(g.adj[v]&s)==3){bad|=U(1)<<v;if(__builtin_popcountll(bad)>2)break;}}
        int score=__builtin_popcountll(s&branches);
        if(!bad) {
            if(score>p.maximum){p.maximum=score;p.witness=s;}
            if(stop_above>=0&&p.maximum>stop_above){p.exact=false;return p;}
            for(int e=0;e<int(g.es.size());e++) {
                auto[u,v]=g.es[e];bool x=s>>u&1,y=s>>v&1;auto&r=p.edge[e];
                if(x&&y){if(score>r.t){r.t=score;r.wt=s;}}
                else {if(score>r.b){r.b=score;r.wb=s;}
                    if(!x&&!y&&score>r.c){r.c=score;r.wc=s;}}
            }
        } else if(__builtin_popcountll(bad)==2) {
            int u=__builtin_ctzll(bad);bad&=bad-1;int v=__builtin_ctzll(bad);
            U chord=g.inc[u]&g.inc[v]&~c;
            if(!chord)throw std::runtime_error("unpaired chord endpoints");
            int e=__builtin_ctzll(chord);auto&r=p.edge[e];
            if(score>r.b){r.b=score;r.wb=s;}
        }
    }
    return p;
}

Subgraph expand(const Subgraph&g,int e) {
    auto es=g.es;auto[u,v]=es[e];int a=g.n,b=a+1,w=a+2;
    es[e]={u,a};
    for(auto xy:std::vector<std::pair<int,int>>{{a,b},{b,v},{a,w},{b,w}})es.push_back(xy);
    return Subgraph(g.n+3,es);
}

#ifndef TRIANGLE_DESCENT_LIBRARY
int main(int argc,char**argv) {try {
    if(argc<4)throw std::runtime_error("usage: triangle_surplus_descent PREFIX MAX_CHILDREN [--neutral-depth DEPTH] INPUT.g6 [...]");
    std::string prefix=argv[1];U limit=std::stoull(argv[2]);
    int first_file=3,max_depth=100;bool neutral=false;
    if(std::string(argv[3])=="--neutral-depth") {
        if(argc<6)throw std::runtime_error("missing neutral depth or inputs");
        neutral=true;max_depth=std::stoi(argv[4]);first_file=5;
    }
    std::ofstream nodes(prefix+"_nodes.txt"),transitions(prefix+"_transitions.txt");
    if(!nodes||!transitions)throw std::runtime_error("output");
    U roots=0,exact_roots=0,children=0,lowerings=0,neutral_moves=0,skipped_size=0,skipped_limit=0,skipped_depth=0;
    std::set<std::string>seen;std::map<int,U>levels,surpluses;
    auto descend=[&](auto&& self,const Subgraph&g,const Profile&p,int depth)->void {
        int target=int(g.es.size())-g.n;
        if(p.maximum<target)throw std::runtime_error("ORIGINAL COUNTEREXAMPLE CANDIDATE");
        for(int e=0;e<int(g.es.size());e++) {
            const auto&r=p.edge[e];int next=std::max({r.b,r.t+2,r.c+2});
            if(next>p.maximum+int(neutral))continue;
            // Good sets always lift with nonnegative gain. This catches errors.
            if(next<p.maximum)throw std::runtime_error("optimum decreased");
            if(next==p.maximum)lowerings++;else neutral_moves++;
            auto[u,v]=g.es[e];
            transitions<<code_of(g)<<' '<<u<<' '<<v<<' '<<p.maximum<<' '
                <<r.b<<' '<<r.t<<' '<<r.c<<' '<<r.wb<<' '<<r.wt<<' '<<r.wc<<'\n';
            if(next<target+1){transitions.flush();throw std::runtime_error("ORIGINAL COUNTEREXAMPLE CANDIDATE IN PREDICTED PROFILE");}
            if(depth>=max_depth){skipped_depth++;continue;}
            if(g.n+3>42||g.es.size()+4>63){skipped_size++;continue;}
            Subgraph h=expand(g,e);std::string code=code_of(h);
            if(!seen.insert(code).second)continue;
            if(children>=limit){skipped_limit++;continue;}
            children++;Profile q=analyze(h);int surplus=q.maximum-(int(h.es.size())-h.n);
            if(q.maximum!=next)throw std::runtime_error("triangle formula mismatch");
            nodes<<depth+1<<' '<<code<<' '<<q.maximum<<' '<<q.witness<<" 1\n";
            levels[depth+1]++;surpluses[surplus]++;
            if(surplus<0){nodes.flush();transitions.flush();throw std::runtime_error("ORIGINAL COUNTEREXAMPLE CANDIDATE");}
            self(self,h,q,depth+1);
        }
    };
    for(int file=first_file;file<argc;file++) {
        std::ifstream in(argv[file]);if(!in)throw std::runtime_error("input");std::string code;
        while(std::getline(in,code)) {
            Graph base(code);Subgraph g(base.n,base.edges);Profile p=analyze(g,g.n/2+2);roots++;
            nodes<<0<<' '<<code<<' '<<p.maximum<<' '<<p.witness<<' '<<p.exact<<'\n';
            if(p.exact){exact_roots++;descend(descend,g,p,0);}
            if(roots%10000==0)std::cerr<<"roots="<<roots<<" exact="<<exact_roots<<" children="<<children<<" lowerings="<<lowerings<<std::endl;
        }
    }
    std::cout<<"DONE roots="<<roots<<" exact_roots="<<exact_roots<<" children="<<children
        <<" lowerings="<<lowerings<<" neutral_moves="<<neutral_moves<<" skipped_size="<<skipped_size
        <<" skipped_limit="<<skipped_limit<<" skipped_depth="<<skipped_depth<<'\n';
    for(auto[d,c]:levels)std::cout<<"depth "<<d<<" count "<<c<<'\n';
    for(auto[s,c]:surpluses)std::cout<<"surplus "<<s<<" count "<<c<<'\n';
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}}
#endif
