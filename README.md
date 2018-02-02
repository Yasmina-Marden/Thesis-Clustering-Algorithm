Thesis Clustering Algorithm
==============
Python implementation of clustering algorithm I designed as part of my undergraduate senior thesis at Reed College. An R script has been provided for easy visualization of clustering results (best when there are fewer than 100 nodes). A pdf of the pseudocode has also been provided.

Algorithm Overview
--------------
The algorithm is an ad-hoc, hierarchical clustering algorithm that allows overlap between clusters. It works on an input graph G, in iterations, where each iteration represents a level of the clustering hierarchy of G, starting from bottom to top.

During an iteration, all nodes are marked as unchecked, and a list of the nodes, L, is created, wherein the nodes are ordered from highest to lowest node degree. The first element (the node with the highest degree) is then selected as a seed for a cluster. Unchecked nodes are then checked and scored, starting with the nodes that are adjacent to the seed. (Marking nodes as checked and unchecked is done to prevent redundant score calculations.)

A node's score is first set to zero and then calculated by checking each of that node's adjacent nodes. For each of the adjacent nodes, if the adjacent node is (not) also adjacent to the seed, then the weight of edge connecting the node to the adjacent node is added to (subtracted from) the score. Then, if the node shares an edge with the seed and seed has no self-loop, the weight of that edge is added to the score. If the score is at least zero, the node is added to the current cluster and its adjacent nodes are recursively checked and scored. (A score of at least zero can roughly be interpreted as the corresponding node having at least half the same adjacencies as the seed.)

Once all the seed's adjacent nodes have been checked and scored, the cluster is complete and all nodes within the cluster that are in L are removed from L. After the removals, the new first element of L is set as the seed, all nodes are remarked as unchecked, and the checking and scoring process repeats to create a new cluster, until L is empty.

All the clusters made from L represent the clustering at the given iteration. Once L is empty, an iteration is complete and a new graph GNew is created, where the nodes are the clusters of the latest iteration's clustering and the edges preserve the node relationships of G. If GNew is the same as G, then there are no further iterations and we have reached the top of the clustering hierarchy. Else, G is set to GNew and a new iteration begins.