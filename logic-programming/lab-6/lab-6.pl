% lab-6.pl
:- consult('family.pl').
:- use_module(library(plunit)).

% 2. zip
zip([], [], []).
zip([H1|T1], [H2|T2], [[H1,H2]|T3]) :- zip(T1, T2, T3).

% 3. duplicates
contains_duplicates(L) :- append(_, [X|T], L), member(X, T), !.

% 4. flatten
my_flatten([], []) :- !.
my_flatten([H|T], Flat) :- !, my_flatten(H, FH), my_flatten(T, FT), append(FH, FT, Flat).
my_flatten(X, [X]).

% 5. gray
gray([], [[]]) :- !.
gray([_|T], Code) :-
    gray(T, Prev), reverse(Prev, Rev),
    map_prefix(0, Prev, P0), map_prefix(1, Rev, P1),
    append(P0, P1, Code).

map_prefix(_, [], []) :- !.
map_prefix(P, [H|T], [[P|H]|RT]) :- map_prefix(P, T, RT).

run_lab_tests :-
    run_tests,
    zip([a,b], [1,2], Z), format("2. zip: ~w~n", [Z]),
    (contains_duplicates([a,b,a]) -> format("3. duplicates: yes~n")),
    my_flatten([a, [b, [c]]], F), format("4. flatten: ~w~n", [F]),
    gray([0,0], G), format("5. gray: ~w~n", [G]).

:- begin_tests(lab6).
test(zip) :- zip([a],[1],[[a,1]]).
test(zip_var) :- zip([A,B],[1,2],[[A,1],[B,2]]).
test(dups) :- contains_duplicates([a,a]).
test(dups_vars) :- contains_duplicates([X,a,X]).
test(flat) :- my_flatten([a,[b]], [a,b]).
test(flat_deep) :- my_flatten([a, [[b], c], [[d]]], [a,b,c,d]).
test(gray) :- gray([0], [[0],[1]]).
test(gray2) :- gray([0,0], [[0,0],[0,1],[1,1],[1,0]]).
test(predok_stephen_mary) :- предок_потомок(stephen, mary).
test(predok_ivan_lisa) :- предок_потомок(ivan, lisa).
:- end_tests(lab6).
