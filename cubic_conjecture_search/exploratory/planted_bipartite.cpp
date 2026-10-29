// Exact bounded search for good sets, with propagation of selected degrees.
// Exhausts bipartite completions of a planted cycle and a specified complement.
#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>
using namespace std;
using Mask=unsigned long long;
struct Oracle {
 int n,target; array<Mask,60>a{}; Mask full,witness=0; long long nodes=0;
 explicit Oracle(int order,int threshold):n(order),target(threshold),full((Mask(1)<<order)-1){}
 bool search(Mask yes,Mask no){
  nodes++;
  while(true){
   if(__builtin_popcountll(full&~no)<target)return false;
   Mask unknown=full&~(yes|no),add_yes=0,add_no=0;
   for(int v=0;v<n;v++){
    if(no>>v&1)continue;
    int chosen=__builtin_popcountll(a[v]&yes),free=__builtin_popcountll(a[v]&unknown);
    if(yes>>v&1){
     if(chosen>2||chosen+free<2)return false;
     if(chosen==2)add_no|=a[v]&unknown;
     else if(chosen+free==2)add_yes|=a[v]&unknown;
    }else if(chosen>2||chosen+free<2)add_no|=Mask(1)<<v;
   }
   if(add_yes&add_no)return false;
   if(!(add_yes|add_no))break;
   yes|=add_yes;no|=add_no;
  }
  Mask unknown=full&~(yes|no);
  if(__builtin_popcountll(yes)>=target){
   bool good=true;for(int v=0;v<n;v++)if((yes>>v&1)&&__builtin_popcountll(a[v]&yes)!=2){good=false;break;}
   if(good){witness=yes;return true;}
  }
  if(!unknown)return false;
  int branch=-1,best=-1;
  for(int v=0;v<n;v++)if(unknown>>v&1){
   int priority=4*__builtin_popcountll(a[v]&yes)+__builtin_popcountll(a[v]&no);
   if(priority>best){best=priority;branch=v;}
  }
  return search(yes|(Mask(1)<<branch),no)||search(yes,no|(Mask(1)<<branch));
 }
};
string encode(const Oracle&o){string code(1,char(o.n+63));int value=0,bits=0;for(int v=1;v<o.n;v++)for(int u=0;u<v;u++){value=(value<<1)|int(o.a[u]>>v&1);if(++bits==6){code+=char(value+63);bits=value=0;}}if(bits)code+=char((value<<(6-bits))+63);return code;}
void edge(Oracle&o,int u,int v){o.a[u]|=Mask(1)<<v;o.a[v]|=Mask(1)<<u;}
int main(int argc,char**argv){
 if(argc<2)return 2;
 if(string(argv[1])=="check"){
  long long count=0;for(int f=2;f<argc;f++){ifstream in(argv[f]);string line;while(getline(in,line)){
   int n=line[0]-63;if(n<1||n>26)return 2;Oracle o(n,(n+1)/2);int bit=0;
   for(int v=1;v<n;v++)for(int u=0;u<v;u++,bit++)if((line[1+bit/6]-63)&(1<<(5-bit%6)))edge(o,u,v);
   if(!o.search(0,0)){cout<<"NO_HALF "<<line<<endl;return 1;}
   for(int v=0;v<n;v++)if((o.witness>>v&1)&&__builtin_popcountll(o.a[v]&o.witness)!=2)return 3;
   count++;
  }}cout<<"VERIFIED half_witnesses="<<count<<endl;return 0;
 }
 string kind=argv[1];vector<int>lengths;for(int i=2;i<argc;i++)lengths.push_back(stoi(argv[i]));
 int t=accumulate(lengths.begin(),lengths.end(),0)-(kind=="theta"?1:0),s=t-2,n=t+s;
 if(n<8||n>40||s%2)return 2;
 Oracle base(n,n/2+1);for(int i=0;i<s;i++)edge(base,i,(i+1)%s);
 if(kind=="theta"){
  if(lengths.size()!=3||count(lengths.begin(),lengths.end(),1)>1)return 2;int next=s+2;
  for(int length:lengths){int prev=s;for(int j=1;j<length;j++){edge(base,prev,next);prev=next++;}edge(base,prev,s+1);}if(next!=n)return 2;
 }else if(kind=="barbell"){
  if(lengths.size()!=2||min(lengths[0],lengths[1])<3)return 2;int start=s;
  for(int length:lengths){for(int i=0;i<length;i++)edge(base,start+i,start+(i+1)%length);start+=length;}edge(base,s,s+lengths[0]);
 }else return 2;
 vector<int>colour(n,-1),queue={s};colour[s]=0;for(int k=0;k<(int)queue.size();k++){
  int v=queue[k];for(int u=s;u<n;u++)if(base.a[v]>>u&1){if(colour[u]<0){colour[u]=1-colour[v];queue.push_back(u);}else if(colour[u]==colour[v])return 2;}
 }
 vector<int>left,right;for(int v=s;v<n;v++)if(__builtin_popcountll(base.a[v])==2)(colour[v]?left:right).push_back(v);
 if(left.size()!=s/2||right.size()!=s/2)return 2;
 // Rotate the planted cycle so vertex 0 meets the first opposite-colour port.
 int first=left[0];left.erase(left.begin());long long graphs=0,nodes=0,max_nodes=0;
 do {auto r=right;do{
  Oracle o=base;edge(o,0,first);for(int i=0;i<(int)left.size();i++)edge(o,2*i+2,left[i]);for(int i=0;i<(int)r.size();i++)edge(o,2*i+1,r[i]);
  for(int v=0;v<n;v++)if(__builtin_popcountll(o.a[v])!=3)return 3;
  graphs++;bool found=o.search(0,0);nodes+=o.nodes;max_nodes=max(max_nodes,o.nodes);
  if(!found){cout<<"CANDIDATE_COUNTEREXAMPLE graph6="<<encode(o)<<" n="<<n<<" target="<<o.target<<" cases="<<graphs<<endl;return 1;}
  for(int v=0;v<n;v++)if((o.witness>>v&1)&&__builtin_popcountll(o.a[v]&o.witness)!=2)return 3;
  if(graphs%10000==0)cerr<<"cases="<<graphs<<" nodes="<<nodes<<endl;
 }while(next_permutation(r.begin(),r.end()));}while(next_permutation(left.begin(),left.end()));
 cout<<"DONE order="<<n<<" target="<<base.target<<" labelled_completions="<<graphs<<" search_nodes="<<nodes<<" maximum_nodes="<<max_nodes<<endl;
 return 0;
}
