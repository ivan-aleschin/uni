-module(ring_srv).

-behaviour(gen_server).

-export([start_link/0, ring/2]).
-export([init/1, handle_call/3, handle_cast/2, handle_info/2, terminate/2, code_change/3]).

start_link() ->
    gen_server:start_link({local, ring_srv}, ?MODULE, #{}, []).

ring(N, M) ->
    gen_server:call(ring_srv, {ring, N, M}, infinity).

init(State) ->
    {ok, State}.

handle_call({ring, N, M}, From, State) ->
    spawn(fun() ->
        Result = ring:ring(N, M),
        gen_server:reply(From, Result)
    end),
    {noreply, State};
handle_call(_Req, _From, State) ->
    {reply, {error, unknown_request}, State}.

handle_cast(_Msg, State) ->
    {noreply, State}.

handle_info(_Info, State) ->
    {noreply, State}.

terminate(_Reason, _State) ->
    ok.

code_change(_OldVsn, State, _Extra) ->
    {ok, State}.
