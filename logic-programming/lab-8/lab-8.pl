% lab-8.pl
:- use_module(library(plunit)).

% 1. nu (not unifiable) через ! и fail
% Если X и Y унифицируются — отсекаем альтернативы и вызываем fail.
nu(X, X) :- !, fail.
nu(_, _).

% 2. abs (абсолютное значение) с зеленым отсечением
% ! указывает, что если X >= 0, то второй клоз проверять не нужно.
abs(X, X) :- X >= 0, !.
abs(X, Y) :- X < 0, Y is -X.

% 3. set_union (объединение множеств)
% Если голова H есть во втором списке — пропускаем её (она уже там есть).
set_union([], L2, L2).
set_union([H|T], L2, Res) :- member(H, L2), !, set_union(T, L2, Res).
set_union([H|T], L2, [H|Res]) :- set_union(T, L2, Res).

% 5. unifiable (проверка унифицируемости без связывания переменных)
% \+ \+ (H = Term) проверяет, возможна ли унификация, а затем откатывает связи.
unifiable([], _, []).
unifiable([H|T], Term, [H|Rest]) :- \+ \+ (H = Term), !, unifiable(T, Term, Rest).
unifiable([_|T], Term, Rest) :- unifiable(T, Term, Rest).

run_lab_tests :-
    run_tests,
    format("--- Задание 1: nu ---~n"),
    (nu(a, b) -> format("1. nu(a, b): yes~n")),
    (nu(X, X) -> true; format("2. nu(X, X): no~n")),

    format("~n--- Задание 2: abs ---~n"),
    abs(-10, A), format("3. abs(-10): ~w~n", [A]),

    format("~n--- Задание 3: set_union ---~n"),
    set_union([1,2,3,4,5], [3,5,6,7,8], U),
    format("4. set_union([1..5], [3..8]): ~w~n", [U]),

    format("~n--- Задание 5: unifiable ---~n"),
    % Используем _X и _Y, чтобы избежать Singleton Warnings
    unifiable([_X, b, t(_Y)], t(a), List),
    format("5. unifiable([X, b, t(Y)], t(a)): ~p~n", [List]).

:- begin_tests(lab8).
test(nu) :- \+ nu(a, a).
test(abs) :- abs(-5, 5).
test(union) :- set_union([1,2], [2,3], [1,2,3]).
test(unif) :- unifiable([X], a, [X]), var(X).
:- end_tests(lab8).
