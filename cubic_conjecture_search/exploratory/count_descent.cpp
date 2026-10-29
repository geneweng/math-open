#define main planted_main
#include "planted_bipartite.cpp"
#undef main
#include <chrono>
#include <cmath>
#include <random>
struct Counter:Oracle{
 long long count=0,limit=100000000,node_limit=5000000;int maximum=0;bool aborted=false;
 Counter(int n,int target):Oracle(n,target){}
 void collect(Mask yes,Mask no){
  if(aborted||count>=limit)return;if(++nodes>node_limit){aborted=true;return;}
  while(true){
   if(__builtin_popcountll(full&~no)<target)return;
   Mask unknown=full&~(yes|no),add_yes=0,add_no=0;
   for(int v=0;v<n;v++){
    if(no>>v&1)continue;int chosen=__builtin_popcountll(a[v]&yes),free=__builtin_popcountll(a[v]&unknown);
    if(yes>>v&1){if(chosen>2||chosen+free<2)return;if(chosen==2)add_no|=a[v]&unknown;else if(chosen+free==2)add_yes|=a[v]&unknown;}
    else if(chosen>2||chosen+free<2)add_no|=Mask(1)<<v;
   }
   if(add_yes&add_no)return;if(!(add_yes|add_no))break;yes|=add_yes;no|=add_no;
  }
  Mask unknown=full&~(yes|no);
  if(!unknown){
   int size=__builtin_popcountll(yes);if(size<target)return;
   for(int v=0;v<n;v++)if((yes>>v&1)&&__builtin_popcountll(a[v]&yes)!=2){cerr<<"invalid witness\n";exit(3);}
   count++;maximum=max(maximum,size);witness=yes;return;
  }
  int branch=-1,best=-1;for(int v=0;v<n;v++)if(unknown>>v&1){int priority=4*__builtin_popcountll(a[v]&yes)+__builtin_popcountll(a[v]&no);if(priority>best){best=priority;branch=v;}}
  collect(yes|(Mask(1)<<branch),no);collect(yes,no|(Mask(1)<<branch));
 }
};
Oracle decode(const string&code){int n=code[0]-63;if(n<4||n>50||code.size()!=1+(n*(n-1)/2+5)/6)exit(2);Oracle o(n,(n+1)/2);int bit=0;for(int v=1;v<n;v++)for(int u=0;u<v;u++,bit++)if((code[1+bit/6]-63)&(1<<(5-bit%6)))edge(o,u,v);return o;}
bool connected(const Oracle&o){Mask seen=1,old=0;while(old!=seen){old=seen;for(int v=0;v<o.n;v++)if(seen>>v&1)seen|=o.a[v];}return seen==o.full;}
void erase_edge(Oracle&o,int u,int v){o.a[u]&=~(Mask(1)<<v);o.a[v]&=~(Mask(1)<<u);}
Counter evaluate(const Oracle&o,long long limit=100000000){Counter c(o.n,o.target);c.a=o.a;c.limit=limit;c.collect(0,0);return c;}
int main(int argc,char**argv){
 if(argc<3)return 2;
 if(string(argv[1])=="count"){
  ifstream in(argv[2]);string code;while(getline(in,code)){auto o=decode(code);auto c=evaluate(o);cout<<code<<" "<<c.count<<" "<<c.maximum<<" "<<c.aborted<<" "<<c.nodes<<"\n";}return 0;
 }
 if(argc!=7&&argc!=8)return 2;bool lex=argc==8&&string(argv[7])=="lex";ifstream in(argv[1]);string code;getline(in,code);Oracle initial=decode(code),current=initial,best_graph=initial;
 int seconds=stoi(argv[2]),seed=stoi(argv[3]);bool bipartite=string(argv[4])=="bipartite";string prefix=argv[5];long long max_steps=stoll(argv[6]);mt19937 rng(seed);
 vector<int>colour(initial.n,-1),queue={0};colour[0]=0;for(int k=0;k<(int)queue.size();k++){int v=queue[k];for(int u=0;u<initial.n;u++)if(initial.a[v]>>u&1){if(colour[u]<0){colour[u]=1-colour[v];queue.push_back(u);}else if(colour[u]==colour[v]&&bipartite)return 2;}}
 auto c=evaluate(initial);if(c.aborted||c.count>=c.limit)return 2;long long value=c.count,best=c.count,accepted=0,checked=0,incomplete=0;int best_max=c.maximum,current_max=c.maximum;
 ofstream improvements(prefix+"_improvements.txt");
 auto save=[&](long long step){ofstream out(prefix+"_best.g6");out<<encode(best_graph)<<"\n";improvements<<step<<" "<<best<<" "<<best_max<<" "<<encode(best_graph)<<endl;};save(0);
 cout<<"START n="<<initial.n<<" count="<<best<<" maximum="<<best_max<<endl;
 auto start=chrono::steady_clock::now();
 for(long long step=1;step<=max_steps;step++){
  if(chrono::duration<double>(chrono::steady_clock::now()-start).count()>seconds)break;
  if(step%10000==1){current=step%30000==1?initial:best_graph;value=step%30000==1?c.count:best;current_max=step%30000==1?c.maximum:best_max;}
  Oracle next=current;int switches=(rng()%100<85?1:(rng()%2?2:3));
  for(int sw=0;sw<switches;sw++){
   vector<pair<int,int>>es;for(int v=1;v<next.n;v++)for(int u=0;u<v;u++)if(next.a[u]>>v&1)es.push_back(bipartite&&colour[u]?make_pair(v,u):make_pair(u,v));
   for(int attempt=0;attempt<100;attempt++){
    auto[a,b]=es[rng()%es.size()];auto[d,e]=es[rng()%es.size()];if(!bipartite&&rng()%2)swap(d,e);
    if(a==d||a==e||b==d||b==e||(next.a[a]>>e&1)||(next.a[d]>>b&1))continue;
    erase_edge(next,a,b);erase_edge(next,d,e);edge(next,a,e);edge(next,d,b);break;
   }
  }
  if(!connected(next))continue;
  auto result=evaluate(next,min(100000LL,4*value+100));checked++;
  if(result.aborted||result.count>=result.limit){incomplete++;continue;}
  if((!lex&&result.count<best)||(lex&&(result.maximum<best_max||(result.maximum==best_max&&result.count<best)))){best=result.count;best_max=result.maximum;best_graph=next;save(step);cout<<"BEST step="<<step<<" count="<<best<<" maximum="<<best_max<<endl;}
  if(!result.count){cout<<"CANDIDATE_COUNTEREXAMPLE "<<encode(next)<<endl;return 1;}
  double temperature=.08+.6*(1.0-(step%10000)/10000.0);
  double improvement=log(double(value))-log(double(result.count))+(lex?20.0*(current_max-result.maximum):0.0);
  if(improvement>=0||generate_canonical<double,32>(rng)<exp(improvement/temperature)){current=next;value=result.count;current_max=result.maximum;accepted++;}
  if(step%10000==0)cout<<"PROGRESS step="<<step<<" best="<<best<<" checked="<<checked<<" incomplete="<<incomplete<<endl;
 }
 cout<<"DONE checked="<<checked<<" accepted="<<accepted<<" incomplete="<<incomplete<<" minimum_count="<<best<<" best_graph_maximum="<<best_max<<endl;
}
