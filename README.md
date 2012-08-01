pezmine
=======
Data mining [debugdb](http://github.com/debugdb) to find problems and
solutions.

pezmine builds clusters of problematic boards to identify common problems which
may be too subtle or infrequent for human detection.

Boards that have been fixed provide a mapping of problems (clusters) to
solutions.

Goals:

1. Identify common problems, so boards can be grouped appropriately
2. Mine knowledge on how to fix problems based on successful results

In principle, this should be able to tell you what is wrong and how to fix it
immediately upon testing a board.

Principles
----------
Test results (couchdb documents) are flattened into a key-value map. Each
key becomes a dimension in the "subspace" of the test, and numerical values
are treated as a position and used to compute a distance between pairs of
boards. This equal-weighting approach has pros (doesn't bias you against subtle
 problems) and cons (clusters are fuzzed out by statistical fluctuations).

The clustering properties of the *old* tests of fixed boards provide a means
to match problems and solutions. Fixed boards are tagged with the real
solution by a human.

Clustering across test subspaces without losing information is a work in
progress. Subspace clustering techniques seem appropriate, but will take
some thought.

The test subspaces are clustered via a modified k-means algorithm, where at
each iteration new nodes are generated for outliers given a threshold and
empty nodes are removed. This serves to isolate outliers regardless of their
number, which is what we want and isn't possible in traditional k-means
clustering. This will be improved with e.g. a fuzzy C-means version.

