% family.pl
% Базовая база данных для Лабораторной работы 6

% parent(Родитель, Потомок)
parent(stephen, ivan).
parent(ivan, mary).
parent(ivan, alex).
parent(mary, lisa).

% предок_потомок(Предок, Потомок)
предок_потомок(X, Y) :- parent(X, Y).
предок_потомок(X, Y) :- parent(X, Z), предок_потомок(Z, Y).
