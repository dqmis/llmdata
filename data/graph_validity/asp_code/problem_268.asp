
% Allocate exactly one color to each node
% This rule ensures that each node is assigned exactly one color
1{coloring(Node, Color): color(Color)}1 :- node(Node).

% Constraint to prevent two connected nodes (i.e., nodes connected by an edge) from having the same color
% This ensures that any valid coloring does not assign the same color to adjacent nodes
:- edge(Node1, Node2), coloring(Node1, Color), coloring(Node2, Color).

% Define predefined colorings for specific nodes
color(purple).
color(blue).
color(green).
color(yellow).
color(orange).

% Define the nodes and edges in the graph
node(0).
node(1).
node(2).
node(3).
node(4).
node(5).
edge(0, 3).
edge(1, 3).
edge(1, 2).
edge(2, 5).
edge(4, 5).
