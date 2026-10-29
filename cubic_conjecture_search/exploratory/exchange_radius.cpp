// Exact minimum number of planted-cycle vertices deleted by an improvement.
// Input lines: graph6, planted-set bitmask. Every input is checked explicitly.
#define main planted_main
#include "planted_bipartite.cpp"
#undef main
#include <sstream>
struct Exchange:Oracle{
 Mask planted;int budget;long long limit;bool aborted=false;
 Exchange(int n,int target,Mask planted,int budget,long long limit):Oracle(n,target),planted(planted),budget(budget),limit(limit){}
 bool find(Mask yes,Mask no){
  if(aborted)return false;
  if(++nodes>limit){aborted=true;return false;}
  while(true){
   if(__builtin_popcountll(planted&no)>budget||__builtin_popcountll(full&~no)<target)return false;
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
   if(__builtin_popcountll(planted&no)==budget)add_yes|=planted&unknown;
   if(add_yes&add_no)return false;
   if(!(add_yes|add_no))break;
   yes|=add_yes;no|=add_no;
  }
  if(__builtin_popcountll(yes)>=target&&__builtin_popcountll(planted&~yes)<=budget){
   bool good=true;for(int v=0;v<n;v++)if((yes>>v&1)&&__builtin_popcountll(a[v]&yes)!=2){good=false;break;}
   if(good){witness=yes;return true;}
  }
  Mask unknown=full&~(yes|no);if(!unknown)return false;
  int branch=-1,best=-1;
  for(int v=0;v<n;v++)if(unknown>>v&1){
   int priority=4*__builtin_popcountll(a[v]&yes)+__builtin_popcountll(a[v]&no);
   if(priority>best){best=priority;branch=v;}
  }
  return find(yes|(Mask(1)<<branch),no)||find(yes,no|(Mask(1)<<branch));
 }
};
int main(int argc,char**argv){
 if(argc<2||argc>3)return 2;
 long long limit=argc==3?stoll(argv[2]):100000000;
 ifstream in(argv[1]);string line;int id=0;
 while(getline(in,line)){
  istringstream row(line);string code;Mask planted;row>>code>>planted;if(!row)return 2;
  int n=code[0]-63;if(n<4||n>58||code.size()!=1+(n*(n-1)/2+5)/6)return 2;
  int size=__builtin_popcountll(planted),target=size+1;Oracle base(n,target);int bit=0;
  for(int v=1;v<n;v++)for(int u=0;u<v;u++,bit++)if((code[1+bit/6]-63)&(1<<(5-bit%6)))edge(base,u,v);
  if(planted&~base.full||size!=n/2-1)return 3;
  int defects=0;
  for(int v=0;v<n;v++){
   if(__builtin_popcountll(base.a[v])!=3)return 3;
   int selected=__builtin_popcountll(base.a[v]&planted);
   if(planted>>v&1){if(selected!=2)return 3;}
   else{if(selected>1)return 3;defects+=selected==0;}
  }
  if(defects!=2)return 3;
  long long total=0;bool finished=false;
  for(int budget=0;budget<=size;budget++){
   Exchange o(n,target,planted,budget,limit);o.a=base.a;
   bool found=o.find(0,0);total+=o.nodes;
   if(o.aborted){cout<<"{\"case\":"<<id<<",\"status\":\"UNKNOWN\",\"failed_through\":"<<budget-1<<",\"nodes\":"<<total<<"}"<<endl;finished=true;break;}
   if(found){
    if(__builtin_popcountll(o.witness)<target||__builtin_popcountll(planted&~o.witness)!=budget)return 3;
    for(int v=0;v<n;v++)if((o.witness>>v&1)&&__builtin_popcountll(o.a[v]&o.witness)!=2)return 3;
    cout<<"{\"case\":"<<id<<",\"status\":\"OPTIMAL\",\"radius\":"<<budget
        <<",\"witness\":"<<o.witness<<",\"witness_size\":"<<__builtin_popcountll(o.witness)<<",\"nodes\":"<<total<<"}"<<endl;
    finished=true;break;
   }
  }
  if(!finished){cout<<"{\"case\":"<<id<<",\"status\":\"NO_IMPROVEMENT\",\"nodes\":"<<total<<"}"<<endl;return 1;}
  id++;
 }
}
