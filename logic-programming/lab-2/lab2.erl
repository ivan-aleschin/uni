-module(lab2).

-export([sum_neg_squares/1, dropwhile/2, antimap/2, solve/4, for/4, sort_by/2,
         run_tests/0]).

%% 1. Сумма квадратов отрицательных чисел
sum_neg_squares([]) ->
    0;
sum_neg_squares([H | T]) when is_number(H), H < 0 ->
    H * H + sum_neg_squares(T);
sum_neg_squares([_ | T]) ->
    sum_neg_squares(T).

%% 2. Отбросить начальные элементы, пока Pred истинен
dropwhile(_, []) ->
    [];
dropwhile(Pred, [H | T]) ->
    case Pred(H) of
        true ->
            dropwhile(Pred, T);
        false ->
            [H | T]
    end.

%% 3. Применить список функций к одному аргументу
antimap([], _) ->
    [];
antimap([F | Fs], X) ->
    [F(X) | antimap(Fs, X)].

%% 4. Метод бисекции: найти корень Fun(X) = 0 на [A, B] с точностью Eps
solve(_Fun, A, B, Eps) when B - A < Eps ->
    (A + B) / 2;
solve(Fun, A, B, Eps) ->
    Mid = (A + B) / 2,
    case Fun(Mid) =< 0 of
        true ->
            solve(Fun, Mid, B, Eps);
        false ->
            solve(Fun, A, Mid, Eps)
    end.

%% 5. Цикл for: for(Init, Cond, Step, Body)
for(Init, Cond, Step, Body) ->
    case Cond(Init) of
        false ->
            ok;
        true ->
            Body(Init),
            for(Step(Init), Cond, Step, Body)
    end.

%% 6. Сортировка слиянием с пользовательским компаратором
sort_by(_, []) ->
    [];
sort_by(_, [X]) ->
    [X];
sort_by(Cmp, List) ->
    {Left, Right} = split(List),
    merge_by(Cmp, sort_by(Cmp, Left), sort_by(Cmp, Right)).

split(List) ->
    split(List, [], []).

split([], L, R) ->
    {L, R};
split([X], L, R) ->
    {[X | L], R};
split([X, Y | T], L, R) ->
    split(T, [X | L], [Y | R]).

merge_by(_, [], R) ->
    R;
merge_by(_, L, []) ->
    L;
merge_by(Cmp, [H1 | T1] = L, [H2 | T2] = R) ->
    case Cmp(H1, H2) of
        greater ->
            [H2 | merge_by(Cmp, L, T2)];
        _ ->
            [H1 | merge_by(Cmp, T1, R)]
    end.

%% Тесты
run_tests() ->
    %% 1
    R1 = sum_neg_squares([-3, a, false, -3, 1]),
    io:format("1. ~w~n", [R1]),         % => 18

    %% 2
    R2 = dropwhile(fun(X) -> X < 10 end, [1, 3, 9, 11, 6]),
    io:format("2. ~w~n", [R2]),         % => [11, 6]

    %% 3
    R3 = antimap([fun(X) -> X + 2 end, fun(X) -> X * 3 end], 4),
    io:format("3. ~w~n", [R3]),         % => [6, 12]

    %% 4
    R4 = solve(fun(X) -> X * X - 2 end, 0, 2, 0.001),
    io:format("4. ~f~n", [R4]),         % => ~1.41421...

    %% 5
    io:format("5. for loop output: "),
    for(1, fun(I) -> I =< 5 end, fun(I) -> I + 1 end, fun(I) -> io:format("~w ", [I]) end),
    io:format("~n"),                    % => 1 2 3 4 5

    %% 6
    Cmp = fun(X, Y) ->
             if X < Y -> less;
                X > Y -> greater;
                true -> equal
             end
          end,
    R6 = sort_by(Cmp, [3, 1, 4, 1, 5, 9, 2, 6]),
    io:format("6. ~w~n", [R6]).         % => [1,1,2,3,4,5,6,9]
