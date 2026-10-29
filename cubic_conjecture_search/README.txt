INDUCED CYCLES CONJECTURE: RESEARCH RECORD
October 29, 2026

Status
======
The general conjecture has NOT been proved or disproved in this work.
No counterexample to the original conjecture was found. This directory contains finite certificates
and reproducible search programs, not a claimed solution.

Latest continuation: direct bipartite counterexample synthesis
============================================================
See direct_bipartite/RESULTS.txt. A direct connected cubic bipartite search
at order 26, with no seed-distance restriction, rejected 11 proposals.
Independent enumeration gives optimum 18 for every one, the largest
possible in this class; a counterexample would require optimum at most 12.
The run ended at its time guard. No infeasibility or new exhaustive bound
is claimed, and the original conjecture remains unresolved.

Previous continuation: explicit limits of the profile conditions
=============================================================
See profile_scope/RESULTS.txt. The ten-profile condition is NOT universal:
an explicit 62-vertex cubic parent yields a realizable profile outside it.
Two successive 15-profile extensions also have explicit failures. All
three graphs satisfy the original half bound. The earlier conditional
assembly theorems remain valid; universal versions of those conditions
must not be assumed.

A targeted exhaustive scan of 23,326 small weighted cores produced
positive certificates for their completed cubic parents and for both
rooted tests at all 437,518 core edges. Independent witness verification
passed. A final 16-profile closure also proves the half bound for arbitrary
ring assemblies of these pieces. This does not cover all cubic graphs;
the original conjecture remains unresolved. The paper/PDF is unchanged.

Previous continuation: complete finite closure for ring assemblies
===============================================================
See ring_closure/RESULTS.txt. A ten-vector boundary-profile condition is
closed under series composition, as independently verified for all 100
ordered basis pairs. Induction proves the original half bound for arbitrary
ring assemblies from pieces satisfying this condition. The 27 retained
two-port pieces, completed theta/cycle families, and the disjoint P13 pair
are covered. This is a complete finite-certificate induction, not a search
timeout or an extrapolation from bounded ring lengths.

A 30-vertex completed diamond also refutes the stronger vertex-deletion
claim: c_ind(G)=16 but c_ind(G-v)=14 for a specified vertex. It satisfies
the original half bound. The profile condition has not been proved for
all cubic graphs, so the original conjecture remains unresolved.

Previous continuation: endpoint information at two-edge cuts
==========================================================
See two_cut_audit/RESULTS.txt. An exact five-state composition law shows
why U,T,W alone cannot determine general two-edge joins. A verified
18-vertex piece yields rings with c_ind=11k-2t on 18k vertices, where t
counts preferred-port/preferred-port joins. Uniform and alternating
orientations (even k) differ by k despite identical local aggregate data.
Both satisfy the original bound. This is an infinite-family theorem and
a limitation of profile compression, not a solution of the conjecture.

Previous continuation: direct edge-profile exclusions
==================================================
See edge_tradeoff/RESULTS.txt. Explicit certificates exclude both rooted
constructions at all 35,388 edges of the 983 labelled connected single-
switch neighbours of the retained sharp 24-vertex graph. This is a
specified local neighbourhood, not a census of cubic graphs of order 24.

A two-edge-cut composition lemma and exact local path certificates show
that every bridge bypass formed from two P13 caps has a good set of at
least 16 vertices out of 28. This closes that targeted construction too.
The general U,T,W tradeoff is not proved, the original conjecture remains
unresolved, and the paper/PDF is unchanged.

Previous continuation: finite covers and the descent obstruction
=============================================================
See cover_audit/RESULTS.txt. All 127 connected signed two-sheeted covers
of Franklin were checked by independent cycle-space enumeration. The six
sharp assignments yield only the previously known 24-vertex type.

Pullback certificates exclude both rooted constructions throughout the
family of finite Franklin covers. An explicit common-cover construction
also shows that EVERY connected cubic graph has a cover of degree at
most 12 with those certificates. Consequently cover existence alone is
no restriction on a possible counterexample. A cube-to-K4 example checks
why simply projecting a good half-set is invalid. This is a limitation
of this strategy, not a proof or disproof of the original conjecture.
The main paper/PDF is unchanged.

Previous review: extremal-library audit and revised proof target
============================================================
See extremal_audit/REVIEW.txt and its reproducible certificates. The 101
retained equality parents have only eight isomorphism types. Their traced
decompositions use Franklin cores and bridge-attached triangles only.
This does not classify equality graphs in general.

A certificate theorem, supported by 418 independently checked half-sized
edge witnesses and eight complementary good partitions, excludes BOTH
rooted constructions at every edge of these retained parents. A proposed
universal near-sharp edge-coverage lemma fails on two 14-vertex graphs;
all four failing edges instead have large edge-deletion gain. The revised
target is a joint U,T,W inequality, not further duplication of this library.
The general conjecture remains unresolved. The main paper/PDF is unchanged.

Previous continuation: non-bridge edge and exact parent target (round 34)
====================================================================
The original conjecture remains unresolved. Section 27 proves that the
distinguished edge in either minimum rooted obstruction normal form cannot
be a bridge. Other edges in the cubic parent may still be bridges.

For a parent of order 2h and distinguished edge uv, write
U=c_ind(G-uv), T=max size of a good set containing u,v in G, and
W=c_ind(G-{u,v}). A minimum triangle-form rooted obstruction must satisfy
    U=h+1, T<=h-1, W<=h-2.
These three conditions would also suffice to construct an original
counterexample by doubling the rooted triangle replacement. Every good
set of the parent of size at least h would separate u,v. A bipartite
parent in this minimum triangle form must have order 2 modulo 4.
These are necessary restrictions and a conditional construction, not
an existence proof or a proof that no such parent exists.

A bounded CEGIS search targeted a 25-vertex root profile A<=12, B<=13,
C<=10 near one sharp-parent seed, with at most six seed edges removed.
Such a graph would give a counterexample on 54 vertices after root
expansion and doubling. It reached its between-iteration time limit
after 407.4 seconds, with 12 candidates and 1919 cuts (160 initial).
The labelled search neighbourhood was not exhausted. Independent
cycle-space enumeration of all 8192 vectors per candidate confirms
no counterexample among the 12 records, either before or after expansion.
The minimum doubled optima are 30/50 and 32/54 respectively.

Source: exploratory/root_triangle_synthesis.py.
Data: round34_data/seed.json and round34_data/synthesis.json.
Verifier: verify_round34.py (small exhaustive formulas); add --search
for independent exact cycle-space audits, seed-profile checks, candidate
connectivity and edge-distance checks, and validation of all recorded
cut witnesses. Formula checks cover all 369 parent-edge cases through
order ten, including the bridge case. Results are stored in
round34_formula_verification.json and round34_search_verification.json.
The established general counterexample lower bound remains 24 vertices;
for connected counterexamples with a bridge it remains 30 vertices.

Previous continuation: rooted obstruction normal form (round 33)
=============================================================
The original conjecture remains unresolved. Section 26 proves an
arbitrary-order reduction: a minimum-order rooted fragment whose symmetric
double violates half is either an edge subdivision of a connected simple
cubic graph, or the result of replacing one edge by a rooted triangle.
Bridge symmetrization makes these two forms sufficient for existence
searches for bridged counterexamples. This does not resolve either form
at arbitrary orders or address all bridgeless graphs.

For root-in, root-out, and closed-root-neighbourhood-avoiding optima
(A,B,C), root triangle expansion has the exact map
    (A,B,C) -> (C+3, max(B,A+1), B).
Two consecutive expansions preserve the doubled half bound, by parity.
A diamond termination and its single expansion also preserve it. These
facts prove the normal form. For a non-obstructing rooted graph of order
2h+1, one expansion fails exactly when B=h+1, A<=h, and C<=h-2.
No graph realizing a counterexample profile was found.

All 33,079,650 canonical rooted tests over the 556,471 connected cubic
parents through order 20 have independently checked positive certificates.
The unchanged round-32 certificates cover edge subdivisions of every
order-22 parent. The normal form therefore excludes every rooted
obstruction of order at most 23, including roots lying in triangles.
Consequences: every connected bridged cubic counterexample has at least
30 vertices; every 46-vertex cubic graph with a bridge splitting it into
two 23-vertex components satisfies half, without a triangle restriction.
The general counterexample lower bound remains 24 vertices.

Source: exploratory/root_normal_forms.cpp; runner:
exploratory/run_root_normal_forms.py. Independent checker:
exploratory/check_root_normal_forms.cpp. Verifier: verify_round33.py.
Run the verifier with --formulas for independent exhaustive checks on
84 small rooted inputs (all four profile transformations and the exact
single-expansion failure criterion). Without arguments it verifies all
canonical certificates and hashes of the inherited round-32 data.
Data: round33_data/. Results: round33_verification.json and
round33_formula_verification.json. Enumeration completeness relies on
nauty geng; positive masks are checked independently of the search.

Previous continuation: edge-boundary certificates (round 32)
========================================================
The original conjecture remains unresolved. Section 25 proves a sufficient
boundary criterion: if a cubic graph of order 2h has a good set S of size
c >= h+1 and every selected edge e has a good set of size at least 2h-c
in G-e, every symmetric double of an edge subdivision meets the half bound.
Bridge symmetrization then covers any mixed join of certified fragments.
The boundary hypothesis has not been proved universally.

The criterion passes for the retained witness in every one of the 7,319,447
connected simple cubic graphs of order 22. All 241,541,751 parent-edge
records are covered: 95,430,602 require new deletion masks; 146,111,149
reuse the original mask with the subdivision root omitted. A separate
C++ checker validates all new masks; the Python driver matches every
parent row exactly to the independently verified round-30 census.
Completeness inherits the nauty census assumptions from that round.

Consequently every bridge join of two connected 23-vertex rooted fragments
with nonadjacent root neighbours satisfies the half bound on 46 vertices.
The root is the unique degree-two vertex; all other vertices have degree
three. This covers symmetric and mixed joins, not all order-46 cubic graphs.
Adjacent root neighbours and arbitrary larger orders remain outside this
finite result. Direct whole-graph checks also validate 2,048 mixed joins.

Producer: exploratory/edge_half_certificates.cpp.
Runner: exploratory/run_edge_half_census.py (uses the saved round-30 inputs).
Independent checker: exploratory/check_edge_half.cpp.
Verifier: verify_round32.py. Retained data: round32_data/.
Records: round32_verification.json, round32_mixed_verification.json.
Compile the producer with clang++ -O3 -std=c++17 into tmp/cubic_round32/edge_half
before running the generator. The verifier compiles its own checker.

Previous continuation: unbounded extension loss (round 31)
======================================================
The original conjecture remains unresolved. A single two-edge extension
can decrease c_ind by an arbitrarily large amount. Section 24 proves this
for an explicit family: |G_k|=16k, c_ind(G_k)=12k; its extension has
order 16k+2 and c_ind=11k+2. The loss is k-2. The extended graph still
has surplus 3k+1 over the original half bound, so it is not a counterexample.

The construction attaches subdivided triangular prisms to a cycle.
Each seven-vertex attachment has exact maximum five, attained both with
and without its root. Bridge separation reduces the exact optimum to
that of the cycle or extended theta core. This also proves a completion
formula c_ind(N(H))=5D+c_ind(H) for any subcubic H with D missing incidences.
This completion preserves the unweighted optimum up to an additive
constant; it does not preserve the surplus over half.

verify_round31.py independently checks the attachment, all subsets of
two smaller before/after pairs (orders 12/14 and 16/18), 64 theta cores,
and explicit whole-graph witnesses for k=2,...,100. Exact smaller optima
fall from 9 to 8 and from 12 to 10. The infinite-family upper bounds have
an analytic proof and do not rely on extrapolation from finite checks.

exploratory/extension_monotonicity.cpp performs exact searches over
edge extensions. Its retained scan outputs are exploratory search data;
only the two selected examples are independently exhaustively checked
by verify_round31.py. See round31_verification.json for reproducible results.

Previous continuation: complete order-22 census (round 30)
======================================================
The original conjecture remains unresolved. Every one of the 7,319,447
connected simple cubic graphs on 22 vertices has a retained good-set
witness of size at least 12. All witnesses were independently checked
for cubicity, connectivity, selected size, and induced degree two.
A separate exhaustive check of all 2^22 vertex subsets of one example
proves its optimum is exactly 12. Thus the exact minimum at order 22
is 12. Together with earlier checks, any original counterexample has
at least 24 vertices. This is a finite computational result.

Generation: nauty 2.9.3 geng -c -d3 -D3 -X0 -x3200 22 r/64, all 64
residues. Per-shard generator, search and independent checker counts
agree; the total agrees with the House of Graphs census. Completeness
relies on geng's isomorph-free generation and residue partitioning.
The positive witnesses are separately checkable without trusting the
search algorithm. Compressed certificates and hashes are retained.

Also proved an exact four-case formula for subdividing two disjoint
edges and joining their new vertices. Every such extension of 101
retained sharp parent records has a positive half-bound witness:
182,679 indexed constructions of orders 14 through 60. The formula
was independently checked on all 1,674 eligible cases through order 10.
Repeated constructions are possible; this extension family is not an
exhaustive census at those larger orders.

Sources: exploratory/cubic_census_witness.cpp,
exploratory/check_cubic_census.cpp, exploratory/run_cubic22_census.py,
exploratory/two_edge_extension.cpp, verify_round30_census.py,
verify_round30_extensions.py, verify_round30_minimum.py.
Data: round30_data/. Verification records: round30_census_verification.json,
round30_extension_verification.json, round30_minimum_verification.json.
The general conjecture is neither proved nor disproved.

Previous continuation: mixed assembly criterion (round 29)
=======================================================
The original conjecture remains unresolved. Section 22.2 combines the
closed-port and open-port assembly theorems. A subgraph F of the joining
multigraph must have degree zero or two at every vertex. Degree-zero
pieces use the closed criterion; degree-two pieces use the open criterion.
A single Hall matching assigns all remaining selected ports. This is a
sufficient condition and does not assert that every mixture admits F.

In particular, all K5 assemblies with three or four designated open-type
pieces are covered by taking a cycle through them. One or two open-type
pieces are not covered by this choice. The verifier constructs and checks
1,000 mixed examples of orders 44 through 60 using pieces satisfying only
their designated criterion.

A counterexample-guided search on K5, using ten closed-type and ten
open-type profiles in all 24 port orders, reached a 120.7-second wall
limit after 78 solver queries and 41 positive witness cuts. All witnesses
are independently checked. The remaining domain is NOT proved infeasible.

A separate exhaustive test uses just a four-cycle piece and the 8-vertex
piece from graph6 I?BeeOwM? with vertices 2 and 5 removed. For one or two
four-cycle pieces on K5, all 486 distinct indexed boundary-profile
assignments have direct good-set witnesses with doubled surplus at least
10. Orders are 32 or 36. The 486 count includes possible repeated graphs;
it is complete only for these two fragment types and this joining graph.

Sources: verify_round29.py, exploratory/mixed_four_pole_synthesis.py,
exploratory/mixed_k5_exhaust.py. Data: round29_data/; verification results:
round29_verification.json. A universal reduction or a counterexample to
the original conjecture is still missing.

Previous continuation: open-port assemblies and cyclic search (round 28)
====================================================================
The original conjecture remains unresolved. Section 22 proves another
arbitrary-assembly criterion. For every pair of ports, a fragment must
have a half-sized solution opening that pair and either avoiding both
other ports, or permitting either other port alone to be selected closed.
A 2-factor chooses the open joining edges. Hall's theorem assigns any
required extra closed ports along the complementary edges. The selected
local sets then give a whole-graph good set meeting the half-bound.

Of the broader round-27 library, 5,552 fragments satisfy this criterion.
Arbitrary assemblies made only from these pieces are covered. This does
not justify arbitrary mixtures with pieces satisfying only round 26's
closed-port criterion. Twenty-one explicit assembled-graph certificates
were checked, including one using all 5,552 pieces (65,380 vertices).

A separate coordinate-descent search considered cyclic assemblies with
two joining edges between consecutive fragments, at lengths 3,4,5,6,8,
12,20,40. Each coordinate update scans 29,736 indexed profile/orientation
choices. There were 43,711,920 coordinate evaluations and 1,470 retained
records. This is not exhaustive over all cyclic words. Independent DP
and direct graph-degree checks verify every retained good set (orders
12 through 470). No counterexample was found. All eight zero-surplus
words are independently certified relabellings of the Franklin graph.

Sources: exploratory/four_pole_cycle_search.py, verify_round28.py,
verify_round28_assembly.py, exploratory/check_cycle_sharp.py.
Data: round28_data/; results: round28_verification.json and
round28_assembly_verification.json. The general existence gap remains.

Previous continuation: four-port contraction and broader joins (round 27)
=====================================================================
The original conjecture remains unresolved. Section 21 proves a local
contraction criterion: replace an induced four-port fragment by two
adjacent vertices, with two attachments at each. If the contracted graph
is simple cubic and the three explicit boundary conditions hold, every
good set lifts with gain at least (q-2)/2. A smallest counterexample
cannot contain such a reducible fragment. No proof is given that every
cubic graph contains one.

Of the 2,214 previous fragments, 1,945 pass the criterion in their
inherited port pairing. All 19,450 lifts from the K3,3 exterior model
are independently checked. This finite check supports the implementation;
the general lifting proof is by the four possible endpoint selections.

A broader direct search generates 9,492 four-port fragments from all
621 connected cubic graphs through order 14. It reduces 7,144 labelled
profiles to 2,054 up to port permutations, then retains 1,239 profiles
under domination. All 18,436,320 retained pairings with repetition and
all 24 orientations have a nonnegative witness. Thus all two-piece joins
from this library satisfy the bound (orders 8 through 24). Counts are
indexed constructions, not distinct graphs. Larger assemblies are not
covered by this finite pair result.

verify_round27.py checks all 210,400 local witnesses, every profile
domination, and all pairings using an independent bitset method. It uses
NumPy solely for exact integer componentwise comparisons. Large-profile
upper bounds are neither independently verified nor needed for this
positive result. Data: round27_data/; results: round27_verification.json.

Previous continuation: arbitrary four-port assemblies (round 26)
=============================================================
The original conjecture remains unresolved. A new sufficient condition
proves the half-bound for arbitrary mixtures of four-port fragments:
each fragment must have either a half-sized closed good set avoiding
all ports, or such a set selecting exactly any prescribed pair of ports.
Hall's theorem assigns two joining edges to each fragment requiring the
second option, with no edge assigned twice. The local sets then combine
without selected endpoints across any joining edge.

All 2,214 eligible adjacent-vertex deletions from 56 saved sharp cubic
examples satisfy this criterion: 1,643 avoid all ports and the remaining
571 allow every pair. The source examples are Franklin, the five saved
sharp examples on 24/26/36/38/42 vertices, and 50 symmetric doubles of
13-vertex caps. Counts are labelled records, not nonisomorphic counts.
Arbitrary repetition, orientation, and number of these pieces is covered.
This does not cover arbitrary four-port fragments or all cubic graphs.

verify_round26.py checks 44,154 local witnesses directly; it also checks
all 252 eligible profiles from cubic graphs through order 10 against
exhaustive vertex-subset enumeration. The large profiles' upper bounds
are not independently verified or used for the positive theorem.
It constructs and directly checks 41 whole-graph assemblies, including
one using every retained piece (54,996 vertices). These examples check
the implementation; the arbitrary-size conclusion follows from the proof.
Data: round26_data/ and round26_verification.json. Paper: Section 20.

Previous continuation: barriers with only a total edge bound (round 25)
===================================================================
The original conjecture remains unresolved. Removing the pseudoforest
constraint does not rescue bounded-defect repair by simple-cycle exchanges.
For the sharp family B_k, every repair of M_k through arbitrary odd factors
with at most n edges has peak isolated-edge count at least
1 + ceil((k-1)/4). A known repair has peak k. This is an unbounded barrier
in a larger state space, not a counterexample to the original conjecture.

The proof is entirely mathematical: a cap restriction with cost w has at
least 13-4w edges. The first core-cycle exchange adds k edges and forces
at least k-1 edges of prior savings. The local coefficient four is sharp;
no claim is made that the resulting global lower bound is exact.

verify_round25.py exhausts all 524,288 cap edge subsets (128 parity states),
checks the local bound and root-avoiding maximum, and directly checks the
explicit repairs for k=3,...,40. Results: round25_verification.json.

Previous continuation: direct triangle-obstruction searches (round 24)
==================================================================
The original conjecture remains unresolved. Every single-vertex triangle
expansion of every parent in the two round-20 radius-four edge regions
satisfies the half-bound. There are 4,872,232 parent reconnection records
and 122,729,334 indexed expansions, INCLUDING DUPLICATE CONSTRUCTIONS.
These are not counts of distinct labelled or nonisomorphic graphs.

The algorithm checks strict parent witnesses or a collection of half-bound
witnesses covering every vertex. It retained 5,656 new strict witnesses
and 76 half witnesses. All 5,732 are independently degree-checked, along
with 142,886 explicit lifts. No direct expanded-graph fallback was needed.
The large regions are not independently regenerated; generation is the
round-20 reconnection method, separately tested at orders 6 and 8.

Broader CEGIS searches target expanded counterexamples directly, with
parent orders 24/26, a fixed expanded vertex neighbourhood, and radius 6.
They produced 8/6 candidates and stopped at wall-time limits after
1,821/1,907 constraints. Independent cycle-space enumeration verifies
candidate optima and large-set counts, and positive bounds for the parents.
Timeouts remain inconclusive. All 1,134 two-port joins of the 14-vertex
critical-star example to the old 27-profile library have doubled surplus
at least 2, so none yields a sharp graph or original counterexample.

Reproduce from the repository root:
  mkdir -p tmp/cubic_round24
  clang++ -O3 -std=c++17 cubic_conjecture_search/exploratory/triangle_edge_ball.cpp -o tmp/cubic_round24/triangle_edge_ball
  tmp/cubic_round24/triangle_edge_ball cubic_conjecture_search/round20_data/seed24.g6 cubic_conjecture_search/round20_data/seed24_masks.txt 4 cubic_conjecture_search/round24_data/ball24
  tmp/cubic_round24/triangle_edge_ball cubic_conjecture_search/round20_data/seed26.g6 cubic_conjecture_search/round20_data/seed26_masks.txt 4 cubic_conjecture_search/round24_data/ball26
  python3 cubic_conjecture_search/verify_round24.py
Data and results: round24_data and round24_verification.json.

Latest continuation: triangle obstruction reduction (round 23)
============================================================
The original conjecture remains unresolved. For a cubic G of order 2h,
let B_v maximize good sets avoiding v, C_v maximize those avoiding N[v],
and D_v maximize good sets containing v after deleting one incident edge.
The exact vertex-triangle expansion value is max(B_v,C_v+3,D_v+1).
If G satisfies the half-bound, its expansion fails precisely when
B_v=h, D_v<=h-1, C_v<=h-3. Then G is sharp and v occurs in no maximum
good set. For EVERY incident edge, subdividing once and doubling at the
root gives an original cubic counterexample of order 4h+2, optimum 2h.
This is a conditional reduction; no instance of its obstruction was found.

Complementary good-set partitions were directly verified for 100 prior
sharp records (five cubic records and 95 doubled rooted records), orders
24 through 58. All 3,932 single-vertex expansions receive explicit lifts.
This does not prove a partition theorem for all sharp graphs or safety
under repeated expansions. The exact expansion identity was independently
checked for all 246 expansions of connected cubic graphs through order 10.

The auxiliary assertion that all three edges at a cubic vertex cannot be
deletion-critical is false. Graph M???FBOq@KF?D_B_? has order 14 and
c_ind=8, while deleting any edge at vertex 2 gives c_ind=10. Independent
subset enumeration checks the optima. This graph satisfies the original
bound and is NOT a counterexample to it.

Reproduce:
  python3 cubic_conjecture_search/exploratory/triangle_obstruction_certificates.py
  python3 cubic_conjecture_search/verify_round23.py
Data and results: round23_data and round23_verification.json.

Latest continuation: exact cap-and-chain formula (round 22)
=========================================================
The original conjecture remains unresolved. The one indexed fragment
failing both round-21 criteria splits into a fourteen-vertex two-port R+
and the known thirteen-vertex cap P. R+ is formed from R=F-e by adding
ports a,b and edges ua,ab,bv. Its only feasible states are 00,11,22,
with exact selected sizes 6,8,8 (doubled surpluses -2,+2,+2).

For ANY simple cubic assembly of R+ and P, let r_cyc count R+ blocks in
cyclic components of the fragment-incidence graph. The paper proves
  c_ind(G) = |V(G)|/2 + r_cyc.
Path components terminate in two P caps and attain equality; cyclic
components contribute +1 per R+ block. This resolves arbitrary assemblies
made solely of that exceptional disconnected fragment, not arbitrary
mixed assemblies of all exceptional fragments.

A bounded mixed-assembly search retains 388 records plus 56 uniform cases.
All 444 full expanded graphs, of orders 100 through 580, have independently
checked nonnegative-surplus witnesses. There are 443 OPTIMAL and one
FEASIBLE solver reports; general optimum claims are not independently
verified. The one FEASIBLE uniform case is optimal by the proved formula.
The records can repeat an assembly and are not a census.

The verifier checks all 24,576 local subsets, the source decomposition and
isomorphisms, 200 path/cycle transfer calculations, and every full-graph
witness. Data: round22_data; results: round22_verification.json.
Reproduce:
  python3 cubic_conjecture_search/exploratory/exception_assemblies.py
  python3 cubic_conjecture_search/exploratory/exception_uniform.py
  python3 cubic_conjecture_search/verify_round22.py

Latest continuation: three-port contraction certificates (round 21)
=================================================================
The original conjecture is unresolved. Exact cycle-space searches produced
1,238 vertex-deletion profiles from 42 retained near-sharp cubic graphs of
orders 24 through 32. The independent verifier checks 13,927 feasible-state
witnesses directly, without relying on optimality or infeasibility claims.

The paper proves a contraction criterion: an odd-order three-port fragment
with all-zero surplus at least -1, and surplus at least +1 for each pair of
open ports (the third port may be unselected or internally saturated), can
be replaced by one vertex when its outside neighbours are distinct. Any
half-bound witness in the contracted graph lifts with the required gain.
1,190 fragments satisfy this criterion.

A second proved criterion permits arbitrary assemblies of 1,230 fragments:
either an all-zero-port nonnegative-surplus witness exists, or its surplus
plus that of a witness selecting exactly one port is nonnegative. Conflicts
between single-port choices form a matching; averaging proves the bound.
Seven of its eight exceptions satisfy the contraction criterion.

For pairwise joins of the entire library, 594 canonical profiles reduce to
45 componentwise-minimal profiles. All 12,150 ordered-pair/port-matching
checks have nonnegative certified surplus. This certifies every pairwise
join in the library, not every larger assembly of exceptional fragments.

Reproduce from the repository root:
  mkdir -p tmp/cubic_round21
  clang++ -O3 -std=c++17 cubic_conjecture_search/exploratory/three_pole_large.cpp -o tmp/cubic_round21/three_pole_large
  tmp/cubic_round21/three_pole_large cubic_conjecture_search/round21_data/seeds.g6 cubic_conjecture_search/round21_data/profiles.txt
  python3 cubic_conjecture_search/exploratory/reduce_three_pole_profiles.py
  python3 cubic_conjecture_search/verify_round21.py

Latest continuation: exhaustive edge neighbourhoods (round 20)
=============================================================
The original conjecture remains unresolved. For each retained sharp seed
of orders 24 and 26, every labelled simple cubic graph obtained by deleting
at most four seed edges and reconnecting the exposed incidences has a
half-sized induced 2-regular subgraph. Disconnected candidates are included.
Counts are reconnection records, with possible duplicates: 1,974,349 and
2,897,883. All 1,350 newly required positive witnesses are independently
checked. The reconnection generator is also checked against independent
complete labelled cubic enumeration at orders 6 and 8. The large regions
are not independently regenerated. See round20_verification.json.

The direct constraint-generation attempts produced 9 and 7 candidates,
then reached wall-time limits. Their outcomes alone are inconclusive.
All candidate optima and qualifying-set counts were independently checked
by cycle-space enumeration. No auxiliary failure is an original counterexample.

Reproduce (from repository root):
  clang++ -O3 -std=c++17 cubic_conjecture_search/exploratory/edge_ball_enumerate.cpp -o tmp/cubic_round20/edge_ball_enumerate
  tmp/cubic_round20/edge_ball_enumerate cubic_conjecture_search/round20_data/seed24.g6 cubic_conjecture_search/round20_data/seed24_masks.txt 4 cubic_conjecture_search/round20_data/ball24
  tmp/cubic_round20/edge_ball_enumerate cubic_conjecture_search/round20_data/seed26.g6 cubic_conjecture_search/round20_data/seed26_masks.txt 4 cubic_conjecture_search/round20_data/ball26
  python3 cubic_conjecture_search/verify_round20.py

Round 19 proved the Petersen-four-pole packing bound c_ind >= 5k and
checked explicit witnesses of sizes 31 and 30 in two 52-vertex graphs.
Its local smoothing fails when all four outside neighbours are selected.
The proof and limitation appear in Section 15 of the paper; the original
conjecture is unaffected. See round19_verification.json.

Latest continuation: direct searches and strict family certificates
=================================================================
The ORIGINAL conjecture remains unresolved. No original counterexample
or general proof was obtained. This continuation does not meet the
requested stopping condition.

A direct cubic-graph search minimized the maximum good-set size, then
the number of maximum good sets. It used edge switches, occasional
upward moves, and restarts. Cycle-space enumeration was exact for
accepted moves; early exits produced only positive lower bounds.
Twelve seeds led to 30,000 switch proposals at orders 24,26,28,30,32,
36,38,42. Including 185 retained vertex expansions, the saved data
contain 30,185 records and 28,733 distinct labelled graphs. All saved
positive witnesses were independently degree-checked. A separate
vertex-assignment enumeration checks all 45 best records, including
both their optima and their numbers of maximum good sets.

The best retained exact sizes by order are:

    order:       24  26  28  30  32  36  38  42
    best size:   12  13  15  16  18  18  19  21

These are results of a bounded heuristic search, not exhaustive lower
bounds for all graphs at those orders.

Four newly retained bases of orders 26,28,30,32 were tested for
simultaneous edge-triangle replacements. The solver reported INFEASIBLE
for all four counterexample queries, but no formal infeasibility proof
files are retained. Separately, EXACT RATIONAL certificates prove the
positive conclusion, with cut totals respectively 96/7,29/2,31/2,33/2.
The certificate term counts are 84,10,10,12. Each cut total exceeds n/2.

The existing lifting proof gives the quantitative bound

    b_ind(H_A) >= |A| + ceil(tau),
    tau = sum_e min(p_e,1-p_e).

Consequently the cubic completions of ARBITRARY triangle chains on
each of these four bases satisfy c_ind >= order/2+1. The certificate
checks use Fraction arithmetic and do not rely on solver statuses.
This proves four further infinite-family bounds, not the original
unrestricted assertion.

    python3 cubic_conjecture_search/verify_round18.py

The direct search source is exploratory/cubic_multiplicity_descent.cpp.
The large-seed construction is reproducible with
exploratory/prepare_cubic_descent_seeds.py. Data, parameters, logs,
compressed witnesses, and rational certificates are in round18_data/.
Independent results and hashes are in round18_verification.json.
Non-best records are independently checked only as positive witnesses;
their reported exact flags are not a repeated optimum census.

Previous continuation: marked forests in a smallest obstruction
==============================================================
The ORIGINAL conjecture remains unresolved. No original counterexample
or general proof was obtained, so the requested stopping condition is
not met.

There is a stronger necessary condition on the normal form from the
previous continuation. Let H_A be a minimum-order branch counterexample
obtained by expanding edges A of a simple cubic base G. For EVERY
nonempty B subset A, put U=V(B) and q_B=|E(G[U]) minus A|. Then

    2|B| + q_B <= 2|U|-1.

Proof: take the good set consisting of the gadget triangles for B.
It contains 2|B| branch vertices and its outside neighbourhood is U.
The exact neighbourhood-deletion identity gives a drop of 2|U|-q_B
in |E|-|V|. If the displayed strict inequality failed, deletion and
the explicit lift would give a smaller counterexample.

In particular A must be a FOREST. Every nontrivial marked component
induces a tree or a unicyclic graph in G. For the full subset condition,
contract the nontrivial components of A and keep all unmarked edges
with both ends in V(A), retaining loops and parallel edges. The condition
is equivalent to this auxiliary multigraph having at most 2|W|-1 edges
inside every nonempty vertex set W. The paper gives both directions.
This does not say that A is a matching, and A can still be empty. The
unrestricted cubic case therefore remains open.

Independent standard-library checks compare the two formulations on
all 21,568 markings of all eight connected cubic bases through order
eight. There are 13,284 forests; 4,276 markings satisfy the stronger
condition. For markings of size at most three, 10,351 neighbourhood
deletions and all 45,390 good-set lifts are checked.

Two bounded synthesis runs sought a 29-vertex rooted graph with both
rooted optima at most 14, which would give a genuine 58-vertex original
counterexample after doubling. They allowed at most six or four removed
seed edges, fixed the root neighbours, and preserved degrees. The first
stopped on a query timeout after one candidate; the second reached the
wall-time limit after six. Neither region is proved infeasible. A
separate binary-cycle-space enumeration verifies every candidate's
rooted optima and checks a good set of size at least 29 on each full
58-vertex cubic double. No candidate violates the original conjecture.

    python3 cubic_conjecture_search/verify_round17.py

Search records are in round17_data/; independent profiles, witnesses,
counts and data hashes are in round17_verification.json. The updated
paper includes the unrestricted sparsity proof and the bounded search
outcomes with their limitations.

Previous continuation: a normal form and conditional certificates
================================================================
The ORIGINAL conjecture remains unresolved. The requested stopping
condition has not been met: no general proof or original counterexample
has been obtained.

A new structural theorem eliminates the loop and parallel-edge gap in
triangle-chain reductions. Every minimum-order counterexample to the
branch inequality would be obtained from a connected SIMPLE cubic base
G on n vertices by replacing each edge of A once with a triangle gadget,
where |A| < n/2. The empty set A is allowed, so this theorem leaves the
unrestricted cubic case. It does NOT assert that A is a matching.

The proof uses an exact neighbourhood deletion identity. For a good set
S, write T=N(S)-S and H'=H-(S union T). Then

    b_ind(H) >= b_ind(H') + |S intersect V_3(H)|,
    (m-n) - (m'-n') = sum_{v in T}(d_H(v)-1) - |E(H[T])|.

This rules out triangle chains forming loops or sufficiently long
parallel pairs. An explicit three-case lift handles one expanded edge
parallel to an ordinary edge, including coincident or adjacent outside
neighbours. The previous consecutive-triangle lemma then leaves at most
one triangle per edge of a simple base.

The simultaneous-replacement formula has a useful exact simplification.
For Eulerian F with support R and chord set X contained in A,

    lifted branch surplus = |A symmetric_difference delta(R)| - n/2.

Thus a probability distribution on states with X contained in a set P
of forced marked edges certifies all markings P subset A disjoint from Q
if

    sum_{e in P}(1-p_e) + sum_{e in Q}p_e
      + sum_{e outside P union Q}min(p_e,1-p_e) >= n/2.

Here Q is forced unmarked, and p_e is the cut probability. Two exact
rational certificates (ten states each) prove the inequality for ALL
2^39 markings of the sharp 26-vertex double of P, splitting on whether
its joining bridge is marked. This is a certificate proof, not an
individual enumeration of 549,755,813,888 cases. Pair reduction extends
it to arbitrary triangle chains, covering a base that the unconditional
criterion cannot certify.

Explicit uniform distributions on four rooted good sets each also give
cut probabilities at most 1/2 in the thirteen-vertex attachment, both
with its root in and out. Consequently arbitrary triangle chains and
completion of their new tips produce rooted graphs Q with

    |V(Q)| = 13+16K,  A(Q) >= 7+8K,  B(Q) >= 6+8K.

These are lower bounds, not claims of exact optima. They prove the half
bound for arbitrary bridge-tree graphs from the paper after expanding
bridges and leaf-cap edges and completing the new tips. The original
internal triangle edges are excluded from that particular corollary.

The independent standard-library verifier checks 17,945 neighbourhood
lifts on 12,911 small labelled subcubic graphs; 4,850 lifts for the short
parallel configuration; 55 longer loop/parallel configurations; all
rational coefficients and conditional inequalities; and both rooted
certificates for all 524,288 markings. It constructs 191 full cubic
doubles of order at most 90 and checks their half-bound witnesses.

    python3 cubic_conjecture_search/verify_round16.py

Certificates are retained in round16_data/; counts and data hashes are
in round16_verification.json. The mathematical proofs, not a solver
infeasibility status or the finite checks, establish the family results.
The paper and PDF have been updated.

Previous continuation: simultaneous replacements
================================================
The ORIGINAL conjecture remains unresolved. No original counterexample
was found, and the requested stopping condition has not been met.

Two new statements are proved for simultaneous triangle replacements.
Let G be a simple cubic base of order n, and replace any subset A of its
edges by the triangle gadget from the preceding continuation. For every
Eulerian edge set F of G, write R=V(F), X=E(G[R])-F, and C=delta(R).
The set X is a matching. The exact branch optimum of the expanded H_A is

    b_ind(H_A) = max_{F Eulerian, X subset A}
                   [ |R| + 2*(|A|-|A intersect C|-|X|) ].

Thus simultaneous replacements can be evaluated using the cycle space
of the BASE graph, without an extra exponential factor for the gadgets.
The empty Eulerian set is included. This is an exact formula; the proof
projects every good set and gives an attaining lift in the other direction.

A probability distribution on good sets of G, with edge-cut probabilities
p_e, is a sufficient certificate for ALL marked-edge subsets if

    sum_e min(p_e,1-p_e) >= n/2.

Indeed the expected lifted surplus is
sum_{e not in A} p_e + sum_{e in A}(1-p_e) - n/2, which is nonnegative.
The consecutive-triangle reduction extends the conclusion to arbitrary
nonnegative numbers k_e of triangles in series on every edge. If K is
their sum, the subcubic graph has branch optimum at least n/2+K, and
its cubic completion has n+16K vertices and satisfies the half bound.

EXACT RATIONAL certificates are saved for 2,250 bases: 2,249 selected
connected cubic bases through order twenty, plus one tight base of
order twenty-four. The list through order twenty was selected for
computed optimum at most n/2+2; the certificate proof does not rely on
that eligibility claim. Uniform distributions suffice for 1,477 bases,
and rational LP proposals supply the other 773. The verifier checks
all selected degrees, coefficient signs and sums, and the cut inequality
using Fraction arithmetic. These certificates prove infinite families
via arbitrary triangle-chain lengths; they do not cover all cubic graphs.

The sufficient certificate cannot hold for the known sharp 26-vertex
double of P. Every good set has size at most 12 plus its indicator of
crossing the joining bridge. If that crossing probability is p, then
the cut sum is at most 12+p-max(0,2p-1) <= 25/2 < 13. A saved rational
distribution attains 25/2. This is a limitation of the certificate;
the graph itself satisfies the original conjecture with equality.

Independent verification checks the new Eulerian-state generator against
all edge subsets of all eight connected cubic bases through order eight.
It also checks the optimum formula against every vertex subset of 551
expanded graphs: every marking of K4, and markings of size at most two
for the other bases through order eight. All 551 full cubic completions
have directly degree-checked half-bound witnesses, with orders up to 100.

Exploratory searches followed strict or neutral surplus steps to depth
four and produced 11,193 distinct labelled expanded graphs. Saved
positive witnesses are independently checked. Simultaneous-marking
CP-SAT runs report INFEASIBLE for 1,387 of the selected small bases
before the overall wall-time limit, and for two further tight bases
of orders 24 and 26. No formal solver infeasibility proofs are retained.
The rational certificates, not those statuses, prove the family claims.

    python3 cubic_conjecture_search/verify_round15.py

round15_data/ preserves all rational certificates, search records, and
query statuses. Large text records are gzip-compressed. The exact
verification summary and SHA-256 hashes are in round15_verification.json.
The paper includes the unrestricted formulas and conditional theorems,
their verified applications, and their explicit limits.

Previous continuation: one triangle and strictness census
=======================================================
The ORIGINAL conjecture remains unresolved. This continuation does not
provide a proof or a counterexample to it.

An exact local formula is proved. Replace an edge uv of a cubic graph
G on n=2h vertices by ua,ab,bv,aw,bw, with new vertices a,b,w. Write
B=c_ind(G-uv), T for the largest good set of G containing both u,v,
and C for the largest good set avoiding both. The resulting subcubic H
satisfies

    b_ind(H) = max(B,T+2,C+2),        |E(H)|-|V(H)| = h+1.

If G satisfies the half bound but H fails the branch inequality, then
c_ind(G)=h, B<=h, and T,C<=h-2. Thus every maximum good set of G must
separate u,v. Subdivide uv once and join two copies at the new roots:
the resulting cubic graph has 2n+2 vertices and c_ind<=n, so it would
be an ORIGINAL counterexample. No graph meeting these conditions was
found. The statement is a necessary condition and an exact reduction,
not a proof that the conditions are impossible.

A strictness census of all 556,471 connected cubic graphs through order
20 finds exactly one equality case, the twelve-vertex Franklin graph.
All other 556,470 graphs have saved good sets of size at least n/2+1.
These witnesses are lower bounds, not asserted maxima. All 4,096 vertex
subsets of the equality case confirm optimum 6, twenty maximum sets,
and a maximum set containing each of its eighteen edges. An explicit
isomorphism to the defined Franklin graph is independently checked.
Coverage up to isomorphism relies on the existing geng input lists.

The formula and this census certify all 16,539,825 indexed single-edge
triangle replacements in those base graphs, and their cubic completions.
This last count is a deduction, not a claim to have enumerated every
expanded graph. The formula itself is separately checked on all 387
edge expansions of cubic bases through order ten and of Franklin,
using every vertex subset of the expanded graphs.

Two bounded synthesis runs sought rooted caps Q of order 25 with
(A,B)<=(12,12) and (A,B)<=(13,11). Both would give original 50-vertex
counterexamples by doubling. The runs preserve root neighbours {1,2}
and permit deletion of at most six seed edges, with matching insertions.
They examined 13 and 10 candidates and reached wall-time limits. Neither
search region is proved infeasible. Independent cycle-space enumeration
computes A,B for all 23 candidates, and a good set of size at least 25
is checked on every full doubled cubic graph. The initial symmetric run
saved only its size-threshold oracle values; its complete A,B profiles
are in round14_verification.json. The final search source also checks
the full doubling criterion on every candidate.

    python3 cubic_conjecture_search/verify_round14.py

The verifier also cross-checks its cycle-space enumeration and the
synthesis degree-propagation oracle against brute force on all 843
labelled subcubic graphs through order five. round14_data/ retains
the positive census certificates and all synthesis candidates; the
verifier records hashes and exact scope. The existing paper and PDF
now include the formula and the finite classification.

Previous continuation: bridge symmetrization
============================================
The ORIGINAL induced-cycles conjecture remains unresolved. No original
counterexample was found in this continuation.

Bridge symmetrization is now proved. If deleting a bridge gives rooted
fragments Q_1,Q_2, let A_i,B_i be their root-in/root-out good-set optima,
delta_i=max(0,A_i-B_i), and d_i=c_ind(D(Q_i))=2B_i+delta_i. Then

    c_ind(G) = (d_1+d_2+abs(delta_1-delta_2))/2.

Consequently, ANY counterexample with a bridge yields a counterexample
formed by joining two identical rooted fragments. The new graph can
have larger order. This leaves bridgeless counterexamples unrestricted
and does not establish that all symmetric joins satisfy the bound.

The corresponding direct search made 20,000 rooted-cap mutation
proposals at orders 13,25,29,37. They contain 14,088 distinct labelled
rooted graphs, with symmetric cubic joins of orders 26,50,58,74. Every
proposal has a verified half-bound witness on the FULL cubic graph.
There are 19,845 early positive exits (lower bounds, not exact optima).
The other 155 records are exact and attain half on doubling; these
comprise 95 distinct labelled rooted graphs. Independent vertex-state
recursion verifies all 95 exact local optima; the search uses binary
cycle-space enumeration. This is a heuristic search, not a census.

    python3 cubic_conjecture_search/verify_round13.py

round13_data/ preserves all candidate certificates and the seeds.
exploratory/rooted_pair_descent.cpp is the direct search. The initial
13- and 29-vertex seeds are sharp; the 25- and 37-vertex seeds are
edge inflations and initially have positive surplus. The search reaches
sharp 25-vertex profiles as well. No negative candidate was observed.

A separate attempted proof estimate was rejected: c_ind(G) need not
be at least L(M)-2*j(M) for an odd factor M. The saved 20-vertex graph
has c_ind=12 but an odd factor with L=15 and j=1. Exhaustion of all
1,048,576 vertex subsets verifies this auxiliary failure. The graph
satisfies the original half bound; it is not an original counterexample.
The failed estimate is recorded to avoid reusing it as a proof step.

Previous continuation: consecutive triangles and direct certificates
===================================================================
The ORIGINAL induced-cycles half-bound conjecture remains unresolved.
This round searched it directly and strengthened a minimal-counterexample
reduction. No auxiliary obstruction is presented as a solution.

New proved reduction: two consecutive degree-two triangles abw, cdz,
joined by bc and attached to distinct nonadjacent outside vertices u,v
via ua,dv, can be replaced by uv. If H' is the smaller graph, then

    b_ind(H) >= b_ind(H')+2,     (m-n)(H) = (m-n)(H')+2.

Every good set of H' lifts: when both u,v are selected use the path
u-a-b-c-d-v; otherwise select a triangle with no selected outside
neighbour. The first case gains four branch vertices, the others two.
Thus this configuration cannot occur in a smallest counterexample.
The outside-neighbour assumptions are part of the statement.

Direct positive certificates were independently checked for:
* All 1,240,455 unordered pairs of distinct edge-triangle replacements
  in the 4,654 connected cubic base graphs of orders 12,14,16 generated
  by geng. The base edges may share an endpoint. The resulting subcubic
  graphs have orders 18,20,22 and two degree-two vertices; each satisfies
  b_ind >= m-n. Their cubic completions have orders 44,46,48 and satisfy
  the original conjecture by the exact completion formula. Counts are
  indexed constructions, not distinct isomorphism classes. Base-list
  completeness relies on geng.
* 1,595 distinct labelled cubic edge-switch candidates of orders 36..114
  starting from sharp constructions. Every candidate has a half-bound
  witness; one initially unresolved timeout has a successful retry.
* 14 named cubic graphs with LCF descriptions from SageMath, orders
  8..126, each with a witness strictly exceeding half. These are lower
  bounds, not asserted maxima. The verifier reconstructs the LCF edges.

The cycle-space search stops on a positive witness. Independent checking
uses only the saved vertex subsets and reconstructed graph adjacency.
The new triangle reduction also has 7,984 directly checked good-set
lifts over 3,615 edge replacements in labelled subcubic graphs through
order five. The paper gives the unrestricted proof.

    python3 cubic_conjecture_search/verify_round12.py

round12_data/ retains every positive certificate (the triangle-pair
records are gzip-compressed), graph inputs and solver query statuses.
round12_verification.json records the independent checks and data hashes.
exploratory/triangle_pair_search.cpp and original_bound_search.py are
the search implementations. No timeout is interpreted as infeasibility.

A separate exhaustive 16-vertex example shows that maximizing the edge
count among odd pseudoforests need not allow an isolated-edge-free
maximizer (15 versus 14 edges). Its induced-cycles maximum is 12, so
this auxiliary objective failure is NOT an original counterexample.
It is recorded in the verification JSON and not used to claim progress
on the original conjecture beyond eliminating that proof objective.

Previous continuation: unbounded repair barriers
================================================
The monotone odd-pseudoforest repair assertion is FALSE. The original
induced cycles conjecture remains unresolved.

For every k >= 3, form B_k from two disjoint k-cycles, joined at one
designated vertex of each by a bridge. Attach a copy of the thirteen-
vertex cap P to each of the remaining 2k-2 cycle vertices. Then

    |V(B_k)| = 28k - 26,       c_ind(B_k) = 14k - 13 = |V(B_k)|/2.

There is an explicit odd spanning pseudoforest M_k with j(M_k)=1.
Every sequence of simple-cycle exchanges through odd pseudoforests
that reaches j=0 must first pass through j >= k. The shortest such
sequence has k exchanges, and an attaining sequence has defect counts

    1, 2, ..., k, 0.

Thus neither a monotone repair nor a uniform bound on temporary defect
increase is possible. This is an unrestricted theorem, not a conclusion
from a finite search. The first example has 58 vertices and escape
counts 1,2,3,0; its final induced cycle union has 29 vertices.

The proof uses the cap's root-out optimum of six. If a cap factor's
root component is acyclic, either its attachment becomes an isolated
edge or the cap has an internal isolated edge. Before the first core-
cycle exchange, all k-1 adjacent caps must be made acyclic. They each
cost at least one defect while the original isolated bridge persists.
The explicit seven-cycle (0,2,12,4,6,5,3,0) switches each cap into the
required state, proving that both lower bounds are attained.

Independent verification exhausts 524,288 cap-edge subsets, 8,192
cap-vertex subsets, and all 128 parity states. The twelve zero-cost
cap states form a connected exchange graph. Their product gives the
complete 20,736-state neutral component of the 58-vertex example.
All those global states and their 41,472 core-cycle exits are checked
directly; every exit fails the pseudoforest condition. The verifier
also checks explicit escape sequences for k=3,...,12, orders 58,...,310.

The obstruction does not survive the tested canonical bipartite double
covers: explicit two-cycle sequences have j=2,1,0 and end with good
sets of size n/2+4. All ten covers, orders 116 through 620, are checked
to be connected and bridgeless. These are specific examples, not a
general theorem about repair in bridgeless graphs.

Reproduce the independent checks without third-party dependencies:

    python3 cubic_conjecture_search/verify_round11.py

The exploratory CP-SAT program large_cycle_repair.py found the first
cover witnesses. A 30-second timeout on order 284 was reported UNKNOWN;
the later explicit template supplies a verified repair for that graph.
round11_data/ retains full graph and factor witnesses, cap profiles,
and both the exploratory and independently checked results. Section 13
of the paper contains the proof. Historical result files are preserved;
their earlier 'unproved' status for monotone repair is superseded here.
The broader existence of an odd spanning pseudoforest with j=0 remains
unproved, as does the original induced cycles conjecture.

Previous continuation: single-edge replacement
==============================================
The original conjecture remains unresolved. Two unrestricted statements
now explain what single-edge replacement by R=F-(2,4) can and cannot do.

If H_R replaces an edge uv of a simple cubic graph H by this twelve-vertex
fragment, then

    c_ind(H_R) = 6 + max(c_ind(H), c_ind(H-uv)).

The four feasible boundary states of R give both the upper bound and
explicit attaining extensions. In particular, this operation preserves
the half bound whenever it holds for H. A smallest counterexample cannot
contain an induced copy of R with distinct, nonadjacent outside neighbors,
since smoothing it to one edge would give a smaller simple cubic graph.

There is also a factor lift preserving every simple-cycle exchange. In R,
take the tree with edges

    (0,2) (1,2) (1,3) (1,11) (4,6) (4,7)
    (5,6) (6,8) (8,10) (8,11) (9,11)

and the path P=(2,0,3,5,7,4). T symmetric-difference P is an odd unicyclic
spanning graph U, namely the cycle (1,3,5,6,8,11) with six pendant leaves.
When uv belongs to a factor M, replace it by T and the two attachment
edges. When uv does not belong to M, add U as a separate factor component.
The lifted factor is an odd pseudoforest whenever M is, with exactly six
additional leaves and

    j(lift(M)) = j(M) - indicator(uv is an isolated component of M).

A cycle using uv lifts by replacing that edge with the attachment edges
and P; other cycles remain unchanged. If uv is initially not an isolated
component, a monotone-j repair of length l therefore lifts to a repair of
length at most l: stop at the first lifted strict decrease. This rules out
making a two-exchange repair harder by this particular factor lift.
It does not cover arbitrary factors of H_R or prove that a repair exists
in H. The paper's Section 12 contains the complete arguments.

The independent verifier checks 312 pseudoforest lifts and 4,209 cycle
exchanges on small base graphs, as well as all 5,111,808 vertex subsets
of the 24 edge replacements of connected cubic graphs through order six.
It verifies the exact replacement formula in every case.

Two structured searches were also completed:
* 2,895 labelled triangle expansions of the three order-20 obstructions,
  at orders 22..42: 2,882 have one-move repairs and thirteen need two.
* 216 lifted factors on 54 labelled graphs of order 32 formed by inserting
  R: sixty have one-move repairs and 156 need two.
All 3,111 recorded repair paths and their final good sets are independently
checked. These are samples, not exhaustive graph censuses at their orders.

Exhausting all 7,077,888 odd factors in those 54 order-32 inputs gives
5,895,198 pseudoforests, of which 5,878,454 have isolated edges. Every bad
one admits a repair within two exchanges. Exactly 1,838 factors need a
neutral first move; all have j=1. The separate path search reproduces
their two-move distances and retains every path. The independent verifier
checks all these paths and, for one neutral factor in each of the 54
graphs, exhausts all simple cycles (968,802 total) and confirms that no
direct repair exists. It does not independently repeat the full census.

Reproduce from the repository root:

    mkdir -p tmp/cubic_round10
    python3 cubic_conjecture_search/exploratory/repair_expansions.py
    python3 cubic_conjecture_search/exploratory/repair_inflations.py
    clang++ -O3 -std=c++17 cubic_conjecture_search/exploratory/pseudoforest_distance.cpp -o tmp/cubic_round10/pseudoforest_distance
    tmp/cubic_round10/pseudoforest_distance cubic_conjecture_search/round10_data/expansion_inputs.txt
    tmp/cubic_round10/pseudoforest_distance cubic_conjecture_search/round10_data/inflation_inputs.txt
    tmp/cubic_round10/pseudoforest_distance cubic_conjecture_search/round10_data/inflated_neutral_inputs.txt
    clang++ -O3 -std=c++17 cubic_conjecture_search/exploratory/pseudoforest_repair.cpp -o tmp/cubic_round10/pseudoforest_repair
    tmp/cubic_round10/pseudoforest_repair --k2 --record-neutral --quiet cubic_conjecture_search/round10_data/inflated_graphs.g6
    python3 cubic_conjecture_search/verify_round10.py

The triangle sample uses seed 2026102710. The path search reports a
state-limit stop as unresolved, never as a trap. No stop or trap occurred
in these runs. round10_data/ retains the inputs and paths, while
round10_verification.json stores the independent checks. At that stage,
both the repair assertion and the original conjecture were unresolved.
Round 11 disproves the repair assertion; the original conjecture remains
unresolved.

Previous continuation: the order-20 census
==========================================
The general conjecture is still unresolved. The complete odd-pseudoforest
repair census has now been extended to every connected simple cubic graph
of order 20, up to isomorphism. This is a test of a stronger proposed repair
assertion, not a new verification range for the original conjecture, which
the literature already checks through order 22.

The order-20 run covers 510,489 graphs and 1,045,481,472 odd factors.
Of these, 920,048,096 are pseudoforests and 889,866,061 contain isolated
edges. Every bad pseudoforest can reduce its number j of isolated edges
in at most two simple-cycle exchanges preserving the pseudoforest
condition and never increasing j. Exactly 1,234 factors need two moves;
all others have a direct improvement. These 1,234 factors occur in 291
graphs: 152 factors have vertex connectivity one, 1,079 connectivity two,
and three connectivity three. There are 1,218 cases with j=1 and sixteen
with j=2. All supporting order-20 graphs have triangles.

Thus 3-connectivity does NOT guarantee a one-step repair. One explicit
example has graph6 code S??????o@_@_gCGoWCAD?Cg?X??WO?IG? and initial
factor mask 983379956. The factor is a K2 plus an 18-vertex unicyclic
component. Of 664 simple cycles, none gives an immediate j-reduction;
57 give neutral moves. A shortest repair is

    983379956 -> 983451959 -> 977257976.

The final factor has eleven leaves forming a good set. Complete vertex
subset enumeration gives c_ind=14 for this graph, so it is not a
counterexample to the original half bound. The other two 3-connected
examples also have c_ind=14. No 3-connected one-step obstruction occurs
in the complete smaller-order census, so 20 is the minimum possible
order according to these exhaustive finite computations.

The standard-library verifier verify_round9.py independently checks
all 1,448 reported neutral factors through order 20. It uses direct
edge-parity recursion, vertex-path cycle enumeration, and component
traversal, rather than the C++ cycle-space/DSU implementation. Across
the 330 supporting graphs it enumerates 633,600 odd factors and 93,837
simple cycles; every reported case has no direct improvement and an
explicit two-move repair. It also checks every one of the 3,145,728
vertex subsets of the three 3-connected examples. It does not repeat
the full 556,471-graph census independently.

Another failed shortcut is to minimize h(M)=|E(M)|+j(M) over all odd
factors. The ten-vertex graph I?BeeOwM? has minimum h=8 among factors
with j>0, but minimum h=9 among factors with j=0. Independent enumeration
checks all 64 odd factors and all 1,024 vertex subsets, obtaining c_ind=6.
The minimum bad factor can be two K1,3 components plus a K2; it also
disproves c_ind >= number_of_leaves(M)-j(M).

A separate triangle-expansion calculation also rules out a unit-gain
shortcut. Let B be the largest good-set size avoiding a cubic vertex v,
C the largest avoiding N[v], and D the largest size containing v in G-e,
maximized over edges e incident with v. Replacing v by a triangle gives
the exact value max(D+1,B,C+3). A good set meets the new triangle in
zero, two, or three vertices. In the two-vertex case, contract them to
v and delete the edge from v toward the third triangle vertex's external
neighbor; this gives exactly the D state. The external neighbor may be
selected, so replacing D by the maximum in the original G is invalid.

Independent subset enumeration checks both that missing-state issue
and a genuine no-unit-gain example. For K?ABE`Ke@gDO at vertex 0,
(B,C,D)=(8,5,7); both the original 12-vertex graph and its 14-vertex
triangle expansion have c_ind=8. Both satisfy the half bound. The
corrected exploratory scan covers 816,770 vertex profiles in all 45,982
cubic graphs through order 18 and finds 13,183 profiles with no unit gain.
The initial three-state calculation was discarded after direct subset
verification detected its missing boundary state; only the corrected
four-state calculation is retained.

Reproduce the main census and independent certificates:

    mkdir -p tmp/cubic_round9
    geng -c -d3 -D3 20 tmp/cubic_round9/cubic20.g6
    clang++ -O3 -std=c++17 cubic_conjecture_search/exploratory/pseudoforest_repair.cpp -o tmp/cubic_round9/pseudoforest_repair
    tmp/cubic_round9/pseudoforest_repair --k2 --record-neutral --quiet cubic_conjecture_search/round9_data/cubic20.g6
    tmp/cubic_round9/pseudoforest_repair --k2 --record-neutral --quiet cubic_conjecture_search/round8_data/cubic_through18.g6
    python3 cubic_conjecture_search/verify_round9.py

The full census may take substantial time; the independent verifier
checks the retained obstruction certificates without repeating it.
The new max_neutral_repair_moves field is the actual BFS distance to
the first strict improvement. Historical max_flat_size remains a queue
size, not a path length. round9_data/ retains inputs and logs, and
round9_verification.json stores the independent certificates. The paper
and PDF include the new 3-connected obstruction and census.

Previous continuation: a first repair step
==========================================
A first-step repair theorem for odd pseudoforests is now proved.
The general conjecture is still unresolved.

For every perfect matching P of a nonempty finite simple cubic graph, some
induced non-P-alternating cycle C makes P symmetric-difference C an
odd spanning pseudoforest with fewer isolated-edge components. The
existence of C follows from Speyer's cyclic-orientation theorem;
the resulting components and the strict decrease are proved directly.
This only proves the first repair step: later factors need not be
perfect matchings.

The sufficient assertion considered at that stage was that every odd spanning
pseudoforest with an isolated edge can be repaired by cycle exchanges
preserving the pseudoforest condition, with the number j of isolated
edges never increasing and eventually decreasing. Starting from an
odd spanning forest and iterating this assertion would prove the
original conjecture. Round 11 now disproves this assertion.

Finite obstructions rule out two shortcuts:
* A 14-vertex factor made of three K1,3 components and one K2 has no
  immediate reduction of j. A neutral move followed by a reduction
  succeeds. The same phenomenon occurs in a 36-vertex bipartite graph.
* A 16-vertex factor with 15 edges and one K2 has no nontrivial cycle
  exchange preserving both pseudoforest structure and its edge count.
  All permitted exchanges decrease its edge count. Its graph has
  c_ind=10, so it is not a counterexample to the original conjecture.

The independent standard-library verifier enumerates all simple cycles
of these examples (93, 196, and 11,976) and retains complete move tables
and exact two-move repair certificates where applicable. It also checks
a separate 14-vertex example requiring a neutral move under the objective
"maximize edges, then minimize j". On all 112 connected cubic graphs
through order 12 it independently enumerates 12,296 odd factors, of which
10,911 are pseudoforests and 9,334 contain K2 components. Every one of the
latter has an immediate j-reducing move. It checks 17,356 matching repairs
from all 1,098 perfect matchings in these graphs.

The assertion allowing neutral moves passed complete factor enumeration
for each graph in these separate input collections:
* all 45,982 connected cubic graphs through order 18: 44,513,544 factors;
  214 factors require neutral moves;
* the earlier seeded 240-graph sample of orders 24..42: 261,726,208 factors;
  144 factors require neutral moves;
* 39 bipartite double covers of orders 28..36: 18,776,064 factors;
  48 factors require neutral moves.
The latter two collections are samples, not full censuses of their orders.
The double covers come from the 39 distinct graphs containing the 214
small neutral-move factors. Every lifted starting factor has a direct
repair; the 48 neutral cases are other factors found in those covers.

An additional 7,616 connected bipartite completions of a fixed 36-vertex
factor were tested by switching its complementary edges (seed 2026102708).
Ten have no direct improvement; all ten have vertex connectivity two.
This is a finite observation, not a theorem for 3-connected graphs.
All 144 neutral-move factors in the 240-graph sample occur in one
42-vertex graph of vertex connectivity one.

Reproduce from the repository root:

    mkdir -p tmp/cubic_round8
    clang++ -O3 -std=c++17 cubic_conjecture_search/exploratory/pseudoforest_repair.cpp -o tmp/cubic_round8/pseudoforest_repair
    tmp/cubic_round8/pseudoforest_repair --k2 --record-neutral cubic_conjecture_search/round8_data/cubic_through18.g6
    tmp/cubic_round8/pseudoforest_repair --k2 --record-neutral cubic_conjecture_search/round7_data/larger_instances.g6
    tmp/cubic_round8/pseudoforest_repair --k2 --record-neutral cubic_conjecture_search/round8_data/double_covers.g6
    python3 cubic_conjecture_search/verify_pseudoforest_repair.py

For individual factors and the fixed-factor switch sample:

    clang++ -O3 -std=c++17 cubic_conjecture_search/exploratory/pseudoforest_probe.cpp -o tmp/cubic_round8/pseudoforest_probe
    tmp/cubic_round8/pseudoforest_probe cubic_conjecture_search/round8_data/double_cover_factors.txt
    tmp/cubic_round8/pseudoforest_probe cubic_conjecture_search/round8_data/bipartite_switch_inputs.txt --first
    python3 cubic_conjecture_search/verify_repair_switches.py

The --first probe stops on the first improving witness; if it reports
none, all simple cycles have been exhausted. Without --first it exhausts
all cycles in every case. The repair program's historical log fields
first_strict and first_plateau distinguish whether the first direct
improvement increased the edge count; both count strict improvements
of the chosen objective. flat_repairs counts factors needing a neutral
move. max_flat_size is the largest discovered BFS queue, not a path
length or a complete plateau size.

round8_data/ retains all inputs and logs. round8_verification.json stores
the independently checked explicit certificates; round8_search_results.json
records scope and hashes. The paper's Section 11 gives the proof and gap.
The switch verifier checks all 7,606 improving witnesses and independently
exhausts 146,120 cycles across the ten remaining inputs, also confirming
that each has vertex connectivity two.

Previous continuation: odd-factor formulation
=============================================
An odd-factor formulation and an independent exact checker have been added.
The general conjecture is still unresolved.

A good set S corresponds exactly to an odd spanning factor M with no K2
component: delete the edges of G[S], and S becomes the leaves of M.
The exact identity is

    |S| - n/2 = n - |E(M)| = components(M) - cycle_rank(M).

An odd spanning pseudoforest without K2 components would therefore suffice.
Existence of such a factor for arbitrary cubic graphs is NOT proved.
The perfect-forest theorem permits K2 components and does not close this gap.

The binary cycle space enumerates all 2^(n/2+1) odd factors in a connected
cubic graph. One pass computes the complete good-set size histogram and
all single-edge-deletion and edge-containing optima. For e=uv, put
B_e=c_ind(G-e) and T_e=max size of a good set containing u and v. Subdivide
e and join two copies at the new roots. This is a counterexample exactly
when 2B_e<n+1 and B_e+T_e<n (an infeasible T_e is negative infinity).
The output uses -1 for an infeasible edge-containing state.

Independent subset enumeration agrees with every histogram coefficient
and all 1,899 edge profiles on the 112 connected cubic graphs through
order 12, checking 369,040 subsets. An additional 240 labelled candidates
of orders 24..42 were checked by exhausting 261,726,208 odd factors.
All 11,526 resulting edge profiles fail the counterexample test. Five
inputs are tight for the original half bound. These larger inputs are
a seeded sample, NOT an exhaustive census through order 42. Every
reported maximum and edge-profile witness is retained and checked;
upper bounds depend on complete cycle-space enumeration.

Reproduce from the repository root:

    mkdir -p tmp/cubic_round7
    clang++ -O3 -std=c++17 cubic_conjecture_search/exploratory/odd_factor_enumerate.cpp -o tmp/cubic_round7/odd_factor_enumerate
    python3 cubic_conjecture_search/exploratory/odd_factor_instances.py
    tmp/cubic_round7/odd_factor_enumerate cubic_conjecture_search/round7_data/larger_instances.g6 > cubic_conjecture_search/round7_data/larger_profiles.jsonl
    python3 cubic_conjecture_search/verify_odd_factors.py

The first and last programs require only a C++ compiler and standard
Python respectively; generating the seeded larger inputs uses NetworkX.
round7_data/ retains inputs and exact profiles; round7_search_results.json
records the finite scope and file hashes. The paper's new Section 10
contains the correspondence, proofs, and remaining obstacle.

Previous continuation: exchange obstructions
============================================
Two exchange obstructions are now proved in the paper. Neither is a
counterexample to the original induced-cycles conjecture.

1. If S is good, its boundary is a matching, and q outside vertices
   have no neighbour in S, then every distinct good set T satisfies

       girth(G) <= 6 |S - T| + q.

   A switching argument constructs connected simple cubic bipartite
   two-defect graphs of arbitrarily large girth. Consequently, for
   every fixed r there is such a graph with |S|=n/2-1 for which no
   distinct good set can be obtained by deleting at most r vertices
   from S. A universal bounded-deletion improvement lemma is false.
   The proof does not assert that the starting set is globally optimal.

2. A single-cycle exchange means that the edge-set symmetric difference
   of the old and new induced cycle sets is one simple cycle. The sharp
   bridge family with its internal tree a path has a good set of size
   7t+14, while its exact optimum is 8t+13. For every t>=2, no sequence
   of nondecreasing single-cycle exchanges escapes this starting set.
   Thus the gap from the true optimum is unbounded.

   At t=2 this gives a specific 58-vertex graph with a locally optimal
   28-vertex set and true optimum 29. An improving sequence must first
   fall to at most 26 vertices. The explicit sizes 28,27,26,29 attain
   this barrier. The verifier checks all 430 simple cycles: 88 flips
   yield good sets, and none improves the starting set. The example
   satisfies the original half bound exactly.

Run the independent, standard-library verification:

    python3 cubic_conjecture_search/verify_exchange_obstructions.py

It also verifies exact minimum deletion counts on 600 seeded examples
of orders 26,38,50, checking 48,480 candidates with smaller deletion
counts. These sampled minima are one or two. Their small values do
not extend to the unbounded-girth construction. Sources and sample
outputs are retained in exploratory/ and round6_data/;
round6_verification.json contains the explicit 58-vertex graph,
selected sets, exact optimum, and escape sequence.

The general conjecture is still unresolved. The new theorems rule out
two specific proof/search strategies; they do not substitute for a
proof or counterexample to the requested conjecture.

Previous continuation: two defects
==================================
The newest continuation classifies and exhaustively checks a restricted
bipartite two-defect class; it does NOT settle the general conjecture.

If a cubic graph has a 1-limited dominating set D of size n/2+1,
then either D is good or its complement S is good and G[D] has
exactly two degree-three vertices. The latter component is a theta
or two cycles joined by a path; all other components are cycles.
For bipartite graphs the branch vertices are in opposite colour
classes. This gives a complete template list for that restricted class.

Every bipartite completion of these templates was checked at orders
10, 14, 18, 22, and 26. At order 26 there are 88 templates and
36,115,200 labelled completions; every one has a directly checked
good set on at least 14 vertices. These are NOT counts of pairwise
nonisomorphic graphs. Witnesses were checked during the run; the saved
files contain aggregate counts and rolling digests rather than a
separate witness for every completion. No counterexample was found.

The paper gives the structural proof and a parity restriction:
a cubic bipartite graph of order 0 modulo 4 has no 1-limited
dominating set of size n/2+1; one of order 2 modulo 4 has none of
size n/2. Together with the finite census, this verifies the conjecture
for every cubic bipartite graph of order at most 26 having a 1-limited
dominating set of size at most n/2+1. Such a set need not exist in an
arbitrary cubic graph. The two-defect case at unbounded order also
remains unresolved here.

The independent verifier confirms the 22 complement shapes and four
cycle factors against separately generated nauty files. It also checks
the counting solver by direct enumeration on all 112 connected cubic
graphs through order 12. Reproduce from the repository root:

    mkdir -p tmp/cubic_round5
    clang++ -O3 -std=c++17 cubic_conjecture_search/exploratory/count_descent.cpp -o tmp/cubic_round5/count_descent_lex
    python3 cubic_conjecture_search/verify_two_defect_search.py --counter tmp/cubic_round5/count_descent_lex
    clang++ -O3 -std=c++17 cubic_conjecture_search/exploratory/two_defect_bipartite.cpp -o tmp/cubic_round5/two_defect_bipartite
    tmp/cubic_round5/two_defect_bipartite cubic_conjecture_search/round5_data/two_defect26.txt

round5_search_results.json also records six fixed-template Z3 synthesis
runs at order 24, each ending UNSAT for its specified template only,
and 486,766 heuristic local-search evaluations. No formal UNSAT proof
files are retained. The count-only objective can decrease the number
of large good sets while increasing their maximum size; the two later
runs prioritize the maximum size before the count. None found a
counterexample. The sources and representative outputs are preserved.

Previous continuation
=====================
Two further results are now proved in bridge_completion/main.tex.

1. Replace every edge of a cubic multigraph B on n vertices by the
   specified twelve-vertex fragment R. The resulting graph I(B) is simple
   cubic and has

       |V(I(B))| = 19n,
       c_ind(I(B)) = 9n + nu_2(B),

   where nu_2 is ordinary vertex-disjoint cycle packing (not necessarily
   induced). A counting argument gives nu_2(B) >= n/2+1 for connected B;
   for bridgeless B, Petersen's theorem gives nu_2(B)=n. Consequently the
   half bound holds for the whole inflation class. An explicit family
   has order 38t+38 and exact c_ind=19t+20, attaining half plus one.

2. A nonuniform replacement criterion applies to every loopless bridgeless
   cubic base B, without an order bound. For each two-attachment fragment,
   let f(i,j) be its maximum doubled local surplus in boundary state (i,j),
   let C=max(f(0,0),f(0,1),f(1,0),f(1,1)), D=f(0,0), and A=f(2,2).
   If A is finite for every fragment and sum_edges(3C+D+2A) >= 0,
   the assembled graph satisfies the conjecture. The proof averages the
   construction with no selected base vertices and constructions from
   a distribution of perfect matchings with edge marginals 1/3, using
   Edmonds' matching-polytope theorem. Of the 27 independently verified
   retained fragments, all 21 with finite A satisfy the local inequality.
   Thus arbitrary choices and orientations from this library work over
   every bridgeless cubic base. Neither the inequality for all fragments
   nor the unrestricted conjecture has been established.

The complement identity is also proved: for every good set S in a
subcubic H, with T=V(H)-S,

    |S intersect V_3(H)| - (m-n) = |T| - |E(H[T])|.

This makes a pseudoforest complement a sufficient condition. Existence
of such a decomposition for arbitrary cubic graphs remains unproved.

New independent checks, using only Python's standard library:

    python3 cubic_conjecture_search/verify_edge_inflation.py
    python3 cubic_conjecture_search/verify_boundary_profiles.py
    python3 cubic_conjecture_search/verify_matching_criterion.py

They check the exact four-state table of R, 12 small auxiliary base
optima, 11 sharp-family members, all 27 retained two-port tables, their
21 matching inequalities, and 451 explicit good sets in 82 assemblies.
verify_bridge_reduction.py additionally checks 1,636 instances of the
complement identity on its 843 small labelled bases.

round4_search_results.json records further exploration, including:

* All 1,059,165 connected graphs of order 19 with one degree-two root
  and all other degrees three have root-excluded witnesses of size >=9
  and unrestricted witnesses of size >=10. The search stops after both
  lower bounds are witnessed, so it does not report every exact optimum.
* 4,781,904 fragile-edge tests on chains built from 111 boundary matrices
  found no doubled-cap counterexample. The two- and three-block cases
  were exhaustive for this library; longer sequences were heuristic.
* 1,000,000 random triangle compositions produced 130 additional three-port
  profiles. This was not an exhaustive closure calculation.
* A matrix closure attempt stopped at a resource guard with 20,002 active
  states. Its closure flag is false; it is not a proof of an invariant.
* All 45,982 connected cubic graphs through order 18 passed the stronger
  pseudoforest-complement test. This is a finite observation.
* Two- and four-port assembly searches found no certified counterexample.
  Some runs have FEASIBLE or UNKNOWN statuses. In particular the general
  four-port run was stopped with 15,400 recorded cases, including 20
  without a certified half-sized witness. Negative feasible objectives
  and UNKNOWN objective values are not evidence of a counterexample.
* Three counterexample-synthesis runs at order 24 were incomplete. Two
  were interrupted and the radius-four run timed out. None returned an
  UNSAT proof. An initial-labeling mismatch in the radius-eight run is
  recorded explicitly; the radius-four run corrected it.

These computations do not resolve the general conjecture. The new exact
theorems have complete proofs independent of heuristic search. No claim
of publication priority is made.

Example additional commands, from the repository root:

    mkdir -p tmp/cubic_round4
    clang++ -O3 -std=c++17 cubic_conjecture_search/exploratory/cap_cone.cpp -o tmp/cubic_round4/cap_cone
    geng -cq -d2 -D3 19 28:28 tmp/cubic_round4/caps19.g6
    tmp/cubic_round4/cap_cone tmp/cubic_round4/caps19.g6
    clang++ -O3 -std=c++17 cubic_conjecture_search/exploratory/edge_fragility.cpp -o tmp/cubic_round4/edge_fragility
    tmp/cubic_round4/edge_fragility cubic_conjecture_search/four_port_chain_profiles.txt

The other exploratory programs retain their scratch paths under
tmp/cubic_round4. three_pole_profiles.txt, two_pole_profiles.txt,
four_port_chain_profiles.txt, four_pole_network_profiles.json, and
triangle_records.txt preserve the representative data. The synthesis
scripts require the compiled enumerate_large oracle used by the earlier
searches. Four-port network searches read the chain library from
tmp/cubic_full/profiles_diag0.txt; the retained copy can be placed there.

Earlier continuation
====================
The paper now also proves pruning and suppression reductions: a smallest
counterexample to the subcubic branch inequality is connected, has minimum
degree two, and has its degree-two vertices in pairwise vertex-disjoint
triangles, each with two degree-three vertices. The proof also excludes
pendant cycles by an explicit good-set extension. Subdividing an
edge cannot decrease b_ind and preserves m-n. These facts leave the cubic
case unresolved.

For an odd-order attachment Q with one degree-two root, write A and B for
its largest good-set sizes with and without the root. Joining two copies
at their roots gives the exact optimum max(2B,A+B). This is another proved
counterexample criterion, not an attachment that violates the conjecture.

further_search_results.json records the latest completed searches:

* All 4,597,428 connected simple graphs with degrees in {2,3}, of orders
  3 through 17, satisfy b_ind >= m-n; 618 are equalities. The generator
  is geng -cq -d2 -D3 ORDER. Input SHA-256 hashes and counts are recorded.
  The subset search stops early only on a witness strictly above the
  target; reported equalities require exhausting all improving subsets.
* All 1,225,155 single-edge deletions from 45,982 connected cubic graphs
  through order 18 satisfy the branch inequality. The order-16 search
  also checked 925,680 pairs of independent deleted edges.
* 73,352 vertex-deletion fragments from cubic graphs through order 16
  reduce, under componentwise domination and port permutations, to 259
  retained profiles. All 202,020 two-fragment joins and 4,900 heuristic
  assemblies met the bound. Each heuristic optimization finished OPTIMAL.
* A further 9,000 edge-switch proposals on subcubic graphs with exactly
  two degree-two vertices, at orders 24, 26, and 42, found no violation.
  Their recorded branch minima were 12, 13, and 20, against targets
  11, 12, and 20. Every optimization finished OPTIMAL.

These results depend on the generator for isomorphism-class completeness;
the full branch census is not a collection of independently stored
witnesses. The retained fragment profiles ARE independently checked by
enumerating every subset in Python:

    python3 cubic_conjecture_search/verify_further_reductions.py

That standard-library verifier also checks 1,591 pruning cases and 1,803
good-set lifts across 1,011 suppressions, and verifies two obstructions to
stronger cover methods. A three-connected ten-vertex graph cannot be
covered by two good sets. For a specified sixteen-vertex graph, among all
111,930 four-multisets of good sets, exactly five cover every vertex twice;
each uses some edge three times. Neither graph violates the original
half-coverage conjecture. See further_reduction_checks.json.

Reproduce a branch search from the repository root, for example:

    mkdir -p tmp/cubic_round3
    clang++ -O3 -std=c++17 cubic_conjecture_search/exploratory/branch_search.cpp -o tmp/cubic_round3/branch_search
    geng -cq -d2 -D3 12 tmp/cubic_round3/subcubic12.g6
    tmp/cubic_round3/branch_search tmp/cubic_round3/subcubic12.g6

The exploratory three_pole_profiles.cpp accepts an output path followed
by cubic graph6 inputs. pole_assemblies.py reads the generated profiles
from tmp/cubic_round3/three_pole_profiles.txt; alternatively copy the
retained file from this directory to that path. rooted_tight_search.py
reproduces the rooted-edge and local branch searches. These scripts use
NetworkX and OR-Tools where indicated by their imports.

Structural continuation
=======================
bridge_completion/main.tex gives proofs of an exact completion formula
and an infinite equality family. The final PDF is
output/pdf/bridge_completion.pdf relative to the repository root.

For a subcubic graph H with n vertices and m edges, let b_ind(H) be the
maximum number of its degree-three vertices in a good set. Attach a fixed
13-vertex cap to each missing incidence, and put D=3n-2m. The resulting
cubic graph C(H) satisfies the proved identities

    |V(C(H))| = n+13D,
    c_ind(C(H)) = 7D+b_ind(H),
    c_ind(C(H)) - |V(C(H))|/2 = b_ind(H) - (m-n).

Thus the original conjecture is equivalent to b_ind(H) >= m-n for every
subcubic H. This is an exact reformulation; the new inequality remains
unproved in general. The paper also proves c_ind=8t+13 for explicit cubic
graphs with bridges of order 16t+26, for every integer t>=0. Their orders
preclude a square factor.

Run the independent finite checks with:

    python3 cubic_conjecture_search/verify_bridge_reduction.py

It checks the cap by exhaustive enumeration, completing witnesses for
all 843 labelled subcubic graphs on one through five vertices, and 13
members of the equality family. The optional verify_completion_solver.py
cross-checks seven full completion graphs with CP-SAT, using the general
bridge constraint but no attachment-specific upper bounds. Solver status
and bounds are recorded in completion_solver_results.json; time-limited
feasible results must not be read as proofs of optimality.

continuation_results.json records those checks and the later searches:
9,000 edge-switch proposals from tight graphs of orders 24, 26, and 42;
120 weighted fragment assemblies; and a floating-point weighted search
over all 39,866 bridgeless graphs among the 41,301 connected cubic graphs
of order 18. No counterexample was found. The order-18 and assembly
weighted searches are exploratory, not part of certificates.json.

Example continuation commands, run from the repository root:

    mkdir -p tmp/cubic_continue
    python3 cubic_conjecture_search/exploratory/tight_local_search.py 24 3000
    python3 cubic_conjecture_search/exploratory/weighted_assemblies.py

For the order-18 run, compile the existing subset enumerator to
tmp/cubic_full/cert_enumerator and finish generating the graph6 file
before running the search:

    geng -cq -d3 -D3 18 tmp/cubic_continue/cubic18.g6
    python3 cubic_conjecture_search/exploratory/weighted18.py

The continuation also records counterexamples to stronger proof-method
requirements (forcing a specified vertex or edge into a half-sized good
set, and synchronizing edge endpoints in a weighted cover). These are
not counterexamples to the original conjecture.

The conjecture asks whether every finite simple cubic graph G satisfies

    c_ind(G) >= |V(G)|/2,

where c_ind(G) is the largest number of vertices inducing a 2-regular
subgraph. Several mutually nonadjacent induced cycles are permitted.
The existing square-factor paper in this repository proves a restricted
case. None of the computations here extends that proof to all cubic graphs.

Literature checked
==================
Henning, Joos, Loewenstein, and Sasse, Induced Cycles in Graphs:
https://arxiv.org/abs/1406.0606

Knor, Sedlar, and Skrekovski, Counterexamples to two conjectures on
(1,2)-domination in cubic graphs, version 2, August 19, 2026:
https://arxiv.org/html/2608.17851
This paper explicitly leaves the original half-coverage conjecture open.
Its counterexamples concern stronger comparisons with a domination number.
It already reports searches over connected cubic graphs through order 22;
our unweighted computation through order 16 is not a new record.

Radic, Radic, and Tepeh, Structural aspects of 1-limited domination in
cubic graphs, October 19, 2026:
https://arxiv.org/html/2610.26259
This paper also presents the half-coverage statement as a conjecture.

Finite certificates
===================
certificates.json contains one record for each graph output by nauty's
geng -cq -d3 -D3 at the even orders from 4 through 16.

Order                 4     6     8    10    12    14     16    Total
Connected cubic       1     2     5    19    85   509   4060     4681
Bridgeless            1     2     5    18    81   480   3874     4461

Each record has an explicit good set containing at least half the vertices.
Every bridgeless record additionally has an exact rational fractional
cover of total coefficient at most two. These certificates prove the
following statement FOR EACH LISTED BRIDGELESS GRAPH:

    For every assignment of nonnegative weights to its vertices,
    some induced 2-regular subgraph contains at least half the weight.

This is a finite computational result, not a theorem for all bridgeless
cubic graphs. No publication-priority claim is made.

Why the certificates imply the weighted bound
-------------------------------------------
Let S_1,...,S_r be good sets and let lambda_1,...,lambda_r be nonnegative
rationals such that

    sum_i lambda_i <= 2,
    sum_{i: v in S_i} lambda_i >= 1  for every vertex v.

For any nonnegative vertex weights w, write W = sum_v w(v). Then

    W <= sum_i lambda_i w(S_i)
      <= (sum_i lambda_i) max_i w(S_i)
      <= 2 max_i w(S_i).

Thus one of the explicitly listed good sets has weight at least W/2.
The verifier checks every degree, coefficient, and coverage inequality
with exact integer or Fraction arithmetic. It does not trust a numerical
solver's claim of feasibility or optimality.

This weighted statement is deliberately restricted to bridgeless graphs.
In a cubic graph with bridges, a vertex incident only with bridges belongs
to no cycle; placing all weight there disproves the unrestricted weighted
statement. That does not disprove the unweighted conjecture.

Reproduce and verify
====================
Run from the repository root:

    python3 cubic_conjecture_search/verify_certificates.py

The independent verifier uses only Python's standard library. It checks
all 4,681 half-witnesses and all 4,461 fractional covers. Invalid witnesses,
invalid cover sets, and excessive total cover weights were also tested
and correctly rejected.
The C++ subset enumerator was also cross-checked against an independent
Python enumeration on all 112 connected cubic graphs through order 12;
their full lists of good sets agreed.

To regenerate the data, install OR-Tools and make nauty's geng and a C++17
compiler available, then run:

    python3 cubic_conjecture_search/generate_certificates.py

Generation enumerates all subsets in each input graph. Linear programming
proposes fractional covers, which are converted to rational numbers and
accepted only after exact checking. A failure to obtain such a cover is
reported as a failure of this procedure, not as a counterexample.

The generator's computed_maximum field records the exhaustive subset
enumeration's maximum. The independent verifier certifies only the lower
bound witnessed by half_witness; it does not re-enumerate subsets to prove
that computed_maximum is an upper bound. Completeness up to isomorphism
relies on geng. The verifier establishes the claims for the listed graphs
and checks that the recorded counts match; it does not independently
certify geng's isomorph-free enumeration.

Other searches
==============
exploratory/ preserves the search programs. They are experimental tools,
separate from the independent certificate verifier. Run them from the
repository root; their scratch files go in the ignored tmp/cubic_full/.
search_results.json records the completed runs and their limited scope.

1. Four-attachment fragments. Delete two independent edges of a small
   cubic graph, leaving four vertices of internal degree two. At each
   attachment, use states 0 (unselected), 1 (selected with internal degree
   two), and 2 (selected with internal degree one). A new attachment edge
   permits exactly (0,0), (0,1), (1,0), or (2,2). For each of the 81 states
   record the maximum local score 2|S|-n_fragment.

   Group two attachments on each side. The resulting 9 by 9 transfer
   matrix uses max-plus multiplication. For a cyclic sequence of blocks,
   the maximum diagonal entry of the product is exactly

       2 c_ind(assembled graph) - |V(assembled graph)|.

   A negative value would be a counterexample. None was found among the
   repeated blocks or mixed sequences tested. The 6,136,866 profiles are
   boundary-labelled cases, not that many nonisomorphic graphs. Arbitrary
   assemblies of all fragments were NOT exhaustively checked.

2. Local search. Starting from a 26-vertex trilobite, 3,000 proposals made
   one or two degree-preserving edge switches. The best candidate still
   had a good set of size 14, versus the required 13. A feasible solution
   alone is never treated as an upper bound. The search would flag a
   candidate counterexample only if the solver's upper bound were below
   half, and such a candidate would still need independent certification.

3. Weighted exploration. Column generation found no weighted violation
   in ten trilobites and 59 additional bridgeless random graphs of orders
   24, 30, and 40. These exploratory floating-point results are not among
   the exact certificates in certificates.json.

4. Three-attachment assemblies. Delete a cap vertex from a trilobite and
   compute all 27 boundary states exactly. The tested deletion types in
   trilobites with 1 through 8 claw layers produced two distinct
   normalized profiles. There were 700 random assemblies on cubic base
   graphs of orders 4, 6, 8, 10, 12, 16, and 20. All admitted good sets
   meeting the half bound. This does not cover all such assemblies.

Example exploratory commands
----------------------------
    mkdir -p tmp/cubic_full
    python3 cubic_conjecture_search/exploratory/local_search.py 4 3000
    python3 cubic_conjecture_search/exploratory/weighted_oracle.py
    python3 cubic_conjecture_search/exploratory/three_port_search.py

For a four-attachment run, first create a graph6 input with geng, then:

    clang++ -O3 -std=c++17 cubic_conjecture_search/exploratory/transfer_search.cpp -o tmp/cubic_full/transfer_search
    geng -cq -d3 -D3 12 tmp/cubic_full/cubic12.g6
    tmp/cubic_full/transfer_search tmp/cubic_full/cubic12.g6

minimal_profiles.cpp accepts an output path followed by graph6 inputs. It
retains componentwise minimal transfer matrices. mix_search.cpp accepts
a file in that output format. In the recorded run, the mixture search
used the 111 retained matrices whose largest diagonal entry was at most
zero. This restriction was a heuristic, not a completeness argument for
the full matrix family.

What remains missing
====================
There is no argument that constructs a half-sized good set in an arbitrary
cubic graph, and no graph with a certified smaller optimum. In particular,
the finite fractional covers have not been replaced by a construction
valid for arbitrary bridgeless cubic graphs, and extending a weighted
approach across bridges requires additional ideas. The full requested
proof or counterexample has not been obtained.
