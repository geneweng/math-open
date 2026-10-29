#include <algorithm>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
using namespace std;
int main(int argc,char**argv){
 long long graphs=0,edgecases=0;
 for(int fi=1;fi<argc;fi++){
  ifstream in(argv[fi]);string code;
  while(getline(in,code)){
   int n=code[0]-63,bit=0;vector<unsigned>a(n);vector<pair<int,int>>es;
   for(int v=1;v<n;v++)for(int u=0;u<v;u++,bit++)if((code[1+bit/6]-63)&(1<<(5-bit%6))){a[u]|=1u<<v;a[v]|=1u<<u;es.push_back({u,v});}
   vector<int>B(es.size(),0),A(es.size(),0);int cind=0;
   for(unsigned s=1;s<(1u<<n);s++){
    unsigned rem=s,defects=0;bool ok=true;
    while(rem){int v=__builtin_ctz(rem);rem&=rem-1;int d=__builtin_popcount(s&a[v]);
     if(d<2){ok=false;break;}if(d==3){defects|=1u<<v;if(__builtin_popcount(defects)>2){ok=false;break;}}}
    if(!ok)continue;int size=__builtin_popcount(s);
    if(!defects){cind=max(cind,size);for(int i=0;i<(int)es.size();i++){auto[u,v]=es[i];if((s>>u&1)&&(s>>v&1))A[i]=max(A[i],size);else B[i]=max(B[i],size-int(s>>u&1)-int(s>>v&1));}}
    else if(__builtin_popcount(defects)==2){int u=__builtin_ctz(defects),v=__builtin_ctz(defects&(defects-1));if(a[u]>>v&1)for(int i=0;i<(int)es.size();i++)if(es[i]==make_pair(u,v)){B[i]=max(B[i],size-2);break;}}
   }
   graphs++;
   for(int i=0;i<(int)es.size();i++){edgecases++;if(2*B[i]<n-2){cout<<"OBSTRUCTION "<<code<<" edge "<<es[i].first<<" "<<es[i].second<<" branch_maximum "<<B[i]<<" containing_edge "<<A[i]<<" cind "<<cind<<" checked "<<graphs<<endl;return 0;}}
   if(graphs%5000==0)cerr<<"graphs "<<graphs<<" edge cases "<<edgecases<<endl;
  }
 }
 cout<<"DONE graphs "<<graphs<<" edge cases "<<edgecases<<" no obstruction"<<endl;
}
