% family.pl
% Базовая база данных семьи

% Родители: parent(Родитель, Ребёнок)
parent(ivan, mary).
parent(ivan, alex).
parent(stephen, ivan).
parent(stephen, olga).
parent(mary, nastya).
parent(vladimir, nastya).
parent(olga, petr).

% Пол
male(ivan).
male(alex).
male(stephen).
male(petr).
male(vladimir).

female(mary).
female(nastya).
female(olga).

% Предикаты-правила

% Брат/сестра (общий родитель)
sibling(X, Y) :-
    parent(Z, X),
    parent(Z, Y),
    X \= Y.

% Сестра
sister(X, Y) :-
    sibling(X, Y),
    female(X).

% Брат
brother(X, Y) :-
    sibling(X, Y),
    male(X).

% Задание 5: Тётя
% X является тётей Y, если X — сестра одного из родителей Y.
aunt(X, Y) :-
    sister(X, Parent),
    parent(Parent, Y).
