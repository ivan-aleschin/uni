% lab-5.pl
:- consult('family.pl').

% Задание 6: Фильмы
movie('Inception', 'Christopher Nolan', 2010).
movie('The Dark Knight', 'Christopher Nolan', 2008).
actor('Inception', 'Leonardo DiCaprio').
actor('Inception', 'Tom Hardy').
actor('The Dark Knight', 'Tom Hardy').
actor('The Dark Knight', 'Christian Bale').

worked_together(A1, A2) :- actor(M, A1), actor(M, A2), A1 \= A2.

actors_connected(A1, A2) :- actors_connected(A1, A2, [A1]).
actors_connected(A1, A2, _) :- worked_together(A1, A2).
actors_connected(A1, A2, V) :-
    worked_together(A1, I), \+ member(I, V),
    actors_connected(I, A2, [I|V]).

% Задание 7: Полёты
есть_рейс(мос, спб).
есть_рейс(мос, ект).
есть_рейс(мос, новосиб).
есть_рейс(спб, новосиб).
есть_рейс(спб, сочи).
есть_рейс(спб, минск).
есть_рейс(ект, сочи).
есть_рейс(сочи, киев).
есть_рейс(минск, новосиб).
есть_рейс(минск, киев).

рейс(X, Y) :- есть_рейс(X, Y).
рейс(X, Y) :- есть_рейс(Y, X).

связаны(X, Y) :- связаны(X, Y, [X]).
связаны(X, Y, _) :- рейс(X, Y).
связаны(X, Y, V) :-
    рейс(X, Z), \+ member(Z, V),
    связаны(Z, Y, [Z|V]).

run_lab_tests :-
    % Run automated unit tests first
    run_tests,
    format("--- Задание 3: Запросы ---~n"),
    (parent(F, nastya), male(F) -> format("1. Отец Насти: ~w~n", [F])),
    (parent(ivan, _) -> format("2. Дети Ивана: есть~n")),

    format("~n--- Задание 5: Тётя ---~n"),
    findall(A-N, aunt(A, N), L5),
    format("5. ~w~n", [L5]),

    format("~n--- Задание 6: Фильмы ---~n"),
    (actors_connected('Leonardo DiCaprio', 'Christian Bale') -> format("6. DiCaprio connected to Bale: yes~n")),

    format("~n--- Задание 7: Полёты ---~n"),
    (связаны(мос, сочи) -> format("7. мос связаны с сочи: да~n")).

:- begin_tests(lab5).

% Test aunt/2: olga should be aunt of mary and alex in the family.pl facts
test(aunt_olga_mary) :-
    aunt(olga, mary).

test(aunt_olga_alex) :-
    aunt(olga, alex).

% Test actors_connected/2: transitive connection
test(actors_connected_di_bale) :-
    actors_connected('Leonardo DiCaprio', 'Christian Bale').

% Negative-ish test: an actor not in DB shouldn't be connected (non-deterministic absence)
test(actors_connected_nonexistent, [fail]) :-
    actors_connected('Leonardo DiCaprio', 'Some Unknown Actor').

% Test flights connectivity: various reachable pairs
test(flights_mos_kiev) :-
    связаны(мос, киев).

% Ensure рейс/2 is undirected (7' requirement)
test(flight_symmetry) :-
    рейс(сочи, спб), % expecting рейс(спб, сочи) exists so рейс(сочи, spb) should be true via рейс/2
    связаны(сочи, спб).

:- end_tests(lab5).
