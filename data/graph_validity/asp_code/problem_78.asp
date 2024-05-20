
% Allocate exactly one color to each node
% This rule ensures that each node is assigned exactly one color
1{coloring(Node, Color): color(Color)}1 :- node(Node).

% Constraint to prevent two connected nodes (i.e., nodes connected by an edge) from having the same color
% This ensures that any valid coloring does not assign the same color to adjacent nodes
:- edge(Node1, Node2), coloring(Node1, Color), coloring(Node2, Color).

% Define predefined colorings for specific nodes
color(yellow).
color(orange).
color(red).
color(green).
color(blue).

% Define the nodes and edges in the graph
node(0).
node(1).
node(2).
node(3).
node(4).
edge(0, 3).
edge(0, 2).
edge(0, 1).
edge(1, 4).
edge(2, 4).
edge(2, 3).
edge(3, 4).
