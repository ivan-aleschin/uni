-module(parent_children).
-export([start/1, send_to_child/2, stop/0]).

%% Public API

start(N) when is_integer(N), N >= 0 ->
    case whereis(parent_children) of
        undefined ->
            ParentPid = spawn(fun() -> parent_init(N) end),
            register(parent_children, ParentPid),
            ok;
        _Pid ->
            {error, already_started}
    end.

send_to_child(I, Msg) when is_integer(I), I >= 1 ->
    case whereis(parent_children) of
        undefined -> {error, not_started};
        ParentPid ->
            ParentPid ! {send_to_child, I, Msg},
            ok
    end.

stop() ->
    case whereis(parent_children) of
        undefined -> ok;
        ParentPid ->
            ParentPid ! stop,
            ok
    end.

%% Parent process

parent_init(N) ->
    process_flag(trap_exit, true),
    Children = spawn_children(1, N, #{}),
    parent_loop(Children).

parent_loop(Children) ->
    receive
        {send_to_child, I, Msg} ->
            case maps:get(I, Children, undefined) of
                undefined ->
                    io:format("Parent: no child ~p~n", [I]);
                Pid ->
                    Pid ! Msg
            end,
            parent_loop(Children);
        stop ->
            unregister(parent_children),
            lists:foreach(fun({_I, Pid}) -> Pid ! stop end,
                          maps:to_list(Children)),
            ok;
        {'EXIT', Pid, Reason} ->
            case child_index_by_pid(Pid, Children) of
                undefined ->
                    parent_loop(Children);
                I ->
                    case Reason of
                        normal ->
                            parent_loop(maps:remove(I, Children));
                        shutdown ->
                            parent_loop(maps:remove(I, Children));
                        _ ->
                            io:format("Parent: child ~p died with ~p, restarting~n", [I, Reason]),
                            NewPid = spawn_child(I),
                            parent_loop(Children#{I => NewPid})
                    end
            end
    end.

spawn_children(I, N, Acc) when I > N -> Acc;
spawn_children(I, N, Acc) ->
    Pid = spawn_child(I),
    spawn_children(I + 1, N, Acc#{I => Pid}).

spawn_child(I) ->
    spawn_link(fun() -> child_loop(I) end).

child_index_by_pid(Pid, Children) ->
    case lists:keyfind(Pid, 2, maps:to_list(Children)) of
        false -> undefined;
        {I, _} -> I
    end.

%% Child process

child_loop(I) ->
    receive
        stop -> ok;
        die  -> exit({child_died, I});
        Msg  ->
            io:format("Child ~p (~p) got message: ~p~n", [I, self(), Msg]),
            child_loop(I)
    end.
