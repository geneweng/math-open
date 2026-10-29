// Exact rooted-profile search for counterexamples to the ORIGINAL half bound.
// Joining roots of two copies of a q-vertex cap has optimum max(2B,A+B).
// Early exits certify a positive lower bound; only fully enumerated profiles
// are used for accepting a mutation or flagging a counterexample candidate.
#define TRIANGLE_PAIR_LIBRARY
#include "triangle_pair_search.cpp"
#include <cmath>
#include <map>
#include <random>

struct Profile {
    int a=-1000,b=0;U wa=0,wb=0,ca=0,cb=1;bool exact=true;
    int surplus(int n) const{return std::max(2*b,a+b)-n;}
    U multiplicity()const {
        if(2*b>a+b)return cb*cb;
        if(2*b<a+b)return 2*ca*cb;
        return cb*cb+2*ca*cb;
    }
};

Profile profile(const Subgraph&g,int root,bool stop_positive) {
    auto bs=g.basis();Profile p;U c=0;
    for(U step=1;step<(U(1)<<bs.size());step++) {
        c^=bs[__builtin_ctzll(step)];U s=0;
        for(int v=0;v<g.n;v++)if(c&g.inc[v])s|=U(1)<<v;
        int score=__builtin_popcountll(s);bool inside=s>>root&1;
        int &value=inside?p.a:p.b;U &count=inside?p.ca:p.cb;
        U &witness=inside?p.wa:p.wb;
        if(score<value)continue;
        U todo=s;bool good=true;
        while(todo){int v=__builtin_ctzll(todo);todo&=todo-1;
            if(__builtin_popcountll(g.adj[v]&s)!=2){good=false;break;}}
        if(!good)continue;
        if(score>value){value=score;count=1;witness=s;}else count++;
        if(stop_positive&&p.surplus(g.n)>0){p.exact=false;return p;}
    }
    return p;
}

std::string encode(const Subgraph&g) {
    std::string out(1,char(g.n+63));int bits=0,k=0;
    for(int v=1;v<g.n;v++)for(int u=0;u<v;u++) {
        bits=(bits<<1)|int(g.adj[u]>>v&1);k++;
        if(k==6){out+=char(bits+63);bits=k=0;}
    }
    if(k)out+=char((bits<<(6-k))+63);
    return out;
}

Subgraph decode_cap(const std::string&code,int root) {
    int n=code[0]-63,bit=0;std::vector<std::pair<int,int>>es;
    if(n<3||n>41||!(n%2)||code.size()!=std::size_t(1+(n*(n-1)/2+5)/6))throw std::runtime_error("cap graph6");
    for(unsigned char c:code)if(c<63||c>126)throw std::runtime_error("graph6 character");
    for(int v=1;v<n;v++)for(int u=0;u<v;u++,bit++)if((code[1+bit/6]-63)>>(5-bit%6)&1)es.emplace_back(u,v);
    Subgraph g(n,es);
    for(int v=0;v<n;v++)if(__builtin_popcountll(g.adj[v])!=(v==root?2:3))throw std::runtime_error("cap degrees");
    g.basis();return g;
}

bool connected(int n,const std::vector<std::pair<int,int>>&es) {
    U reached=1,previous=0;
    while(reached!=previous){previous=reached;for(auto[u,v]:es)
        if((reached>>u&1)||(reached>>v&1))reached|=(U(1)<<u)|(U(1)<<v);}
    return reached==(U(1)<<n)-1;
}

int main(int argc,char**argv) {try {
    if(argc!=5)throw std::runtime_error("usage: rooted_pair_descent INPUT(root graph6 lines) TRIALS SEED OUTPUT");
    std::ifstream in(argv[1]);std::ofstream out(argv[4]);if(!in||!out)throw std::runtime_error("file");
    int trials=std::stoi(argv[2]);std::mt19937_64 rng(std::stoull(argv[3]));
    int root;std::string code;U total=0,exact=0,accepted=0,positive=0;
    while(in>>root>>code) {
        Subgraph seed=decode_cap(code,root),current=seed,best=seed;
        Profile p=profile(seed,root,false),bp=p;
        std::cerr<<"START n="<<seed.n<<" A="<<p.a<<" B="<<p.b<<" multiplicity="<<p.multiplicity()<<std::endl;
        for(int trial=0;trial<trials;trial++) {
            if(trial%1000==0){current=seed;p=profile(seed,root,false);}
            else if(trial%1000==500){current=best;p=bp;}
            auto es=current.es;int changes=1+(rng()%10==0)+(rng()%25==0);bool altered=false;
            for(int change=0;change<changes;change++) {
                for(int attempt=0;attempt<80;attempt++) {
                    int i=rng()%es.size(),j=rng()%es.size();if(i==j)continue;
                    auto [a,b]=es[i];auto[c,d]=es[j];if(rng()%2)std::swap(c,d);
                    if(a==c||a==d||b==c||b==d)continue;
                    auto pair=[](int x,int y){return std::pair<int,int>{std::min(x,y),std::max(x,y)};};
                    std::pair<int,int>e1=pair(a,c),e2=pair(b,d);
                    bool duplicate=false;for(int k=0;k<int(es.size());k++)if(k!=i&&k!=j)
                        if(std::pair<int,int>(pair(es[k].first,es[k].second))==e1 ||
                           std::pair<int,int>(pair(es[k].first,es[k].second))==e2)duplicate=true;
                    if(duplicate)continue;
                    auto oldi=es[i],oldj=es[j];es[i]=e1;es[j]=e2;
                    if(!connected(seed.n,es)){es[i]=oldi;es[j]=oldj;continue;}
                    altered=true;break;
                }
            }
            if(!altered)continue;
            Subgraph h(seed.n,es);Profile q=profile(h,root,true);total++;
            out<<root<<' '<<encode(h)<<' '<<q.a<<' '<<q.b<<' '<<q.wa<<' '<<q.wb<<' '<<q.exact<<'\n';
            if(q.exact) {
                exact++;
                if(q.surplus(h.n)<0){out.flush();std::cout<<"ORIGINAL_COUNTEREXAMPLE_CANDIDATE n="<<2*h.n<<" cap="<<encode(h)<<" root="<<root<<" A="<<q.a<<" B="<<q.b<<std::endl;return 1;}
                if(q.surplus(h.n)<bp.surplus(h.n)||(q.surplus(h.n)==bp.surplus(h.n)&&q.multiplicity()<bp.multiplicity())) {
                    best=h;bp=q;
                    std::cerr<<"NEW_BEST n="<<h.n<<" A="<<q.a<<" B="<<q.b<<" multiplicity="<<q.multiplicity()<<std::endl;
                }
                double ratio=double(p.multiplicity()+1)/double(q.multiplicity()+1);
                if(q.surplus(h.n)<=p.surplus(h.n)&&(q.multiplicity()<=p.multiplicity()||std::generate_canonical<double,53>(rng)<std::pow(ratio,2))) {
                    current=h;p=q;accepted++;
                }
            }else positive++;
            if((trial+1)%1000==0)std::cerr<<"PROGRESS n="<<h.n<<" trial="<<trial+1<<" total="<<total<<" exact="<<exact<<" accepted="<<accepted<<std::endl;
        }
    }
    std::cout<<"DONE candidates="<<total<<" exact="<<exact<<" accepted="<<accepted<<" positive_early_exit="<<positive<<std::endl;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}}
