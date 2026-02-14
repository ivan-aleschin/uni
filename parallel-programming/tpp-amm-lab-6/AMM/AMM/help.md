
## 1. Int-матрицы: AddInt и MultInt (базовая АММ)

### Параметры

- `N = 3`
- В `dgA`:
  ![[Pasted image 20251114071243.png]]
- В `dgB` :
  ![[Pasted image 20251114071254.png]]

### 1.1. AddInt

1. Нажать **`AddInt`**.
2. В `dgC` должно получиться:
   ![[Pasted image 20251114071315.png]]
### 1.2. MultInt

1. С теми же A и B нажать **`MultInt`**.
2. В `dgC` должно быть:
   ![[Pasted image 20251114071342.png]]
   Комментарий (кратко): «Сложение/умножение матриц выполняет generic-класс `AMMimp<int>` с `Parallel.For`».

---
## 2. Floyd Shortest (кратчайшие пути)

### Параметры

1. `N = 4`, можно нажать **`Clear`**.
2. В `dgA` :
   ![[Pasted image 20251114071402.png]]
### Кнопки
1. Нажать **`Floyd Shortest`**.
### Результат (`dgC`)
![[Pasted image 20251114071420.png]]
`INF` — большое число (примерно `1073741823`).
Краткий комментарий:  
«0→3 = 9 (0–1–2–3), 1→3 = 4 (1–2–3) и т.д. – это классический Флойд min/+ на АММ».

#### проверка

![[Pasted image 20251114091612.png]]
![[Pasted image 20251114091601.png]]

---
## 3. Shortest Path (разузлование)
С теми же данными:
1. В `tbFrom` ввести `0`, в `tbTo` — `3`.
2. **`Shortest Path`**.

В MessageBox ожидаем строку:
> `0 -> 1 -> 2 -> 3`

Комментарий:  
«Флойд с матрицей `next`, путь восстанавливается методом `ReconstructPath`».

---

## 4. Floyd Longest (длиннейшие пути)
### Параметры
1. `N = 4`, `Clear`.
2. В `dgA` :
   ![[Pasted image 20251114071517.png]]
### Кнопки
1. Нажать **`Floyd Longest`**.
### Результат (`dgC`)
![[Pasted image 20251114071535.png]]
`−INF` будет отображаться как очень маленькое число (`-1073741824` примерно).
Комментарий:  
«Тот же Флойд, но семиринг max/+ (длиннейшие пути, DAG-пример)».

#### проверка
![[Pasted image 20251114091645.png]]
![[Pasted image 20251114091700.png]]

---
## 5. Bool: AddBool и MultBool
### Параметры
1. `N = 2`, `Clear`.
2. В `dgA`:
   ![[Pasted image 20251114071603.png]]
3. В `dgB`:
   ![[Pasted image 20251114071614.png]]
### 5.1. AddBool
1. Нажать **`AddBool`**.
   Ожидаем `dgC`:
   ![[Pasted image 20251114071638.png]]

#### Проверка

![[Pasted image 20251114091747.png]]

(элементный OR).
### 5.2. MultBool
1. Нажать **`MultBool`**.
   Ожидаем `dgC`:
   ![[Pasted image 20251114071657.png]]
   (булев матричный продукт: ⊕=OR, ⊗=AND).

#### проверка
![[Pasted image 20251114091832.png]]

---

## 6. Bool: Connectivity (связность графа)
### Параметры
1. `N = 4`, `Clear`.
2. В `dgA` задать цепочку 0→1→2→3:
   ![[Pasted image 20251114071710.png]]
### Кнопки
1. Нажать **`Connectivity`**.
### Результат (`dgC`) — транзитивное замыкание
![[Pasted image 20251114071737.png]]
Комментарий:  
«Флойд на булевом полукольце (⊕=OR, ⊗=AND) даёт достижимость всех пар вершин».

#### проверка
![[Pasted image 20251114091916.png]]


---
## 7. Карта проекта по файлам

### `AMMimp.cs` — ядро Абстрактной Матричной Машины
**Классы:**

1. `abstract class AmmOps<T>`

  - Описывает «алгебру» элементов матрицы:

    - `T Zero` — нейтральный элемент для сложения (⊕).

    - `T One` — нейтральный элемент для умножения (⊗).

    - `Add(T a, T b)` — операция ⊕.

    - `Mul(T a, T b)` — операция ⊗.

    - `Better(T candidate, T current)` — критерий «лучше» (для Флойда).

2. `class AMMimp<T>`

  - **Общий (generic) движок матричных операций**.

  - Работает с любой `AmmOps<T>`:


    Методы:
    
    - `AddMatrices(T[,] A, T[,] B, T[,] C)`  
        Параллельное по строкам сложение матриц `C = A ⊕ B` (через `Parallel.For`).
        
    - `MultiplyMatrices(T[,] A, T[,] B, T[,] C)`  
        Параллельное матричное умножение `C = A ⊗ B`.
        
    - `FloydWarshall(T[,] d)`  
        Алгоритм Флойда–Уоршелла на абстрактном семиринге (⊕/⊗). Меняет `d` на месте.
        
    - `FloydWarshallWithPath(T[,] d, int?[,] next)`  
        Тот же Флойд, но заполняет матрицу `next` для восстановления пути.
        
    - `static ReconstructPath(int u, int v, int?[,] next)`  
        Разузлование маршрута из `next`: возвращает массив вершин `u…v`.

3. **Конкретные реализации алгебр:**

  - `IntArithmeticOps`  
    Обычная арифметика `int` (сложение/умножение) — используется для `AddInt`/`MultInt`.

  - `BoolConnectivityOps`  
    Булев семиринг для связности: `⊕ = OR`, `⊗ = AND`.

  - `IntShortestPathOps`  
    Семиринг min/+ для кратчайших путей: `⊕ = min`, `⊗ = +`, `Zero = INF`.

  - `IntLongestPathOps`  
    Семиринг max/+ для длиннейших путей: `⊕ = max`, `⊗ = +`, `Zero = -INF`.


---

### `AMMRI.cs` — работа с **целочисленными** матрицами и графами

**Класс `AMMRI`:**

Поля:

- `int[,] rA, rB, rC` — матрицы A, B, C.

- `_arithMachine` — `AMMimp<int>` с `IntArithmeticOps` (обычные матричные операции).

- `_shortestMachine` — `AMMimp<int>` с `IntShortestPathOps` (Флойд на min/+).

- `_longestMachine` — `AMMimp<int>` с `IntLongestPathOps` (Флойд на max/+).


Методы:

- `InitRnd(string _N, DataGridView A,B,C)`  
  Создаёт матрицы `N×N`, заполняет `rA`, `rB` случайными 0..2 и выводит в гриды.

- `UpdateAFromGrid(DataGridView grid)`  
  Читает текущие значения из `dgA` и переписывает их в `rA`  
  (важно для Флойда и ShortestPath).

- `AddM()`  
  `C = A + B` через `_arithMachine.AddMatrices`.

- `MultM()`  
  `C = A * B` через `_arithMachine.MultiplyMatrices`.

- `Show(DataGridView C)`  
  Выводит `rC` в грид.

- `ComputeAllPairsShortestPaths()`  
  Строит матрицу расстояний `d` из `rA`, запускает `_shortestMachine.FloydWarshall(d)`,  
  результат кладёт в `rC` — **все кратчайшие пути**.

- `ComputeAllPairsLongestPaths()`  
  Аналогично, но через `_longestMachine` — **все длиннейшие пути** (учебный пример).

- `GetShortestPath(int from, int to)`  
  Строит `d` и `next` по `rA`, вызывает  
  `_shortestMachine.FloydWarshallWithPath(d, next)` и возвращает путь как массив вершин.


---

### `AMMRB.cs` — работа с **булевыми** матрицами

**Класс `AMMRB`:**

Поля:

- `bool[,] rA, rB, rC`.

- `_boolMachine = new AMMimp<bool>(new BoolConnectivityOps())`.


Методы:

- `InitRnd(string _N, DataGridView A,B,C)`  
  Создаёт булевы матрицы `N×N`, случайно заполняет `rA`, `rB`.

- `UpdateABFromGrids(DataGridView A, DataGridView B)`  
  Перечитывает текущие значения из `dgA` и `dgB` в `rA` и `rB`  
  (для `AddBool` и `MultBool`).

- `UpdateAFromGrid(DataGridView A)`  
  Перечитывает только `rA` (для `Connectivity`).

- `AddM()`  
  `C = A OR B` (элементно) через `_boolMachine.AddMatrices`.

- `MultM()`  
  Булев матричный продукт (⊕=OR, ⊗=AND) через `_boolMachine.MultiplyMatrices`.

- `Show(DataGridView C)`  
  Выводит `rC`.

- `ComputeConnectivityClosure()`  
  Копирует `rA` в `d`, запускает `_boolMachine.FloydWarshall(d)` —  
  **транзитивное замыкание (достижимость всех пар вершин)**, результат в `rC`.


---

### `AMMF.cs` + `AMMF.Designer.cs` — форма и кнопки

**Главный класс формы `AMMF`**:

- Поля: `AMMRI RI = new AMMRI(); AMMRB RB = new AMMRB();`

- Основные обработчики:


**Int:**

- `btnInit_Click` → `RI.InitRnd(...)`.

- `btnAdd_Click` → `RI.AddM(); RI.Show(dgC);`

- `btnMultInt_Click` → `RI.MultM(); RI.Show(dgC);`

- `btnClearInt_Click` → чистит `dgA/dgB/dgC`.

- `btnFloydShortest_Click` → `RI.UpdateAFromGrid(dgA); RI.ComputeAllPairsShortestPaths(); RI.Show(dgC);`

- `btnFloydLongest_Click` → `RI.UpdateAFromGrid(dgA); RI.ComputeAllPairsLongestPaths(); RI.Show(dgC);`

- `btnShortestPath_Click` → читает `tbFrom/tbTo`,  
  `RI.UpdateAFromGrid(dgA);` → `RI.GetShortestPath(...)` → показывает путь в `MessageBox`.


**Bool:**

- `btnInitBool_Click` → `RB.InitRnd(...)`.

- `btnAddBool_Click` → `RB.UpdateABFromGrids(dgA,dgB); RB.AddM(); RB.Show(dgC);`

- `btnMultBool_Click` → `RB.UpdateABFromGrids(dgA,dgB); RB.MultM(); RB.Show(dgC);`

- `btnConnectivity_Click` → `RB.UpdateAFromGrid(dgA); RB.ComputeConnectivityClosure(); RB.Show(dgC);`


---



## 8. Короткая теория

1. **Абстрактная матричная машина (АММ):**

  - Мы работаем не с «обычными числами», а с элементами абстрактного множества `T`,

  - на котором заданы две операции: «сложение» ⊕ и «умножение» ⊗ с нейтральными элементами.

  - Такая структура называется **семирингом**.

  - В коде это представлено классами `AmmOps<T>` + `AMMimp<T>`.

2. **Семиринги, которые мы используем:**

  - Обычная арифметика `int`: ⊕ = `+`, ⊗ = `*`.
  - Кратчайшие пути: ⊕ = `min`, ⊗ = `+`, `Zero = INF` — классический **min-plus** семиринг.
  - Длиннейшие пути: ⊕ = `max`, ⊗ = `+`, `Zero = -INF` — **max-plus** семиринг (для DAG).
  - Булевы матрицы: ⊕ = `OR`, ⊗ = `AND` — семиринг для связности.

3. **Алгоритм Флойда–Уоршелла:**

  - Перебирает промежуточную вершину `k` и улучшает расстояния `d[i,j]`  
    через путь `i → k → j`:  
    `d[i,j] = d[i,j] ⊕ (d[i,k] ⊗ d[k,j])`.

  - В нашем коде он реализован **один раз** в `AMMimp<T>.FloydWarshall`,  
    а поведение меняется только подстановкой разных `AmmOps<T>`.

4. **Разузлование пути:**

  - Дополнительно храним `next[i,j]` — куда идти из i по кратчайшему пути к j.

  - При каждом улучшении пути через `k` делаем `next[i,j] = next[i,k]`.

  - Потом `ReconstructPath(u,v,next)` строит список вершин маршрута.

5. **Булевы матрицы и связность:**

  - Матрица смежности `A` с True/False.

  - Флойд на булевом семиринге вычисляет **транзитивное замыкание** —  
    `d[i,j]` будет True, если существует путь из i в j любой длины.

6. **Параллельность:**

  - В старом варианте было последовательное тройное вложение циклов.

  - В `AMMimp<T>` внешние циклы заменены на `Parallel.For`,  
    каждый поток обрабатывает свою строку матрицы → используем многоядерность.

---





## 9. Допы

### 1. «Сделать как библиотеку классов»

**Что требовали:**  
Логика АММ должна быть отделена от формы и пригодна для использования с «реальными» матрицами.

**Что мы сделали и где это видно:**

- В файле **`AMMimp.cs`**:

  - классы `AmmOps<T>` и `AMMimp<T>` **не зависят от WinForms** и вообще ничего не знают про `DataGridView`.

  - Это обычные C#-классы, которые можно вынести в отдельный **Class Library** (проект типа _Библиотека классов_) и подключать в другие программы.

- Файлы **`AMMRI.cs`** и **`AMMRB.cs`** – это уже **обёртки для формы**, где:

  - данные читаются из `DataGridView` (`UpdateAFromGrid`, `UpdateABFromGrids`),

  - а дальше передаются в `AMMimp<T>`.


> «Вынес всю матричную логику в generic-класс `AMMimp<T>` и абстрактный `AmmOps<T>`. Они не зависят от UI и могут лежать в отдельной библиотеке классов, которую можно использовать с любыми матрицами: из файла, из БД, из сети и т.п.»

---

### 2. «Использовать ABSTRACT / GENERIC, а не делегаты»

**Что требовали:**  
Не просто функции/делегаты, а полноценные абстрактные/дженерик-классы.

**Что мы сделали:**

- **Абстрактный класс** `AmmOps<T>` (в `AMMimp.cs`):

  - описывает операции ⊕, ⊗, `Zero`, `One`, `Better`.

- **Generic-класс** `AMMimp<T>`:

  - параметризован типом `T` и конкретной реализацией `AmmOps<T>`.

- Конкретные реализации:

  - `IntArithmeticOps` – обычная арифметика;

  - `BoolConnectivityOps` – булевы OR/AND;

  - `IntShortestPathOps` – min/+ (кратчайшие пути);

  - `IntLongestPathOps` – max/+ (длиннейшие пути).


> «Вместо делегатов ввёл абстрактный класс `AmmOps<T>` и generic-движок `AMMimp<T>`. Для каждой задачи (арифметика, кратчайшие/длиннейшие пути, булева связность) у меня свой класс `AmmOps<T>`, а алгоритм (сложение, умножение, Флойд) написан один раз в `AMMimp<T>`.»

---

### 3. «Последовательные операции заменить на параллельные»

**Что требовали:**  
В модуле AMMimp последовательные циклы заменить на параллельные.

**Где это реализовано:**
- В `AMMimp<T>`:

  - `AddMatrices` – внешний цикл по строкам заменён на `Parallel.For`.

  - `MultiplyMatrices` – внешний цикл по строкам `i` тоже через `Parallel.For`.

  - `FloydWarshall` и `FloydWarshallWithPath`:

    - внешний цикл по `k` последовательный (как по алгоритму),

    - **внутри по `i` стоит `Parallel.For`**, а по `j` – обычный цикл.

- В результате каждая строка/ячейка матрицы обрабатывается **в отдельном потоке**, что использует многопроцессорность.


> «В исходной версии был тройной вложенный цикл. Я вынес наружу индекс строки и заменил внешние циклы на `Parallel.For`. Так любые операции над матрицами (сложение, умножение, Флойд) теперь выполняются параллельно по строкам.»

---

### 4. «Флойд–Уоршелл для разных задач» (связность, кратчайший, длиннейший путь, разузлование)

**Где и как:**

- В `AMMimp<T>`:

  - `FloydWarshall` – универсальная реализация Флойда на абстрактных ⊕ и ⊗.

  - `FloydWarshallWithPath` + `ReconstructPath` – тот же алгоритм, но с матрицей `next` для восстановления пути.

- В `AMMRI`:

  - `ComputeAllPairsShortestPaths()` – Флойд с `IntShortestPathOps` → **все кратчайшие пути**.

  - `ComputeAllPairsLongestPaths()` – Флойд с `IntLongestPathOps` → **все длиннейшие пути**.

  - `GetShortestPath(from,to)` – Флойд + `next` → **разузлование одного кратчайшего маршрута**.

- В `AMMRB`:

  - `ComputeConnectivityClosure()` – Флойд с `BoolConnectivityOps` → **связность / транзитивное замыкание графа**.


> «У меня Флойд–Уоршелл реализован один раз в `AMMimp<T>`. В зависимости от того, какую `AmmOps<T>` подставляю, тот же алгоритм решает разные задачи:
>
> - для `BoolConnectivityOps` – связность/достижимость,
>
> - для `IntShortestPathOps` – все кратчайшие пути,
>
> - для `IntLongestPathOps` – длиннейшие пути,
>
> - плюс делаю разузлование пути через дополнительную матрицу `next`.»
>

---
