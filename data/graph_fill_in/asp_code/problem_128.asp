
% Allocate exactly one color to each node
% This rule ensures that each node is assigned exactly one color
1{coloring(Node, Color): color(Color)}1 :- node(Node).

% Constraint to prevent two connected nodes (i.e., nodes connected by an edge) from having the same color
% This ensures that any valid coloring does not assign the same color to adjacent nodes
:- edge(Node1, Node2), coloring(Node1, Color), coloring(Node2, Color).

% Define predefined colorings for specific nodes
color(yellow).
color(red).
color(blue).
color(green).

% Define the nodes and edges in the graph
node(0).
node(1).
node(2).
node(3).
node(4).
node(5).
edge(0, 3).
edge(0, 2).
edge(1, 3).
edge(1, 2).
edge(1, 4).
edge(2, 4).
edge(2, 3).
edge(3, 4).
edge(4, 5).
% Defining colored node facts
coloring(0,green).
coloring(1,yellow).
coloring(2,red).
coloring(3,blue).
coloring(5,red).

% Ensure the grey node (node 4)is assigned exactly one color
1 { coloring(4,Color) : color(Color) } 1.
% Define the answer as the color of the grey node
answer(Color) :- coloring(4,Color).

% Output the final answer
#show answer/1.
