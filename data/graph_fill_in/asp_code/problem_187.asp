
% Allocate exactly one color to each node
% This rule ensures that each node is assigned exactly one color
1{coloring(Node, Color): color(Color)}1 :- node(Node).

% Constraint to prevent two connected nodes (i.e., nodes connected by an edge) from having the same color
% This ensures that any valid coloring does not assign the same color to adjacent nodes
:- edge(Node1, Node2), coloring(Node1, Color), coloring(Node2, Color).

% Define predefined colorings for specific nodes
color(blue).
color(red).
color(yellow).
color(green).

% Define the nodes and edges in the graph
node(0).
node(1).
node(2).
node(3).
node(4).
node(5).
edge(0, 1).
edge(0, 2).
edge(1, 5).
edge(1, 2).
edge(2, 3).
edge(2, 4).
edge(2, 5).
edge(3, 4).
edge(3, 5).
edge(4, 5).
% Defining colored node facts
coloring(0,blue).
coloring(1,green).
coloring(2,red).
coloring(4,yellow).
coloring(5,blue).

% Ensure the grey node (node 3)is assigned exactly one color
1 { coloring(3,Color) : color(Color) } 1.
% Define the answer as the color of the grey node
answer(Color) :- coloring(3,Color).

% Output the final answer
#show answer/1.

