
% Define the domain for the Sudoku problem
% x and y are the coordinates (rows and columns) ranging from 1 to 9
x(1..9).
y(1..9).

% n represents the possible values for each cell, ranging from 1 to 9
n(1..9).

% Each cell (X, Y) must have exactly one value N from 1 to 9
% This rule ensures that for each (X, Y) pair, there is exactly one N such that sudoku(X,Y,N) holds true
{sudoku(X,Y,N) : n(N)}=1 :- x(X), y(Y).

% Define a predicate to represent cells that belong to the same 3x3 subgrid
% subgrid(X,Y,A,B) is true if cells (X,Y) and (A,B) are in the same subgrid
subgrid(X,Y,A,B) :- x(X), x(A), y(Y), y(B), (X-1)/3 == (A-1)/3, (Y-1)/3 == (B-1)/3.

% Constraints to ensure the validity of the Sudoku solution

% Constraint ensuring no two cells in the same row (Y) have the same value (N)
:- sudoku(X,Y,N), sudoku(A,Y,N), X != A.

% Constraint ensuring no two cells in the same column (X) have the same value (N)
:- sudoku(X,Y,N), sudoku(X,B,N), Y != B.

% Constraint ensuring no two cells in the same 3x3 subgrid have the same value (V)
:- sudoku(X,Y,V), sudoku(A,B,V), subgrid(X,Y,A,B), X != A, Y != B.

% Defining the initial Sudoku grid
sudoku(1,1,7). sudoku(1,2,3). sudoku(1,3,2). sudoku(1,4,5). sudoku(1,5,6). sudoku(1,6,4). sudoku(1,7,9). sudoku(1,8,1). sudoku(1,9,8). sudoku(2,1,9). sudoku(2,2,8). sudoku(2,3,5). sudoku(2,4,2). sudoku(2,5,1). sudoku(2,6,3). sudoku(2,7,4). sudoku(2,8,6). sudoku(2,9,7). sudoku(3,1,4). sudoku(3,2,6). sudoku(3,3,1). sudoku(3,4,8). sudoku(3,5,9). sudoku(3,6,7). sudoku(3,7,5). sudoku(3,8,2). sudoku(3,9,3). sudoku(4,1,5). sudoku(4,2,9). sudoku(4,3,6). sudoku(4,4,1). sudoku(4,5,7). sudoku(4,6,8). sudoku(4,7,3). sudoku(4,8,4). sudoku(4,9,2). sudoku(5,1,2). sudoku(5,2,4). sudoku(5,4,3). sudoku(5,5,5). sudoku(5,6,6). sudoku(5,7,7). sudoku(5,8,9). sudoku(5,9,1). sudoku(6,1,3). sudoku(6,2,1). sudoku(6,3,7). sudoku(6,4,4). sudoku(6,5,2). sudoku(6,6,9). sudoku(6,7,6). sudoku(6,8,8). sudoku(6,9,5). sudoku(7,1,6). sudoku(7,2,2). sudoku(7,3,3). sudoku(7,4,7). sudoku(7,5,4). sudoku(7,6,1). sudoku(7,7,8). sudoku(7,8,5). sudoku(7,9,9). sudoku(8,1,1). sudoku(8,2,7). sudoku(8,3,4). sudoku(8,4,9). sudoku(8,5,8). sudoku(8,6,5). sudoku(8,7,2). sudoku(8,8,3). sudoku(8,9,6). sudoku(9,1,8). sudoku(9,2,5). sudoku(9,3,9). sudoku(9,4,6). sudoku(9,5,3). sudoku(9,6,2). sudoku(9,7,1). sudoku(9,8,7). sudoku(9,9,4). 
% Find the missing number in cell (5,3)
1 { sudoku(5,3,N) : n(N) } 1.

% Define the answer predicate to store the missing number
answer(N) :- sudoku(5,3,N).
#show answer/1.
