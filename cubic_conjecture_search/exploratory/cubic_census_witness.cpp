// Every output line is a directly checked positive certificate. If the
// strict bound fails, exhaustively test the original half-bound as well.
#define main edge_ball_unused_main
#include "edge_ball_enumerate.cpp"
#undef main
#include <chrono>
int main(int argc,char**argv){try{
 if(argc!=3)throw std::runtime_error("usage: cubic_census_witness ORDER EXCEPTIONS");
 int n=std::stoi(argv[1]);std::ofstream exceptional(argv[2]);std::string code;
 unsigned long long count=0,sharp=0;auto start=std::chrono::steady_clock::now();
 while(std::cin>>code){Graph g(code);if(g.n!=n)throw std::runtime_error("wrong order");
  Search s{n,n/2+1,(U(1)<<n)-1,g.adjacent};
  bool strict=s.visit(0,0);
  if(!strict){s.threshold=n/2;if(!s.visit(0,0)){
    exceptional<<"COUNTEREXAMPLE_CANDIDATE "<<code<<std::endl;
    throw std::runtime_error("COUNTEREXAMPLE_CANDIDATE requires independent verification");}
   sharp++;exceptional<<"SHARP "<<code<<' '<<s.result<<std::endl;}
  if(!s.good(s.result)||__builtin_popcountll(s.result)<s.threshold)
   throw std::runtime_error("invalid positive witness");
  std::cout<<code<<' '<<s.result<<'\n';count++;
  if(count%10000==0)std::cerr<<"PROGRESS "<<count<<" sharp "<<sharp<<std::endl;
 }
 auto seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
 std::cerr<<"COMPLETE count "<<count<<" sharp "<<sharp<<" seconds "<<seconds<<std::endl;
}catch(const std::exception&e){std::cerr<<e.what()<<std::endl;return 1;}}
