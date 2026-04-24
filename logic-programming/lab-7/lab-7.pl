% lab-7.pl
:- use_module(library(plunit)).

% 1. triangle
triangle(0, 0) :- !.
triangle(N, T) :- N > 0, N1 is N - 1, triangle(N1, T1), T is T1 + N.

% 2. dot
dot([], [], 0) :- !.
dot([H1|T1], [H2|T2], P) :- dot(T1, T2, P1), P is P1 + H1 * H2.

% 3. polynom
polynom(E) :- polynom_ordered(E, _).
is_term(C * x^P, P) :- number(C), C \= 0, integer(P), P > 1, !.
is_term(x^P, P) :- integer(P), P > 1, !.
is_term(C * x, 1) :- number(C), C \= 0, !.
is_term(x, 1) :- !.
is_term(C, 0) :- number(C), C \= 0.

polynom_ordered(A + B, DegA) :- !, polynom_ordered(A, DegA), polynom_ordered(B, DegB), DegA > DegB.
polynom_ordered(Term, Deg) :- is_term(Term, Deg).

% 4. combination
combination(_, 0, []) :- !.
combination([H|T], K, [H|R]) :- K > 0, K1 is K - 1, combination(T, K1, R).
combination([_|T], K, R) :- K > 0, combination(T, K, R).

run_lab_tests :-
    run_tests,
    triangle(4, T), format("1. triangle: ~w~n", [T]),
    dot([1,2],[3,4], D), format("2. dot: ~w~n", [D]),
    (polynom(2*x^3 + x) -> format("3. polynom: yes~n")),
    findall(C, combination([1,2,3], 2, C), L), format("4. combinations: ~w~n", [L]).

:- begin_tests(lab7).
test(tri) :- triangle(4, 10).
test(dot) :- dot([1,2],[3,4], 11).
test(poly) :- polynom(2*x^2 + 1).
test(comb) :- findall(C, combination([1,2], 1, C), [[1],[2]]).
:- end_tests(lab7).
