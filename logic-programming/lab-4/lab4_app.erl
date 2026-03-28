-module(lab4_app).

-behaviour(application).

-export([start/2, stop/1]).

start(_Type, _Args) ->
    lab4_sup:start_link().

stop(_State) ->
    ok.
