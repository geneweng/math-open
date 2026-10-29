// Enumerate all nonempty vertex sets inducing a 2-regular graph.
// Input: graph6 files, restricted to graphs of order at most 26.
// Output: one line per graph, with its graph6 string and all good-set bitmasks.
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

int main(int argc, char** argv) {
    for (int f = 1; f < argc; ++f) {
        std::ifstream input(argv[f]);
        if (!input) return 2;
        std::string line;
        while (std::getline(input, line)) {
            if (line.empty() || line[0] == '>') continue;
            const int n = line[0] - 63;
            if (n < 1 || n > 26) return 3;
            const auto expected_length = static_cast<std::size_t>(1 + (n * (n - 1) / 2 + 5) / 6);
            if (line.size() != expected_length) return 3;
            std::vector<unsigned> adj(n);
            int bit = 0;
            for (int v = 1; v < n; ++v) {
                for (int u = 0; u < v; ++u, ++bit) {
                    if ((line[1 + bit / 6] - 63) & (1 << (5 - bit % 6))) {
                        adj[u] |= 1u << v;
                        adj[v] |= 1u << u;
                    }
                }
            }
            std::cout << line;
            for (unsigned mask = 1; mask < (1u << n); ++mask) {
                unsigned remaining = mask;
                bool good = true;
                while (remaining) {
                    int v = __builtin_ctz(remaining);
                    remaining &= remaining - 1;
                    if (__builtin_popcount(mask & adj[v]) != 2) {
                        good = false;
                        break;
                    }
                }
                if (good) std::cout << ' ' << mask;
            }
            std::cout << '\n';
        }
    }
}
