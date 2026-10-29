#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <string>
#include <utility>
#include <vector>
using namespace std;
using Mat=array<array<int,9>,9>;
constexpr int INF=-1000000;
Mat blank(){Mat a;for(auto& r:a)r.fill(INF);return a;}
Mat mul(const Mat&a,const Mat&b){Mat c=blank();for(int i=0;i<9;i++)for(int j=0;j<9;j++)if(a[i][j]>INF)for(int k=0;k<9;k++)if(b[j][k]>INF)c[i][k]=max(c[i][k],a[i][j]+b[j][k]);return c;}
int trace(const Mat&a){int v=INF;for(int i=0;i<9;i++)v=max(v,a[i][i]);return v;}
int main(int argc,char**argv){
 if(argc!=2)return 2;ifstream in(argv[1]);string line;long long graphs=0,profiles=0,hard=0;
 bool comp[3][3]={{1,1,0},{1,0,0},{0,0,1}};
 bool compatible[9][9];for(int i=0;i<9;i++)for(int j=0;j<9;j++)compatible[i][j]=comp[i%3][j%3]&&comp[i/3][j/3];
 while(getline(in,line)){
  if(line.empty()||line[0]=='>')continue;int n=line[0]-63,bit=0;vector<unsigned>adj(n);vector<pair<int,int>>es;
  for(int v=1;v<n;v++)for(int u=0;u<v;u++,bit++)if((line[1+bit/6]-63)&(1<<(5-bit%6))){adj[u]|=1u<<v;adj[v]|=1u<<u;es.push_back({u,v});}
  struct Record{unsigned mask,defects,ones,threes;int size;};vector<Record> recs;
  for(unsigned s=0;s<(1u<<n);s++){
   unsigned defects=0,ones=0,threes=0;bool valid=true;
   for(int v=0;v<n;v++)if(s>>v&1){int d=__builtin_popcount(s&adj[v]);if(d==0){valid=false;break;}if(d!=2)defects|=1u<<v;if(d==1)ones|=1u<<v;if(d==3)threes|=1u<<v;}
   if(valid&&__builtin_popcount(defects)<=4)recs.push_back({s,defects,ones,threes,__builtin_popcount(s)});
  }
  for(int ei=0;ei<(int)es.size();ei++)for(int fi=ei+1;fi<(int)es.size();fi++){
   auto[a,b]=es[ei];auto[c,d]=es[fi];unsigned ports=(1u<<a)|(1u<<b)|(1u<<c)|(1u<<d);if(__builtin_popcount(ports)!=4)continue;
   int vs[4]={a,b,c,d};int base[81];fill(base,base+81,INF);
   for(const auto&r:recs){
    if(r.defects&~ports)continue;unsigned both=0;if((r.mask>>a&1)&&(r.mask>>b&1))both|=(1u<<a)|(1u<<b);if((r.mask>>c&1)&&(r.mask>>d&1))both|=(1u<<c)|(1u<<d);
    if(r.ones&both)continue;if(r.threes&~both)continue;
    int code=0,power=1;for(int j=0;j<4;j++,power*=3){int state=0;if(r.mask>>vs[j]&1){int degree=__builtin_popcount(r.mask&adj[vs[j]])-int(both>>vs[j]&1);state=degree==2?1:2;}code+=state*power;}
    base[code]=max(base[code],2*r.size-n);
   }
   int permutations[6][4]={{0,1,2,3},{0,1,3,2},{0,2,1,3},{0,2,3,1},{0,3,1,2},{0,3,2,1}};
   for(auto&p:permutations){
    profiles++;Mat local=blank();for(int code=0;code<81;code++)if(base[code]>INF){int s[4],tmp=code;for(int j=0;j<4;j++){s[j]=tmp%3;tmp/=3;}local[s[p[0]]+3*s[p[1]]][s[p[2]]+3*s[p[3]]]=base[code];}
    Mat t=blank();for(int i=0;i<9;i++)for(int l=0;l<9;l++)if(compatible[i][l])for(int r=0;r<9;r++)t[i][r]=max(t[i][r],local[l][r]);
    if(trace(t)>=0)continue;hard++;Mat power=t;
    for(int k=2;k<=15;k++){power=mul(power,t);int value=trace(power);if(value<0){cout<<"COUNTEREXAMPLE graph6="<<line<<" cut="<<a<<","<<b<<";"<<c<<","<<d<<" ports=";for(int j:p)cout<<vs[j]<<",";cout<<" blocks="<<k<<" deficit="<<value<<endl;return 0;}}
   }
  }
  graphs++;if(graphs%50==0)cerr<<"graphs="<<graphs<<" profiles="<<profiles<<" without_one_state_half_witness="<<hard<<endl;
 }
 cout<<"DONE graphs="<<graphs<<" profiles="<<profiles<<" without_one_state_half_witness="<<hard<<endl;
 return 0;
}
