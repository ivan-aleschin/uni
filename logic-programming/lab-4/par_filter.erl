-module(par_filter).

-export([par_filter/3]).

%% par_filter(F, List, Options) -> FilteredList (order not guaranteed)
%% Options:
%%   {sublist_size, integer()}
%%   {processes, integer()}
%%   {timeout, Milliseconds | infinity}
%% Defaults:
%%   sublist_size = 1
%%   processes = parts count
%%   timeout = infinity

par_filter(F, List, Options) ->
    SubSize = opt(sublist_size, Options, 1),
    Timeout = opt(timeout, Options, infinity),
    Parts = split_list(List, SubSize),
    ProcCount = opt(processes, Options, length(Parts)),
    WorkerCount = erlang:max(0, erlang:min(ProcCount, length(Parts))),
    case WorkerCount of
        0 ->
            lists:append([lists:filter(F, Part) || Part <- Parts]);
        _ ->
            Parent = self(),
            Pids = spawn_workers(WorkerCount, Parent, F),
            Results = collect_results(Parts, Pids, Timeout),
            lists:append(Results)
    end.

%% Helpers

opt(Key, Options, Default) ->
    case lists:keyfind(Key, 1, Options) of
        false -> Default;
        {Key, Value} -> Value
    end.

split_list(List, N) when N =< 1 ->
    [[X] || X <- List];
split_list(List, N) ->
    split_list(List, N, []).

split_list([], _N, Acc) ->
    lists:reverse(Acc);
split_list(List, N, Acc) ->
    {Chunk, Rest} = take_n(List, N),
    split_list(Rest, N, [Chunk | Acc]).

take_n(List, N) ->
    take_n(List, N, []).

take_n(Rest, 0, Acc) ->
    {lists:reverse(Acc), Rest};
take_n([], _N, Acc) ->
    {lists:reverse(Acc), []};
take_n([H | T], N, Acc) ->
    take_n(T, N - 1, [H | Acc]).

spawn_workers(Count, Parent, F) ->
    lists:map(
      fun(_) ->
          spawn(fun() -> worker(Parent, F) end)
      end,
      lists:seq(1, Count)
    ).

worker(Parent, F) ->
    Parent ! {ready, self()},
    receive
        stop ->
            ok;
        {task, Part} ->
            Filtered = lists:filter(F, Part),
            Parent ! {result, self(), Filtered},
            worker(Parent, F)
    end.

collect_results(Parts, Pids, Timeout) ->
    Start = erlang:monotonic_time(millisecond),
    collect_loop(Parts, Pids, [], Start, Timeout).

collect_loop(_Parts, [], Acc, _Start, _Timeout) ->
    lists:reverse(Acc);
collect_loop(Parts, Pids, Acc, _Start, infinity) ->
    receive
        {ready, Pid} ->
            case Parts of
                [Part | Rest] ->
                    Pid ! {task, Part},
                    collect_loop(Rest, Pids, Acc, _Start, infinity);
                [] ->
                    Pid ! stop,
                    collect_loop([], lists:delete(Pid, Pids), Acc, _Start, infinity)
            end;
        {result, _Pid, Filtered} ->
            collect_loop(Parts, Pids, [Filtered | Acc], _Start, infinity)
    end;
collect_loop(Parts, Pids, Acc, Start, Timeout) ->
    Remain = remaining_timeout(Start, Timeout),
    receive
        {ready, Pid} ->
            case Parts of
                [Part | Rest] ->
                    Pid ! {task, Part},
                    collect_loop(Rest, Pids, Acc, Start, Timeout);
                [] ->
                    Pid ! stop,
                    collect_loop([], lists:delete(Pid, Pids), Acc, Start, Timeout)
            end;
        {result, _Pid, Filtered} ->
            collect_loop(Parts, Pids, [Filtered | Acc], Start, Timeout)
    after Remain ->
            lists:foreach(fun(Pid) -> Pid ! stop end, Pids),
            lists:reverse(Acc)
    end.

remaining_timeout(_Start, infinity) ->
    infinity;
remaining_timeout(Start, Timeout) ->
    Now = erlang:monotonic_time(millisecond),
    Elapsed = Now - Start,
    Remain = Timeout - Elapsed,
    if
        Remain =< 0 -> 0;
        true -> Remain
    end.
