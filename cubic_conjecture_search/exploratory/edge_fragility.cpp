#define main source_main
#include "transfer_search.cpp"
#undef main
#include <sstream>
#include <random>
#include <cmath>
struct P{Mat t,del[2];string line;int n;};
int main(int argc,char**argv){
 if(argc!=2)return 2;ifstream in(argv[1]);string line;vector<P>ps;
 bool comp[3][3]={{1,1,0},{1,0,0},{0,0,1}};
 while(getline(in,line)){
  istringstream row(line);string g;array<int,4>cut,ports;row>>g;for(int&x:cut)row>>x;for(int&x:ports)row>>x;
  int n=g[0]-63,bit=0;vector<unsigned>adj(n);for(int v=1;v<n;v++)for(int u=0;u<v;u++,bit++)if((g[1+bit/6]-63)&(1<<(5-bit%6))){adj[u]|=1u<<v;adj[v]|=1u<<u;}
  for(int j=0;j<4;j+=2){adj[cut[j]]&=~(1u<<cut[j+1]);adj[cut[j+1]]&=~(1u<<cut[j]);}
  Mat local=blank();
  for(unsigned s=0;s<(1u<<n);s++){
   int states[4]={0,0,0,0};bool ok=true;unsigned rem=s;
   while(rem){int v=__builtin_ctz(rem);rem&=rem-1;int d=__builtin_popcount(adj[v]&s),p=-1;for(int j=0;j<4;j++)if(v==ports[j])p=j;
    if(p<0){if(d!=2){ok=false;break;}}else{if(d!=1&&d!=2){ok=false;break;}states[p]=3-d;}}
   if(ok)local[states[0]+3*states[1]][states[2]+3*states[3]]=max(local[states[0]+3*states[1]][states[2]+3*states[3]],2*__builtin_popcount(s)-n);
  }
  P p;p.line=line;p.n=n;p.t=blank();p.del[0]=p.del[1]=blank();
  for(int i=0;i<9;i++)for(int l=0;l<9;l++)for(int r=0;r<9;r++){
   if(comp[i%3][l%3]&&comp[i/3][l/3])p.t[i][r]=max(p.t[i][r],local[l][r]);
   if(i%3<2&&l%3<2&&comp[i/3][l/3])p.del[0][i][r]=max(p.del[0][i][r],local[l][r]);
   if(comp[i%3][l%3]&&i/3<2&&l/3<2)p.del[1][i][r]=max(p.del[1][i][r],local[l][r]);
  }
  Mat saved;for(auto&r:saved)for(int&x:r)row>>x;
  if(saved!=p.t){cerr<<"PROFILE MISMATCH"<<endl;return 2;}ps.push_back(p);
 }
 int np=ps.size(),best=100;long long tested=0;vector<int>bestword;
 auto evaluate=[&](const vector<int>&word){
  Mat tail=ps[word[1]].t;for(int i=2;i<(int)word.size();i++)tail=mul(tail,ps[word[i]].t);
  Mat prod=mul(ps[word[0]].t,tail);int result=100;
  for(int e=0;e<2;e++){
   int A=INF;for(int i=0;i<9;i++)if((e==0?i%3:i/3)==2)A=max(A,prod[i][i]);
   int B=trace(mul(ps[word[0]].del[e],tail));int score=max(2*B-2,A+B);result=min(result,score);tested++;
   if(score<best){best=score;bestword=word;cerr<<"best cap surplus="<<best<<" core surplus="<<trace(prod)<<" A="<<A<<" B="<<B<<" blocks="<<word.size()<<" tested="<<tested<<endl;}
   if(score<0){cout<<"COUNTEREXAMPLE cap_surplus="<<score<<" edge_index="<<e<<" A="<<A<<" B="<<B<<" blocks="<<word.size()<<endl;for(int j:word)cout<<ps[j].line<<endl;cout.flush();exit(0);}
  }return result;
 };
 for(int i=0;i<np;i++)for(int j=0;j<np;j++)evaluate({i,j});
 cerr<<"pairs complete "<<tested<<endl;
 if(np<=200)for(int i=0;i<np;i++)for(int j=0;j<np;j++)for(int k=0;k<np;k++)evaluate({i,j,k});
 cerr<<"triples complete "<<tested<<endl;
 mt19937 rng(20261030);
 for(int run=0;run<1000;run++){
  int len=4+rng()%13;vector<int>w(len);for(int&i:w)i=rng()%np;int value=evaluate(w);
  for(int step=0;step<1000;step++){
   int pos=rng()%len,old=w[pos];w[pos]=rng()%np;int next=evaluate(w);double temp=.1+1.5*(1.0-step/1000.0);
   if(next<=value||generate_canonical<double,32>(rng)<exp((value-next)/temp))value=next;else w[pos]=old;
   if(step%100==99){rotate(w.begin(),w.begin()+1,w.end());value=evaluate(w);}
  }
  if(run%100==99)cerr<<"runs "<<run+1<<" checked "<<tested<<" best "<<best<<endl;
 }
 cout<<"DONE edge_tests="<<tested<<" minimum_cap_surplus="<<best<<" profiles="<<np<<endl;
}
