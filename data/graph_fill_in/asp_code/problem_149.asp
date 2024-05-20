
% Allocate exactly one color to each node
% This rule ensures that each node is assigned exactly one color
1{coloring(Node, Color): color(Color)}1 :- node(Node).

% Constraint to prevent two connected nodes (i.e., nodes connected by an edge) from having the same color
% This ensures that any valid coloring does not assign the same color to adjacent nodes
:- edge(Node1, Node2), coloring(Node1, Color), coloring(Node2, Color).

% Define predefined colorings for specific nodes
color(red).
color(yellow).
color(blue).
color(green).

% Define the nodes and edges in the graph
node(0).
node(1).
node(2).
node(3).
node(4).
node(5).
edge(0, 5).
edge(0, 4).
edge(1, 2).
edge(1, 3).
edge(1, 4).
edge(1, 5).
edge(2, 4).
edge(2, 3).
edge(2, 5).
edge(3, 4).
edge(3, 5).
% Defining colored node facts
coloring(0,red).
coloring(1,red).
coloring(2,blue).
coloring(3,green).
coloring(4,yellow).

% Ensure the grey node (node 5)is assigned exactly one color
1 { coloring(5,Color) : color(Color) } 1.
% Define the answer as the color of the grey node
answer(Color) :- coloring(5,Color).

% Output the final answer
#show answer/1.

