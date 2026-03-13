%% Реализация множества через отсортированный список.
%% Тот же интерфейс что и lab3_set_bst.
-module(lab3_set_list).

-export([new/0, add/2, remove/2, member/2, union/2, intersection/2, difference/2,
         to_list/1, from_list/1, is_subset/2, size/1]).

new() ->
    [].

add([], X) ->
    [X];
add([H | _] = S, X) when X < H ->
    [X | S];
add([H | T], X) when X > H ->
    [H | add(T, X)];
add(S, _) ->
    S.  % X =:= H, уже есть

remove([], _) ->
    [];
remove([H | T], X) when H =:= X ->
    T;
remove([H | T], X) when H < X ->
    [H | remove(T, X)];
remove(S, _) ->
    S.  % H > X, не найден

member([], _) ->
    false;
member([H | _], X) when H =:= X ->
    true;
member([H | T], X) when H < X ->
    member(T, X);
member(_, _) ->
    false.

%% Слияние двух отсортированных списков без дубликатов
union([], S) ->
    S;
union(S, []) ->
    S;
union([H | T1], [H | T2]) ->
    [H | union(T1, T2)];
union([H1 | T1], [H2 | _] = S) when H1 < H2 ->
    [H1 | union(T1, S)];
union(S, [H2 | T2]) ->
    [H2 | union(S, T2)].

intersection([], _) ->
    [];
intersection(_, []) ->
    [];
intersection([H1 | T1], [H2 | T2]) when H1 < H2 ->
    intersection(T1, [H2 | T2]);
intersection([H1 | T1], [H2 | T2]) when H1 > H2 ->
    intersection([H1 | T1], T2);
intersection([H | T1], [_ | T2]) ->
    [H | intersection(T1, T2)].

difference([], _) ->
    [];
difference(S, []) ->
    S;
difference([H1 | T1], [H2 | T2]) when H1 < H2 ->
    [H1 | difference(T1, [H2 | T2])];
difference([H1 | T1], [H2 | T2]) when H1 > H2 ->
    difference([H1 | T1], T2);
difference([_ | T1], [_ | T2]) ->
    difference(T1, T2).

to_list(S) ->
    S.

from_list(List) ->
    lists:foldl(fun(X, S) -> add(S, X) end, new(), List).

%% is_subset: все элементы S1 содержатся в S2
%% Используем слияние: если S1 ⊆ S2, каждый элемент S1 найдётся в S2
is_subset([], _) ->
    true;
is_subset(_, []) ->
    false;
is_subset([H1 | T1], [H2 | T2]) when H1 > H2 ->
    is_subset([H1 | T1], T2);
is_subset([H | T1], [H | T2]) ->
    is_subset(T1, T2);
is_subset(_, _) ->
    false.  % H1 < H2: элемент S1 не нашёлся

size(S) ->
    length(S).
