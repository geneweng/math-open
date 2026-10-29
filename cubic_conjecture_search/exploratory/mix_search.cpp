#define main source_main
#include "transfer_search.cpp"
#undef main
#include <sstream>
#include <random>
#include <cmath>
int main(int argc,char**argv){
 if(argc!=2)return 2;ifstream in(argv[1]);string line;vector<Mat> ms;vector<string> lines;
 while(getline(in,line)){if(line.empty())continue;lines.push_back(line);istringstream row(line);string g;int v;row>>g;for(int i=0;i<8;i++)row>>v;Mat a;for(auto&r:a)for(int&x:r)row>>x;ms.push_back(a);}
 int n=ms.size(),best=100;vector<int> wordbest;
 auto check=[&](const vector<int>&word){Mat a=ms[word[0]];for(int j=1;j<(int)word.size();j++)a=mul(a,ms[word[j]]);return trace(a);};
 auto found=[&](const vector<int>&word,int val){cout<<"COUNTEREXAMPLE deficit="<<val<<" blocks="<<word.size()<<endl;for(int i:word)cout<<lines[i]<<endl;};
 for(int i=0;i<n;i++)for(int j=0;j<=i;j++){
  int val=trace(mul(ms[i],ms[j]));if(val<best){best=val;wordbest={i,j};cerr<<"pair best "<<best<<" at "<<i<<","<<j<<endl;}
  if(val<0){found({i,j},val);return 0;}
 }
 if(n<=200)for(int i=0;i<n;i++)for(int j=0;j<n;j++){
  Mat a=mul(ms[i],ms[j]);for(int k=0;k<n;k++){int val=trace(mul(a,ms[k]));if(val<0){found({i,j,k},val);return 0;}}
 }
 cerr<<"pairs/triples done n="<<n<<endl;
 mt19937 rng(20261026);
 for(int run=0;run<1000;run++){
  int len=4+rng()%17;vector<int> word(len);for(int&i:word)i=rng()%n;int value=check(word);
  for(int step=0;step<1000;step++){
   int pos=rng()%len,old=word[pos];word[pos]=rng()%n;int next=check(word);
   double temp=0.05+1.5*(1.0-step/1000.0);
   if(next<=value||generate_canonical<double,32>(rng)<exp((value-next)/temp))value=next;else word[pos]=old;
   if(value<0){found(word,value);return 0;}
  }
  if(run%100==0)cerr<<"run="<<run<<" last="<<value<<" length="<<len<<endl;
 }
 cout<<"NO COUNTEREXAMPLE among tested words; pair minimum="<<best<<endl;
}
