#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <random>
#include <sstream>
#include <string>
#include <vector>
using namespace std;using Sig=array<int,27>;const int NEG=-1000000;
vector<array<int,3>>perms;vector<int>valid;bool comp[3][3]={{1,1,0},{1,0,0},{0,0,1}};
array<int,3> state(int k){return {k%3,k/3%3,k/9};}
Sig permute(Sig s,int p){Sig r;for(int k=0;k<27;k++){auto st=state(k);int old=0;for(int j=0;j<3;j++)old+=st[j]*(perms[p][j]==0?1:perms[p][j]==1?3:9);r[k]=s[old];}return r;}
struct Rec{Sig s;int n;bool alive=true;string description;};
struct Trip{int x,y,z,out;};vector<Trip>triples;vector<array<int,4>>kfour;
vector<Rec>records;
void save(string file){ofstream out(file);for(int i=0;i<(int)records.size();i++){auto&r=records[i];out<<i<<" "<<r.n<<" "<<r.alive<<" "<<r.description<<" |";for(int v:r.s)out<<" "<<v;out<<"\n";}}
void check(Rec r,string file){
 int closed=NEG;for(int k:valid){auto st=state(k);if(count(st.begin(),st.end(),2)==0)closed=max(closed,r.s[k]-1);else if(count(st.begin(),st.end(),0)==1)closed=max(closed,r.s[k]+1);}
 if(closed<0){records.push_back(r);save(file);cout<<"COUNTEREXAMPLE vertex_closure id="<<records.size()-1<<" surplus="<<closed<<endl;exit(0);}
 for(int root=0;root<3;root++){
  int a=NEG,b=NEG;for(int k:valid){auto st=state(k);if(count(st.begin(),st.end(),2))continue;int v=r.s[k]+2-2*(st[0]+st[1]+st[2]-st[root]);if(st[root])a=max(a,v);else b=max(b,v);}
  if(max(2*b,a+b)<0){records.push_back(r);save(file);cout<<"COUNTEREXAMPLE cap_tree id="<<records.size()-1<<" root="<<root<<" a="<<a<<" b="<<b<<endl;exit(0);}
 }
 int k4=NEG;for(auto t:kfour){bool ok=true;int v=0;for(int x:t){if(r.s[x]==NEG){ok=false;break;}v+=r.s[x];}if(ok)k4=max(k4,v);}
 if(k4<0){records.push_back(r);save(file);cout<<"COUNTEREXAMPLE K4 id="<<records.size()-1<<" surplus="<<k4<<endl;exit(0);}
}
int main(int argc,char**argv){if(argc!=3)return 2;array<int,3>p={0,1,2};do{perms.push_back(p);}while(next_permutation(p.begin(),p.end()));
 for(int k=0;k<27;k++){auto st=state(k);if(count(st.begin(),st.end(),2)%2==0)valid.push_back(k);}
 for(int x:valid)for(int y:valid)for(int z:valid){auto a=state(x),b=state(y),c=state(z);if(comp[a[2]][b[1]]&&comp[b[2]][c[1]]&&comp[c[2]][a[1]])triples.push_back({x,y,z,a[0]+3*b[0]+9*c[0]});}
 for(int x:valid)for(int y:valid)for(int z:valid)for(int w:valid){auto a=state(x),b=state(y),c=state(z),d=state(w);if(comp[a[0]][b[0]]&&comp[a[1]][c[0]]&&comp[a[2]][d[0]]&&comp[b[1]][c[1]]&&comp[b[2]][d[1]]&&comp[c[2]][d[2]])kfour.push_back({x,y,z,w});}
 ifstream in(argv[1]);string line;while(getline(in,line)){istringstream row(line);string g;int del;array<int,3>ports;row>>g>>del;for(int&v:ports)row>>v;Sig s;for(int&x:s){row>>x;if(x==-1000)x=NEG;}ostringstream meta;meta<<"BASE "<<g<<" "<<del;for(int v:ports)meta<<" "<<v;records.push_back({s,g[0]-64,true,meta.str()});}
 int base=records.size();cerr<<"base "<<base<<" triangle patterns "<<triples.size()<<" K4 patterns "<<kfour.size()<<endl;
 for(int i=0;i<base;i++)check(records[i],argv[2]);
 mt19937 rng(20261031);vector<int>active;for(int i=0;i<base;i++)active.push_back(i);
 long long tested=0,inserted=0;
 for(int iteration=0;iteration<1000000;iteration++){
  array<int,3>ids,orient;array<Sig,3>ss;int order=0;
  for(int j=0;j<3;j++){ids[j]=active[rng()%active.size()];orient[j]=rng()%6;ss[j]=permute(records[ids[j]].s,orient[j]);order+=records[ids[j]].n;}
  Sig s;s.fill(NEG);for(auto t:triples){int x=ss[0][t.x],y=ss[1][t.y],z=ss[2][t.z];if(x>NEG&&y>NEG&&z>NEG)s[t.out]=max(s[t.out],x+y+z);}
  array<Sig,6>variants;for(int p=0;p<6;p++)variants[p]=permute(s,p);int canonical=min_element(variants.begin(),variants.end())-variants.begin();
  bool dominated=false;for(int id:active){for(const auto&v:variants){bool le=true;for(int k:valid)if(records[id].s[k]>v[k]){le=false;break;}if(le){dominated=true;break;}}if(dominated)break;}
  tested++;if(!dominated){
   ostringstream meta;meta<<"TRI";for(int j=0;j<3;j++)meta<<" "<<ids[j]<<" "<<orient[j];meta<<" "<<canonical;
   Rec r{variants[canonical],order,true,meta.str()};check(r,argv[2]);vector<int>keep;
   for(int id:active){bool remove=false;for(const auto&v:variants){bool le=true;for(int k:valid)if(v[k]>records[id].s[k]){le=false;break;}if(le){remove=true;break;}}if(remove)records[id].alive=false;else keep.push_back(id);}
   keep.push_back(records.size());records.push_back(r);active.swap(keep);inserted++;cerr<<"new profile iteration="<<iteration<<" order="<<order<<" active="<<active.size()<<" total="<<records.size()<<endl;
  }
  if(iteration%100000==99999){cerr<<"tested "<<tested<<" active "<<active.size()<<" inserted "<<inserted<<endl;save(argv[2]);}
  if(active.size()>5000){cout<<"POOL_LIMIT ";break;}
 }
 save(argv[2]);cout<<"DONE tested="<<tested<<" new_profiles="<<inserted<<" active="<<active.size()<<" total="<<records.size()<<endl;
}
