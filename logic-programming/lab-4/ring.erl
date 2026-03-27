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
        {ring_done, First} -> ok
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
        {token, Lap, From, M} ->
            io:format("~p received ~w from ~p~n", [self(), Lap, From]),
            IsFirst = (self() =:= First),
            Lap1 =
                case IsFirst andalso (From =:= Last) of
                    true -> Lap + 1;
                    false -> Lap
                end,
            case IsFirst andalso (Lap1 >= M) of
                true ->
                    Next ! stop,
                    io:format("~p finished~n", [self()]),
                    Parent ! {ring_done, self()};
                false ->
                    Next ! {token, Lap1, self(), M},
                    loop(Next, First, Last, Parent)
            end;
        stop ->
            Next ! stop,
            io:format("~p finished~n", [self()])
    end.
