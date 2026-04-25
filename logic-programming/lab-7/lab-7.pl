% uni/logic-programming/lab-7/lab-7.pl
% Реализация заданий 1-4 и дополнительных заданий 5-6
:- use_module(library(plunit)).

% ---------------------
% 1. triangle (N-ое треугольное число)
% ---------------------
% Рекурсивное вычисление N-го треугольного числа:
% Базис: triangle(0,0).
% Шаг: triangle(N,T) вычисляется как triangle(N-1,T1) + N.
triangle(0, 0) :- !.
triangle(N, T) :-
    integer(N), N > 0,
    N1 is N - 1,
    triangle(N1, T1),
    T is T1 + N.

% ---------------------
% 2. dot (скалярное произведение)
% ---------------------
% Вычисление скалярного произведения двух векторов (списков одинаковой длины).
% Рекурсивно перемножаем головы и складываем результаты для хвостов.
dot([], [], 0) :- !.
dot([H1|T1], [H2|T2], P) :-
    dot(T1, T2, P1),
    P is P1 + H1 * H2.

% ---------------------
% 3. polynom (проверка многочлена в нормальной форме)
% ---------------------
% Проверяем, что выражение является многочленом в нормальной форме:
% одночлены вида C * x^P, x^P, C * x, x или константа, коэффициенты ≠ 0,
% степени — целые положительные, и порядок слагаемых — по убыванию степени.
polynom(E) :-
    polynom_ordered(E, _).

is_term(C * x^P, P) :- number(C), C =\= 0, integer(P), P > 1, !.
is_term(x^P, P) :- integer(P), P > 1, !.
is_term(C * x, 1) :- number(C), C =\= 0, !.
is_term(x, 1) :- !.
is_term(C, 0) :- number(C), C =\= 0.

polynom_ordered(A + B, DegA) :-
    !,
    polynom_ordered(A, DegA),
    polynom_ordered(B, DegB),
    DegA > DegB.
polynom_ordered(Term, Deg) :-
    is_term(Term, Deg).

% ---------------------
% 4. combination (k-combinations)
% ---------------------
combination(_, 0, []) :- !.
combination([H|T], K, [H|R]) :-
    K > 0,
    K1 is K - 1,
    combination(T, K1, R).
combination([_|T], K, R) :-
    K > 0,
    combination(T, K, R).

% ---------------------
% 5. prime_factors(Num, Factors)
%    Factors = [factor(P,Power), ...]
% ---------------------
prime_factors(N, Factors) :-
    integer(N), N > 1,
    pf_acc(N, 2, Factors).

pf_acc(1, _, []) :- !.
pf_acc(N, F, [factor(N,1)]) :-
    F * F > N, !.
pf_acc(N, F, [factor(F,Count)|Rest]) :-
    F * F =< N,
    N mod F =:= 0, !,
    count_power(N, F, 0, Count, Rem),
    F1 is F + 1,
    pf_acc(Rem, F1, Rest).
pf_acc(N, F, Rest) :-
    F * F =< N,
    F1 is F + 1,
    pf_acc(N, F1, Rest).

count_power(N, P, Acc, Count, Rem) :-
    ( 0 is N mod P ->
        N1 is N // P,
        Acc1 is Acc + 1,
        count_power(N1, P, Acc1, Count, Rem)
    ; Count = Acc, Rem = N
    ).

% ---------------------
% 6. polynomize(Expr, PolyExpr)
%    Преобразование арифметического выражения (с +, *, ^) в многочлен в нормальной форме
% ---------------------
% Алгоритм:
% 1) expr_to_pairs/2 преобразует Expr в список пар (степень, коэффициент) (временный формат);
% 2) pairs_to_deg/2 приводит форматы к deg(D,C);
% 3) combine_pairs/2 объединяет одночлены одинаковых степеней и сортирует их;
% 4) pairs_to_term/2 собирает итоговый терм (сумму одночленов).
polynomize(Expr, PolyExpr) :-
    expr_to_pairs(Expr, Pairs0),
    % normalize to deg(D,C) terms
    pairs_to_deg(Pairs0, Pairs),
    combine_pairs(Pairs, Combined),      % Combined = [deg(D,C), ...] sorted desc, no zeros
    pairs_to_term(Combined, PolyExpr).

% expr_to_pairs: convert Expr to list of (Degree, Coeff) pairs (may contain duplicates)
expr_to_pairs(Expr, Pairs) :-
    ( number(Expr) -> Pairs = [(0, Expr)]
    ; Expr == x -> Pairs = [(1, 1)]
    ; Expr =.. ['^', Base, Exp], Base == x, integer(Exp), Exp >= 0 ->
        Pairs = [(Exp, 1)]
    ; Expr =.. ['+', A, B] ->
        expr_to_pairs(A, PA), expr_to_pairs(B, PB), append(PA, PB, Pairs)
    ; Expr =.. ['*', A, B] ->
        expr_to_pairs(A, PA), expr_to_pairs(B, PB), mul_pairs(PA, PB, Pairs)
    ; % handle coefficient * expression where coefficient is numeric on either side
      Expr =.. ['*', C, E], number(C), E \= x, \+ (E =.. ['^'|_]), !,
        expr_to_pairs(E, PE), scale_pairs(PE, C, Pairs)
    ; Expr =.. ['*', E, C], number(C), !,
        expr_to_pairs(E, PE), scale_pairs(PE, C, Pairs)
    ; % unary minus (negation)
      Expr =.. ['-', A], !,
        expr_to_pairs(A, PA), scale_pairs(PA, -1, Pairs)
    ; % fallback: attempt numeric evaluation if possible
      number(Expr) -> Pairs = [(0, Expr)]
    ; % otherwise treat as zero (unknown symbol)
      Pairs = [(0, 0)]
    ).

% multiply two pair-lists (convolution)
mul_pairs(P1, P2, Out) :-
    findall((D, C), (member((D1, C1), P1), member((D2, C2), P2), D is D1 + D2, C is C1 * C2), Prod),
    combine_pairs(Prod, Out).

% scale list of pairs by scalar
scale_pairs([], _, []).
scale_pairs([(D,C)|T], S, [(D, C2)|RT]) :-
    C2 is C * S,
    scale_pairs(T, S, RT).

% combine_pairs: sum coefficients by degree, remove zeros, sort descending by degree
combine_pairs(Pairs, Combined) :-
    findall(D, member((D,_), Pairs), Ds),
    sort(Ds, UniqueDs),
    findall((D,Sum), (member(D, UniqueDs), sum_coeff(D, Pairs, Sum), Sum =\= 0), Tmp),
    % order degrees descending
    findall(D0, member((D0,_), Tmp), Ds0), sort(Ds0, DsAsc), reverse(DsAsc, DsDesc),
    build_ordered(DsDesc, Tmp, Combined).

sum_coeff(D, Pairs, Sum) :-
    findall(C, member((D,C), Pairs), Cs),
    sum_list(Cs, Sum).

sum_list(List, Sum) :- sum_list(List, 0, Sum).
sum_list([], Acc, Acc).
sum_list([H|T], Acc, Sum) :- NewAcc is Acc + H, sum_list(T, NewAcc, Sum).

build_ordered([], _, []).
build_ordered([D|DT], Tmp, [(D,Val)|RT]) :-
    member((D,Val), Tmp),
    build_ordered(DT, Tmp, RT).

% pairs_to_term: собираем итоговый синтаксический терм из списка одночленов
% Вход: список одночленов вида deg(Степень, Коэффициент)
% Выход: выражение, например 2*x^2 + 3*x + 5
pairs_to_term([], 0) :- !.
pairs_to_term([deg(D,C)], Term) :- !, mono_to_term(deg(D,C), Term).
pairs_to_term([deg(D,C)|T], Expr) :-
    mono_to_term(deg(D,C), M),
    pairs_to_term(T, Rest),
    Expr = (M + Rest).

mono_to_term((0, C), C) :- !.
mono_to_term((1, 1), x) :- !.
mono_to_term((1, C), Term) :- Term = (C * x), !.
mono_to_term((D, 1), Term) :- Term = (x ^ D), !.
mono_to_term((D, C), Term) :- Term = (C * (x ^ D)), !.

% ---------------------
% run_lab_tests: run unit tests and demonstrations
% ---------------------
run_lab_tests :-
    run_tests,
    triangle(4, T), format('1. triangle: ~w~n', [T]),
    dot([1,2],[3,4], D), format('2. dot: ~w~n', [D]),
    (polynom(2*x^3 + x) -> format('3. polynom: yes~n', []) ; format('3. polynom: no~n', [])),
    findall(C, combination([1,2,3], 2, C), L), format('4. combinations: ~w~n', [L]),

    % extras demonstration
    ( catch((prime_factors(315, PF), format('5. prime_factors(315): ~w~n', [PF])), E, format('5. prime_factors error: ~w~n', [E])) ; true ),
    ( catch((polynomize((x + x)*(x + 1), P), format('6. polynomize((x+x)*(x+1)): ~w~n', [P])), E, format('6. polynomize error: ~w~n', [E])) ; true ),

    % operator experiments short
    format('~nOperator examples (brief):~n', []),
    ( catch((X = 1+2, format('X = 1+2 -> X = ~w~n', [X])), _, format('X = 1+2 -> error~n', [])) ; true ),
    ( (3 = 1+2) -> format('3 = 1+2 -> true~n', []) ; format('3 = 1+2 -> false~n', []) ),
    ( (2+1 = 1+2) -> format('2+1 = 1+2 -> true~n', []) ; format('2+1 = 1+2 -> false~n', []) ),
    ( (3 =:= 1+2) -> format('3 =:= 1+2 -> true~n', []) ; format('3 =:= 1+2 -> false~n', []) ),
    ( catch((X2 is 1+2, format('X2 is 1+2 -> X2 = ~w~n', [X2])), _, format('X2 is 1+2 -> error~n', [])) ; true ),

    true.

% ---------------------
% PlUnit tests
% ---------------------
:- begin_tests(lab7).

test(triangle) :- triangle(4, 10).
test(dot) :- dot([1,2],[3,4], 11).
test(polynom_valid) :- polynom(2*x^2 + 1).
test(combination) :- findall(C, combination([1,2], 1, C), [[1],[2]]).

% extra tests
test(prime_factors_315) :-
    prime_factors(315, L),
    L = [factor(3,2), factor(5,1), factor(7,1)].

test(polynomize_example) :-
    polynomize((x + x)*(x + 1), P),
    % Check produced polynomial is syntactically a polynomial in normal form
    polynom(P).

% operator checks
test(op_is_bind) :- X is 1+2, X =:= 3.
test(op_eval_numeric) :- 3 =:= 1+2.

:- end_tests(lab7).
