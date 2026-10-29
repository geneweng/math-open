// Exhaust every labelled bipartite completion of each supplied template.
// Input: number of S-cycles, their lengths, core kind (0=theta,1=barbell),
// three core lengths, number of extra T-cycles, their lengths.
// For a barbell the lengths are (first cycle, second cycle, joining path).
#define main planted_main
#include "planted_bipartite.cpp"
#undef main
#include <chrono>
#include <sstream>

int main(int argc,char**argv){
 if(argc!=2)return 2;
 ifstream in(argv[1]);string line;int template_id=0;
 while(getline(in,line)){
  if(line.empty())continue;
  istringstream row(line);int ns,kind,p,q,r,nt;row>>ns;
  vector<int>sc(ns);for(auto&x:sc)row>>x;
  row>>kind>>p>>q>>r>>nt;vector<int>tc(nt);for(auto&x:tc)row>>x;
  if(!row||ns<1||kind<0||kind>1)return 2;
  int s=accumulate(sc.begin(),sc.end(),0);
  int t=(kind==0?p+q+r-1:p+q+r-1)+accumulate(tc.begin(),tc.end(),0),n=s+t;
  if(t!=s+2||n>40||n<6)return 2;
  Oracle base(n,(n+1)/2);int next=0;
  auto cycle=[&](int length){
   if(length<4||length%2)exit(2);
   int start=next;next+=length;
   for(int i=0;i<length;i++)edge(base,start+i,start+(i+1)%length);
  };
  for(int length:sc)cycle(length);
  if(kind==0){
   if(p<1||q<3||r<3||p%2!=1||q%2!=1||r%2!=1)return 2;
   int a=next++,b=next++;
   for(int length:{p,q,r}){int prev=a;for(int j=1;j<length;j++){edge(base,prev,next);prev=next++;}edge(base,prev,b);}
  }else{
   if(p<4||q<4||p%2||q%2||r<1||r%2!=1)return 2;
   int a=next;cycle(p);int b=next;cycle(q);int prev=a;
   for(int j=1;j<r;j++){edge(base,prev,next);prev=next++;}edge(base,prev,b);
  }
  for(int length:tc)cycle(length);if(next!=n)return 2;
  vector<int>colour(n,-1);
  for(int root=0;root<n;root++)if(colour[root]<0){
   vector<int>queue={root};colour[root]=0;
   for(int k=0;k<(int)queue.size();k++){int v=queue[k];
    for(int u=0;u<n;u++)if(base.a[v]>>u&1){
     if(colour[u]<0){colour[u]=1-colour[v];queue.push_back(u);}
     else if(colour[u]==colour[v])return 2;
    }
   }
  }
  vector<int>sl,sr,tl,tr;
  for(int v=0;v<n;v++){
   int degree=__builtin_popcountll(base.a[v]);
   if(v<s){if(degree!=2)return 2;(colour[v]?sr:sl).push_back(v);}
   else if(degree==2)(colour[v]?tr:tl).push_back(v);
   else if(degree!=3)return 2;
  }
  if(sl.size()!=tr.size()||sr.size()!=tl.size())return 2;
  // Only a single S-cycle is transitive on its colour class. With several
  // cycles, enumerate every port assignment instead of making this reduction.
  if(ns==1){edge(base,sl.front(),tr.front());sl.erase(sl.begin());tr.erase(tr.begin());}
  auto started=chrono::steady_clock::now();long long cases=0,nodes=0,max_nodes=0;
  unsigned long long digest=1469598103934665603ULL;
  do{auto second=tl;do{
   Oracle o=base;
   for(int i=0;i<(int)sl.size();i++)edge(o,sl[i],tr[i]);
   for(int i=0;i<(int)sr.size();i++)edge(o,sr[i],second[i]);
   for(int v=0;v<n;v++)if(__builtin_popcountll(o.a[v])!=3)return 3;
   bool found=o.search(0,0);cases++;nodes+=o.nodes;max_nodes=max(max_nodes,o.nodes);
   if(!found){cout<<"CANDIDATE_COUNTEREXAMPLE "<<encode(o)<<" template="<<template_id<<endl;return 1;}
   if(__builtin_popcountll(o.witness)<o.target)return 3;
   for(int v=0;v<n;v++)if((o.witness>>v&1)&&__builtin_popcountll(o.a[v]&o.witness)!=2)return 3;
   digest=(digest^o.witness)*1099511628211ULL;
  }while(next_permutation(second.begin(),second.end()));}while(next_permutation(tr.begin(),tr.end()));
  cout<<"{\"template_id\":"<<template_id++<<",\"order\":"<<n<<",\"cases\":"<<cases
      <<",\"nodes\":"<<nodes<<",\"maximum_nodes\":"<<max_nodes<<",\"witness_digest\":\""<<digest
      <<"\",\"seconds\":"<<chrono::duration<double>(chrono::steady_clock::now()-started).count()<<"}"<<endl;
 }
}
