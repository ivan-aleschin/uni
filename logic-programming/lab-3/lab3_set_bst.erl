%% Реализация множества через двоичное дерево поиска (BST).
%% Интерфейс: new, add, remove, member, union, intersection, difference,
%%            to_list, from_list, is_subset, size.
-module(lab3_set_bst).

-export([new/0, add/2, remove/2, member/2, union/2, intersection/2, difference/2,
         to_list/1, from_list/1, is_subset/2, size/1]).

%% Дерево: nil | {node, Value, Left, Right}

new() ->
    nil.

add(nil, X) ->
    {node, X, nil, nil};
add({node, V, L, R}, X) when X < V ->
    {node, V, add(L, X), R};
add({node, V, L, R}, X) when X > V ->
    {node, V, L, add(R, X)};
add(T, _) ->
    T.

remove(nil, _) ->
    nil;
remove({node, V, L, R}, X) when X < V ->
    {node, V, remove(L, X), R};
remove({node, V, L, R}, X) when X > V ->
    {node, V, L, remove(R, X)};
remove({node, _, nil, R}, _) ->
    R;
remove({node, _, L, nil}, _) ->
    L;
remove({node, _, L, R}, _) ->
    %% Заменяем на минимальный элемент правого поддерева
    Min = min_node(R),
    {node, Min, L, remove(R, Min)}.

min_node({node, V, nil, _}) ->
    V;
min_node({node, _, L, _}) ->
    min_node(L).

member(nil, _) ->
    false;
member({node, V, _, _}, X) when X =:= V ->
    true;
member({node, V, L, _}, X) when X < V ->
    member(L, X);
member({node, _, _, R}, X) ->
    member(R, X).

to_list(nil) ->
    [];
to_list({node, V, L, R}) ->
    to_list(L) ++ [V] ++ to_list(R).

from_list(List) ->
    lists:foldl(fun(X, T) -> add(T, X) end, new(), List).

union(T1, T2) ->
    %% Добавляем все элементы T2 в T1
    lists:foldl(fun(X, T) -> add(T, X) end, T1, to_list(T2)).

intersection(T1, T2) ->
    from_list([X || X <- to_list(T1), member(T2, X)]).

difference(T1, T2) ->
    from_list([X || X <- to_list(T1), not member(T2, X)]).

is_subset(T1, T2) ->
    lists:all(fun(X) -> member(T2, X) end, to_list(T1)).

size(T) ->
    length(to_list(T)).
