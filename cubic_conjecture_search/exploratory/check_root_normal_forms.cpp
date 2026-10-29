// Independent verifier: direct adjacency lists and selected-neighbour counts only.
#include <vector>
#include <string>
#include <iostream>
#include <stdexcept>
#include <cstdint>
#include <algorithm>
int main(int argc,char**argv){try{if(argc!=2)throw std::runtime_error("order required");int n=std::stoi(argv[1]);std::string code;std::uint64_t graphs=0,tests=0;
 while(std::cin>>code){if(int(code[0])-63!=n||code.size()!=1+(n*(n-1)/2+5)/6)throw std::runtime_error("graph6 length");for(char c:code)if(c<63||c>126)throw std::runtime_error("char");
 std::vector<std::vector<int>> a(n);std::vector<std::pair<int,int>>es;int pos=0;
 for(int v=1;v<n;v++)for(int u=0;u<v;u++,pos++)if(((code[1+pos/6]-63)>>(5-pos%6))&1){a[u].push_back(v);a[v].push_back(u);es.emplace_back(u,v);}
 if(pos%6&&((code.back()-63)&((1<<(6-pos%6))-1)))throw std::runtime_error("padding");for(auto ns:a)if(ns.size()!=3)throw std::runtime_error("cubic");
 std::vector<bool>seen(n);std::vector<int>todo{0};seen[0]=true;for(int i=0;i<int(todo.size());i++)for(int v:a[todo[i]])if(!seen[v]){seen[v]=true;todo.push_back(v);}if(todo.size()!=n)throw std::runtime_error("disconnected");
 for(auto[u,v]:es)for(int type=0;type<2;type++){
 int q=n+(type?3:1),r=q-1;auto b=a;b.resize(q);b[u].erase(std::find(b[u].begin(),b[u].end(),v));b[v].erase(std::find(b[v].begin(),b[v].end(),u));
 auto join=[&](int x,int y){b[x].push_back(y);b[y].push_back(x);};
 if(type){join(u,n);join(n,n+1);join(n+1,v);join(n,r);join(n+1,r);}else{join(u,r);join(v,r);}
 for(int i=0;i<q;i++)if(b[i].size()!=(i==r?2:3))throw std::runtime_error("fragment degrees");
 std::uint64_t out,in;if(!(std::cin>>out>>in))throw std::runtime_error("missing masks");
 auto check=[&](std::uint64_t s){if(s>>q)throw std::runtime_error("mask range");int k=0;for(int x=0;x<q;x++)if(s>>x&1){k++;int d=0;for(int y:b[x])d+=int(s>>y&1);if(d!=2)throw std::runtime_error("induced degree");}return k;};
 if(out>>r&1)throw std::runtime_error("root out");int B=check(out);
 if(in){if(!(in>>r&1))throw std::runtime_error("root in");if(B+check(in)<q)throw std::runtime_error("sum too small");}
 else if(2*B<q)throw std::runtime_error("double out too small");tests++;
 }graphs++;
 }
 std::cout<<"GRAPHS "<<graphs<<" TESTS "<<tests<<'\n';
}catch(const std::exception&e){std::cerr<<e.what()<<std::endl;return 1;}}
