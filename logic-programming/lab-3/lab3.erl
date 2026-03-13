-module(lab3).

-export([run_tests/0]).

run_tests() ->
    test_split(),
    test_set_bst(),
    test_set_list().

test_split() ->
    io:format("=== 1. split ===~n"),
    T = lab3_tree:from_list([5, 3, 7, 1, 4, 6, 8]),
    {LT, GT} = lab3_tree:split(T, 5),
    io:format("Tree:  ~w~n", [lab3_tree:to_list(T)]),
    io:format("split by 5:~n"),
    io:format("  LT (< 5) = ~w~n", [lab3_tree:to_list(LT)]),  % [1,3,4]
    io:format("  GT (> 5) = ~w~n", [lab3_tree:to_list(GT)]),  % [6,7,8]

    {LT2, GT2} = lab3_tree:split(T, 3),
    io:format("split by 3:~n"),
    io:format("  LT (< 3) = ~w~n", [lab3_tree:to_list(LT2)]),  % [1]
    io:format("  GT (> 3) = ~w~n", [lab3_tree:to_list(GT2)]).  % [4,5,6,7,8]

test_set_bst() ->
    io:format("~n=== BST Set ===~n"),
    S1 = lab3_set_bst:from_list([1, 2, 3, 4]),
    S2 = lab3_set_bst:from_list([2, 3, 4, 5, 6]),
    io:format("S1           = ~w~n", [lab3_set_bst:to_list(S1)]),
    io:format("S2           = ~w~n", [lab3_set_bst:to_list(S2)]),
    io:format("union        = ~w~n",
              [lab3_set_bst:to_list(
                   lab3_set_bst:union(S1, S2))]),
    io:format("intersection = ~w~n",
              [lab3_set_bst:to_list(
                   lab3_set_bst:intersection(S1, S2))]),
    io:format("difference   = ~w~n",
              [lab3_set_bst:to_list(
                   lab3_set_bst:difference(S1, S2))]),
    Sub = lab3_set_bst:from_list([2, 3]),
    io:format("is_subset([2,3], S1) = ~w~n", [lab3_set_bst:is_subset(Sub, S1)]),  % true
    io:format("is_subset(S1, Sub)   = ~w~n", [lab3_set_bst:is_subset(S1, Sub)]).  % false

test_set_list() ->
    io:format("~n=== List Set ===~n"),
    S1 = lab3_set_list:from_list([1, 2, 3, 4]),
    S2 = lab3_set_list:from_list([2, 3, 4, 5, 6]),
    io:format("S1           = ~w~n", [lab3_set_list:to_list(S1)]),
    io:format("S2           = ~w~n", [lab3_set_list:to_list(S2)]),
    io:format("union        = ~w~n",
              [lab3_set_list:to_list(
                   lab3_set_list:union(S1, S2))]),
    io:format("intersection = ~w~n",
              [lab3_set_list:to_list(
                   lab3_set_list:intersection(S1, S2))]),
    io:format("difference   = ~w~n",
              [lab3_set_list:to_list(
                   lab3_set_list:difference(S1, S2))]),
    Sub = lab3_set_list:from_list([2, 3]),
    io:format("is_subset([2,3], S1) = ~w~n", [lab3_set_list:is_subset(Sub, S1)]),  % true
    io:format("is_subset(S1, Sub)   = ~w~n", [lab3_set_list:is_subset(S1, Sub)]).  % false
