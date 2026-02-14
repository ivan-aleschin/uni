% ============================================================
% Лабораторная работа 1 — Вариант 1
% ============================================================

% ------------------------------------------------------------
% 1. Объём шара: ball_volume(+R, -V)
%    ball_volume(1.0, V) => V = 4.1887902...
% ------------------------------------------------------------
ball_volume(R, V) :-
    V is (4.0 / 3.0) * pi * R * R * R.


% ------------------------------------------------------------
% 2. Список целых от N до M: from_to(+N, +M, -List)
%    from_to(1, 4, L) => L = [1, 2, 3, 4]
% ------------------------------------------------------------
from_to(N, M, []) :-
    N > M, !.
from_to(N, M, [N|T]) :-
    N1 is N + 1,
    from_to(N1, M, T).


% ------------------------------------------------------------
% 3. Разности с предыдущим: delta(+List, -DeltaList)
%    delta([1,2,4,3], D) => D = [1,1,2,-1]
% ------------------------------------------------------------
delta([], []).
delta([H|T], [H|D]) :-
    delta_aux(H, T, D).

delta_aux(_, [], []).
delta_aux(Prev, [H|T], [Diff|Rest]) :-
    Diff is H - Prev,
    delta_aux(H, T, Rest).


% ------------------------------------------------------------
% 4. Двоичная строка: int_to_binary(+N, -S)
%    int_to_binary(8, S)  => S = "1000"
%    int_to_binary(-2, S) => S = "-10"
% ------------------------------------------------------------
int_to_binary(0, "0") :- !.
int_to_binary(N, S) :-
    N > 0, !,
    format(atom(A), '~2r', [N]),
    atom_string(A, S).
int_to_binary(N, S) :-
    N < 0,
    N1 is -N,
    format(atom(A), '~2r', [N1]),
    atom_string(A, S1),
    string_concat("-", S1, S).


% ------------------------------------------------------------
% 5. RLE кодирование: rle_encode(+List, -Encoded)
%    rle_encode([a,a,a,b,c,c,a,a], E)
%    => E = [{a,3}, b, {c,2}, {a,2}]
% ------------------------------------------------------------
rle_encode([], []).
rle_encode([H|T], Encoded) :-
    rle_run(H, T, 1, Count, Rest),
    ( Count =:= 1
    -> Encoded = [H | RestEncoded]
    ;  Encoded = [{H, Count} | RestEncoded]
    ),
    rle_encode(Rest, RestEncoded).

rle_run(_, [], Count, Count, []).
rle_run(Elem, [H|T], Acc, Count, Rest) :-
    ( Elem == H
    -> Acc1 is Acc + 1,
       rle_run(Elem, T, Acc1, Count, Rest)
    ;  Count = Acc,
       Rest = [H|T]
    ).


% ------------------------------------------------------------
% Демонстрация всех задач одной командой
% ------------------------------------------------------------
run_tests :-
    % 1
    ball_volume(1.0, V),
    format("1. ball_volume(1.0) = ~f~n", [V]),

    % 2
    from_to(1, 4, L),
    format("2. from_to(1, 4) = ~w~n", [L]),

    % 3
    delta([1,2,4,3], D),
    format("3. delta([1,2,4,3]) = ~w~n", [D]),

    % 4
    int_to_binary(8, B1),
    int_to_binary(-2, B2),
    int_to_binary(0, B0),
    format("4. int_to_binary(8)  = ~w~n", [B1]),
    format("   int_to_binary(-2) = ~w~n", [B2]),
    format("   int_to_binary(0)  = ~w~n", [B0]),

    % 5
    rle_encode([a,a,a,b,c,c,a,a], E),
    format("5. rle_encode([a,a,a,b,c,c,a,a]) = ~w~n", [E]).
