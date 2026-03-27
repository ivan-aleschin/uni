-module(lab4).

-export([run_tests/0, demo_ring/0, demo_parent_children/0, demo_par_filter/0]).

run_tests() ->
    io:format("=== Lab 4 demos ===~n"),
    demo_ring(),
    demo_parent_children(),
    demo_par_filter().

demo_ring() ->
    io:format("~n=== 1. ring ===~n"),
    io:format("Expected: token goes around the ring M times, then all finish.~n"),
    ring:ring(3, 2),
    ok.

demo_parent_children() ->
    io:format("~n=== 2. parent_children ===~n"),
    parent_children:start(3),
    parent_children:send_to_child(1, hello),
    parent_children:send_to_child(2, {msg, from_parent}),
    parent_children:send_to_child(3, die),
    timer:sleep(100),
    parent_children:send_to_child(3, revived),
    parent_children:send_to_child(2, stop),
    parent_children:stop(),
    timer:sleep(100),
    ok.

demo_par_filter() ->
    io:format("~n=== 3. par_filter ===~n"),
    F = fun(X) -> is_integer(X) andalso (X rem 2 =:= 0) end,
    List = [1,2,3,4,5,6,7,8,9,10,a,false,12],
    Options = [{sublist_size, 2}, {processes, 3}, {timeout, 2000}],
    Result = par_filter:par_filter(F, List, Options),
    io:format("Input : ~p~n", [List]),
    io:format("Result: ~p~n", [Result]),
    ok.
