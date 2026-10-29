// Direct search for an ORIGINAL cubic counterexample. Size first, then the
// number of maximum good sets. Exact cycle-space enumeration is used for
// accepted moves; early exits supply only positive lower-bound witnesses.
#define TRIANGLE_PAIR_LIBRARY
#include "triangle_pair_search.cpp"
#include <cmath>
#include <random>
#include <tuple>

struct Result {int size=0;U count=1,witness=0;bool exact=true;};
Result evaluate(const Subgraph&g,int ceiling=1000) {
    auto bs=g.basis();U f=0;Result r;
    for(U t=1;t<(U(1)<<bs.size());t++) {
        f^=bs[__builtin_ctzll(t)];U s=0;
        for(int v=0;v<g.n;v++)if(f&g.inc[v])s|=U(1)<<v;
        int size=__builtin_popcountll(s);if(size<r.size)continue;
        bool valid=true;U todo=s;
        while(todo){int v=__builtin_ctzll(todo);todo&=todo-1;
            if(__builtin_popcountll(g.adj[v]&s)!=2){valid=false;break;}}
        if(!valid)continue;
        if(size>r.size){r.size=size;r.count=1;r.witness=s;}else r.count++;
        if(r.size>ceiling){r.exact=false;return r;}
    }
    return r;
}

std::string encode(const Subgraph&g) {
    std::string out(1,char(g.n+63));int bits=0,k=0;
    for(int v=1;v<g.n;v++)for(int u=0;u<v;u++) {
        bits=(bits<<1)|int(g.adj[u]>>v&1);k++;
        if(k==6){out+=char(bits+63);bits=k=0;}
    }
    if(k)out+=char((bits<<(6-k))+63);return out;
}

bool connected(int n,const std::vector<std::pair<int,int>>&es) {
    U reached=1,previous=0;
    while(reached!=previous){previous=reached;for(auto[u,v]:es)
        if((reached>>u&1)||(reached>>v&1))reached|=(U(1)<<u)|(U(1)<<v);}
    return reached==(U(1)<<n)-1;
}

Subgraph expand_vertex(const Subgraph&g,int v) {
    std::vector<int>ns;for(int u=0;u<g.n;u++)if(g.adj[v]>>u&1)ns.push_back(u);
    auto es=g.es;int p=g.n,q=p+1;
    for(auto &e:es) {
        if(e==std::pair<int,int>{v,ns[1]}||e==std::pair<int,int>{ns[1],v})e={p,ns[1]};
        else if(e==std::pair<int,int>{v,ns[2]}||e==std::pair<int,int>{ns[2],v})e={q,ns[2]};
    }
    es.emplace_back(v,p);es.emplace_back(p,q);es.emplace_back(q,v);
    return Subgraph(g.n+2,es);
}

int main(int argc,char**argv){try {
    if(argc!=5)throw std::runtime_error("usage: cubic_multiplicity_descent INPUT.g6 TRIALS SEED OUTPUT_PREFIX");
    std::ifstream in(argv[1]);if(!in)throw std::runtime_error("input");
    int trials=std::stoi(argv[2]);std::mt19937_64 rng(std::stoull(argv[3]));
    std::string prefix=argv[4];std::ofstream out(prefix+"_candidates.txt"),bestout(prefix+"_best.txt");
    auto save=[&](std::ostream&s,const Subgraph&g,const Result&r){s<<encode(g)<<' '<<r.size<<' '<<r.count<<' '<<r.witness<<' '<<r.exact<<'\n';};
    std::vector<Subgraph>seeds;std::string code;
    while(in>>code){Graph base(code);Subgraph g(base.n,base.edges);seeds.push_back(g);
        while(g.n<32){Subgraph next=expand_vertex(g,0);Result bp=evaluate(next);
            for(int v=1;v<g.n;v++){Subgraph h=expand_vertex(g,v);Result p=evaluate(h);
                save(out,h,p);if(std::tie(p.size,p.count)<std::tie(bp.size,bp.count)){next=h;bp=p;}}
            g=next;seeds.push_back(g);}}
    U proposals=0,exact=0,accepted=0;
    for(const auto&seed:seeds) {
        Subgraph current=seed,best=seed;Result p=evaluate(seed),bp=p;save(bestout,best,bp);
        std::cerr<<"START n="<<seed.n<<" maximum="<<p.size<<" count="<<p.count<<std::endl;
        for(int step=0;step<trials;step++) {
            if(step%1000==0){current=seed;p=evaluate(seed);}
            else if(step%1000==500){current=best;p=bp;}
            auto es=current.es;bool changed=false;
            int switches=1+(rng()%5==0)+(rng()%20==0);
            for(int move=0;move<switches;move++)for(int attempt=0;attempt<80;attempt++) {
                int i=rng()%es.size(),j=rng()%es.size();if(i==j)continue;
                auto[a,b]=es[i];auto[c,d]=es[j];if(rng()%2)std::swap(c,d);
                if(a==c||a==d||b==c||b==d)continue;
                auto pair=[](int u,int v){return std::pair<int,int>{std::min(u,v),std::max(u,v)};};
                auto x=pair(a,c),y=pair(b,d);bool duplicate=false;
                for(int k=0;k<int(es.size());k++)if(k!=i&&k!=j)
                    if(pair(es[k].first,es[k].second)==x||pair(es[k].first,es[k].second)==y)duplicate=true;
                if(duplicate)continue;
                auto oldi=es[i],oldj=es[j];es[i]=x;es[j]=y;
                if(!connected(seed.n,es)){es[i]=oldi;es[j]=oldj;continue;}
                changed=true;break;
            }
            if(!changed)continue;
            Subgraph h(seed.n,es);Result q=evaluate(h,p.size+(rng()%10==0));
            proposals++;save(out,h,q);
            if(q.exact){exact++;
                if(q.size<h.n/2){out.flush();save(bestout,h,q);bestout.flush();
                    std::cout<<"ORIGINAL_COUNTEREXAMPLE_CANDIDATE "<<encode(h)<<std::endl;return 1;}
                if(std::tie(q.size,q.count)<std::tie(bp.size,bp.count)) {
                    best=h;bp=q;save(bestout,h,q);bestout.flush();
                    std::cerr<<"BEST n="<<h.n<<" maximum="<<q.size<<" count="<<q.count<<std::endl;}
                double ratio=double(p.count+1)/double(q.count+1);
                bool accept=q.size<p.size||(q.size==p.size&&(q.count<=p.count||std::generate_canonical<double,53>(rng)<std::pow(ratio,2)))
                    ||(q.size==p.size+1&&std::generate_canonical<double,53>(rng)<0.01);
                if(accept){current=h;p=q;accepted++;}
            }
        }
        std::cerr<<"END n="<<seed.n<<" best="<<bp.size<<" count="<<bp.count<<" proposals="<<proposals<<std::endl;
    }
    std::cout<<"DONE seeds="<<seeds.size()<<" proposals="<<proposals<<" exact="<<exact<<" accepted="<<accepted<<std::endl;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}}
