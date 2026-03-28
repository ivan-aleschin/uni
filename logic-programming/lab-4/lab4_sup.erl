-module(lab4_sup).

-behaviour(supervisor).

-export([start_link/0]).
-export([init/1]).

start_link() ->
    supervisor:start_link({local, lab4_sup}, ?MODULE, []).

init([]) ->
    RingSpec = #{
        id => ring_srv,
        start => {ring_srv, start_link, []},
        restart => permanent,
        shutdown => 5000,
        type => worker,
        modules => [ring_srv]
    },
    ParentSpec = #{
        id => parent_children_srv,
        start => {parent_children_srv, start_link, []},
        restart => transient,
        shutdown => 5000,
        type => worker,
        modules => [parent_children_srv]
    },
    {ok, {{one_for_one, 5, 10}, [RingSpec, ParentSpec]}}.
