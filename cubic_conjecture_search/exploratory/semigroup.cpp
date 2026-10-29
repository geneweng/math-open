#define main source_main
#include "transfer_search.cpp"
#undef main
#include <sstream>
#include <deque>
struct State{Mat t;vector<int>word;bool alive=true;};
bool below(const Mat&a,const Mat&b){for(int i=0;i<9;i++)for(int j=0;j<9;j++)if(a[i][j]>b[i][j])return false;return true;}
int main(int argc,char**argv){if(argc!=3)return 2;ifstream in(argv[1]);string line;vector<Mat>gens;vector<string>labels;
 while(getline(in,line)){labels.push_back(line);istringstream row(line);string s;int v;row>>s;for(int j=0;j<8;j++)row>>v;Mat t;for(auto&r:t)for(int&x:r)row>>x;gens.push_back(t);}
 vector<State>states;deque<int>queue;long long attempts=0;int active=0,processed=0,maxlen=1;
 auto insert=[&](Mat t,vector<int>w){attempts++;if(w.size()>1&&trace(t)<0){cout<<"COUNTEREXAMPLE score="<<trace(t)<<endl;for(int j:w)cout<<labels[j]<<endl;exit(0);}for(const auto&s:states)if(s.alive&&below(s.t,t))return;
 for(auto&s:states)if(s.alive&&below(t,s.t)){s.alive=false;active--;}
 states.push_back({t,w,true});queue.push_back(states.size()-1);active++;maxlen=max(maxlen,int(w.size()));};
 for(int i=0;i<(int)gens.size();i++)insert(gens[i],{i});
 while(!queue.empty()){
  int id=queue.front();queue.pop_front();if(!states[id].alive)continue;Mat t=states[id].t;auto word=states[id].word;processed++;
  for(int j=0;j<(int)gens.size();j++){auto w=word;w.push_back(j);insert(mul(t,gens[j]),w);}
  if(processed%100==0)cerr<<"processed="<<processed<<" active="<<active<<" queue="<<queue.size()<<" maxlen="<<maxlen<<" attempts="<<attempts<<endl;
  if(active>20000||processed>100000){cout<<"INCOMPLETE ";break;}
 }
 ofstream out(argv[2]);for(const auto&s:states)if(s.alive){out<<s.word.size();for(int j:s.word)out<<" "<<j;for(const auto&r:s.t)for(int x:r)out<<" "<<x;out<<"\n";}
 cout<<"states="<<active<<" attempts="<<attempts<<" closed="<<(queue.empty()?"true":"false")<<" maximum_representative_length="<<maxlen<<endl;
}
