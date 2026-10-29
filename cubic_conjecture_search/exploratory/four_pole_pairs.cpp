// Exhaust all port pairings of a retained profile library. Stop each case
// as soon as a nonnegative witness is found; do not claim exact optima.
#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <vector>
int main(int argc,char**argv){
 if(argc!=2)return 2;
 std::ifstream in(argv[1]);std::vector<std::array<int,81>> f;
 for(;;){std::array<int,81>a;if(!(in>>a[0]))break;
  for(int s=1;s<81;s++)if(!(in>>a[s]))return 3;f.push_back(a);}
 std::array<int,4>p{0,1,2,3};std::vector<std::vector<std::pair<int,int>>> cs;
 do{std::vector<std::pair<int,int>>v;
  for(int s=0;s<81;s++)for(int t=0;t<81;t++){
   bool ok=true;int pow[4]={1,3,9,27};
   for(int i=0;i<4;i++){int x=s/pow[i]%3,y=t/pow[p[i]]%3;
    if(!((x==0&&y<=1)||(x==1&&y==0)||(x==2&&y==2)))ok=false;}
   if(ok)v.push_back({s,t});}
  if(v.size()!=256)return 4;cs.push_back(v);
 }while(std::next_permutation(p.begin(),p.end()));
 unsigned long long checks=0;
 for(int i=0;i<int(f.size());i++)for(int j=i;j<int(f.size());j++)for(int k=0;k<24;k++){
  bool ok=false;int best=-2000000;
  for(auto[s,t]:cs[k]){int v=f[i][s]+f[j][t];best=std::max(best,v);if(v>=0){ok=true;break;}}
  checks++;if(!ok){std::cout<<"FAIL "<<i<<' '<<j<<' '<<k<<' '<<best<<'\n';return 1;}
 }
 std::cout<<"PASS profiles "<<f.size()<<" pairings "<<checks<<'\n';
}
