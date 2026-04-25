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
    % Run unit tests first
    run_tests,
    triangle(4, T), format("1. triangle: ~w~n", [T]),
    dot([1,2],[3,4], D), format("2. dot: ~w~n", [D]),
    (polynom(2*x^3 + x) -> format("3. polynom: yes~n")),
    findall(C, combination([1,2,3], 2, C), L), format("4. combinations: ~w~n", [L]),

    format("~n--- Operator experiments ---~n", []),

    % 1) X = 1+2.
    format("?- X = 1+2.~n", []),
    (   catch((X = 1+2, format("   true. X = ~w~n", [X])), E, format("   error: ~w~n", [E]))
    ->  true
    ;   true
    ),

    % 2) 3 = 1+2.
    format("?- 3 = 1+2.~n", []),
    catch(( (3 = 1+2 -> format("   true.~n", []); format("   false.~n", [])) ), E, format("   error: ~w~n", [E])),

    % 3) 2+1 = 1+2.
    format("?- 2+1 = 1+2.~n", []),
    catch(( ( (2+1) = (1+2) -> format("   true.~n", []); format("   false.~n", [])) ), E, format("   error: ~w~n", [E])),

    % 4) X == 1+2.
    format("?- X == 1+2.~n", []),
    catch(( (X == 1+2 -> format("   true.~n", []); format("   false.~n", [])) ), E, format("   error: ~w~n", [E])),

    % 5) 3 == 1+2.
    format("?- 3 == 1+2.~n", []),
    catch(( (3 == 1+2 -> format("   true.~n", []); format("   false.~n", [])) ), E, format("   error: ~w~n", [E])),

    % 6) 2+1 == 1+2.
    format("?- 2+1 == 1+2.~n", []),
    catch(( ((2+1) == (1+2) -> format("   true.~n", []); format("   false.~n", [])) ), E, format("   error: ~w~n", [E])),

    % 7) X =:= 1+2.
    format("?- X =:= 1+2.~n", []),
    catch(( (X =:= 1+2 -> format("   true.~n", []); format("   false.~n", [])) ), E, format("   error: ~w~n", [E])),

    % 8) 3 =:= 1+2.
    format("?- 3 =:= 1+2.~n", []),
    catch(( (3 =:= 1+2 -> format("   true.~n", []); format("   false.~n", [])) ), E, format("   error: ~w~n", [E])),

    % 9) 2+1 =:= 1+2.
    format("?- 2+1 =:= 1+2.~n", []),
    catch(( ((2+1) =:= (1+2) -> format("   true.~n", []); format("   false.~n", [])) ), E, format("   error: ~w~n", [E])),

    % 10) X is 1+2.
    format("?- X is 1+2.~n", []),
    (   catch((X is 1+2, format("   true. X = ~w~n", [X])), E, format("   error: ~w~n", [E]))
    ->  true
    ;   true
    ),

    % 11) 3 is 1+2.
    format("?- 3 is 1+2.~n", []),
    catch(( (3 is 1+2 -> format("   true.~n", []); format("   false.~n", [])) ), E, format("   error: ~w~n", [E])),

    % 12) 2+1 is 1+2.
    format("?- 2+1 is 1+2.~n", []),
    catch(( ((2+1) is (1+2) -> format("   true.~n", []); format("   false.~n", [])) ), E, format("   error: ~w~n", [E])).

:- begin_tests(lab7).
test(tri) :- triangle(4, 10).
test(dot) :- dot([1,2],[3,4], 11).
test(poly) :- polynom(2*x^2 + 1).
test(comb) :- findall(C, combination([1,2], 1, C), [[1],[2]]).

% Operator behavior tests (safe checks that do not raise instantiation errors)
test(op_is_bind) :- X is 1+2, X =:= 3.
test(op_eval_numeric) :- 3 =:= 1+2.
test(op_eval_commute) :- (2+1) =:= (1+2).
test(op_unify_term) :- X = 1+2, X == 1+2.

:- end_tests(lab7).
