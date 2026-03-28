-module(parent_children_srv).

-behaviour(gen_server).

-export([start_link/0, start/1, send_to_child/2, stop/0]).
-export([init/1, handle_call/3, handle_cast/2, handle_info/2, terminate/2, code_change/3]).

start_link() ->
    gen_server:start_link({local, parent_children_srv}, ?MODULE, #{}, []).

start(N) when is_integer(N), N >= 0 ->
    gen_server:call(parent_children_srv, {start, N}).

send_to_child(I, Msg) when is_integer(I), I >= 1 ->
    gen_server:cast(parent_children_srv, {send, I, Msg}).

stop() ->
    gen_server:call(parent_children_srv, stop).

init(_Args) ->
    process_flag(trap_exit, true),
    {ok, #{children => #{}, n => 0}}.

handle_call({start, N}, _From, State) ->
    Children = maps:get(children, State),
    case maps:size(Children) of
        0 ->
            NewChildren = spawn_children(1, N, #{}),
            {reply, ok, State#{children => NewChildren, n => N}};
        _ ->
            {reply, {error, already_started}, State}
    end;
handle_call(stop, _From, State) ->
    Children = maps:get(children, State),
    stop_children(Children),
    {stop, normal, ok, State#{children => #{}}};
handle_call(_Req, _From, State) ->
    {reply, {error, unknown_request}, State}.

handle_cast({send, I, Msg}, State) ->
    Children = maps:get(children, State),
    case maps:get(I, Children, undefined) of
        undefined ->
            io:format("Parent: no child ~p~n", [I]),
            {noreply, State};
        Pid ->
            Pid ! Msg,
            {noreply, State}
    end;
handle_cast(_Msg, State) ->
    {noreply, State}.

handle_info({'EXIT', Pid, Reason}, State) ->
    Children = maps:get(children, State),
    case child_index_by_pid(Pid, Children) of
        undefined ->
            {noreply, State};
        I ->
            case Reason of
                normal ->
                    {noreply, State#{children => maps:remove(I, Children)}};
                shutdown ->
                    {noreply, State#{children => maps:remove(I, Children)}};
                _ ->
                    io:format("Parent: child ~p died with ~p, restarting~n", [I, Reason]),
                    NewPid = spawn_child(I, self()),
                    NewChildren = Children#{I => NewPid},
                    {noreply, State#{children => NewChildren}}
            end
    end;
handle_info(_Info, State) ->
    {noreply, State}.

terminate(_Reason, State) ->
    stop_children(maps:get(children, State, #{})),
    ok.

code_change(_OldVsn, State, _Extra) ->
    {ok, State}.

spawn_children(I, N, Acc) when I > N ->
    Acc;
spawn_children(I, N, Acc) ->
    Pid = spawn_child(I, self()),
    spawn_children(I + 1, N, Acc#{I => Pid}).

spawn_child(I, ParentPid) ->
    spawn_link(fun() -> child_loop(I, ParentPid) end).

stop_children(Children) ->
    lists:foreach(fun({_I, Pid}) -> Pid ! stop end, maps:to_list(Children)).

child_index_by_pid(Pid, Children) ->
    case lists:keyfind(Pid, 2, maps:to_list(Children)) of
        false -> undefined;
        {I, _} -> I
    end.

child_loop(I, _ParentPid) ->
    receive
        stop ->
            ok;
        die ->
            exit({child_died, I});
        Msg ->
            io:format("Child ~p (~p) got message: ~p~n", [I, self(), Msg]),
            child_loop(I, _ParentPid)
    end.
