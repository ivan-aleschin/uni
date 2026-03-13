-module(lab3_tree).

-export([empty/0, insert/2, member/2, to_list/1, from_list/1, split/2]).

%% Дерево: nil | {node, Value, Left, Right}
empty() ->
    nil.

insert(nil, X) ->
    {node, X, nil, nil};
insert({node, V, L, R}, X) when X < V ->
    {node, V, insert(L, X), R};
insert({node, V, L, R}, X) when X > V ->
    {node, V, L, insert(R, X)};
insert(T, _) ->
    T.  % уже есть

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
    lists:foldl(fun(X, T) -> insert(T, X) end, empty(), List).

%% split(Tree, X) -> {TreeLT, TreeGT}
%% TreeLT: все элементы < X, TreeGT: все элементы > X
split(nil, _) ->
    {nil, nil};
split({node, V, L, R}, X) when V < X ->
    {RLT, RGT} = split(R, X),
    {{node, V, L, RLT}, RGT};
split({node, V, L, R}, X) when V > X ->
    {LLT, LGT} = split(L, X),
    {LLT, {node, V, LGT, R}};
split({node, _, L, R}, _X) ->
    %% V =:= X: сам узел исключается, L < X, R > X
    {L, R}.
