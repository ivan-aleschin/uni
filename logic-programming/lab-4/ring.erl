-module(ring).

-export([ring/2]).

%% ring(N, M) creates N processes in a ring and sends a token around M times.
%% After M full laps, a stop signal is propagated and all processes exit.
%% All events are printed with io:format.

ring(N, M) when is_integer(N), N > 0, is_integer(M), M >= 0 ->
    Parent = self(),
    io:format("Current process is ~p~n", [Parent]),
    Pids = spawn_workers(N),
    lists:foreach(fun(Pid) -> io:format("Created ~p~n", [Pid]) end, Pids),
    First = hd(Pids),
    Last = lists:last(Pids),
    init_ring(Pids, First, Last, Parent),
    First ! {token, 0, Parent, M},
    receive
        {ring_done, Last} -> ok
    end.

spawn_workers(N) ->
    lists:map(
      fun(_) ->
          spawn(fun() -> worker() end)
      end,
      lists:seq(1, N)
    ).

init_ring(Pids, First, Last, Parent) ->
    Nexts = tl(Pids) ++ [First],
    lists:foreach(
      fun({Pid, Next}) ->
          Pid ! {init, Next, First, Last, Parent}
      end,
      lists:zip(Pids, Nexts)
    ).

worker() ->
    receive
        {init, Next, First, Last, Parent} ->
            loop(Next, First, Last, Parent)
    end.

loop(Next, First, Last, Parent) ->
    receive
        {token, Count, From, M} ->
            io:format("~p received ~w from ~p~n", [self(), Count, From]),
            IsFirst = (self() =:= First),
            IsLast = (self() =:= Last),
            Count1 =
                case true of
                    _ when IsFirst, From =:= Parent ->
                        Count + 1;
                    _ when IsLast ->
                        Count + 1;
                    _ ->
                        Count
                end,
            case IsFirst andalso (From =:= Last) andalso (Count1 >= M) of
                true ->
                    Next ! {stop, Count1, self()},
                    io:format("~p finished~n", [self()]);
                false ->
                    Next ! {token, Count1, self(), M},
                    loop(Next, First, Last, Parent)
            end;

        {stop, Count, From} ->
            io:format("~p received ~w from ~p~n", [self(), Count, From]),
            io:format("~p finished~n", [self()]),
            case self() =:= Last of
                true ->
                    Parent ! {ring_done, self()};
                false ->
                    Next ! {stop, Count, self()}
            end;
        stop ->
            io:format("~p finished~n", [self()])
    end.
