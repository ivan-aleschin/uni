# CLAUDE.md

Этот файл — инструкции для будущих сессий Claude Code (claude.ai/code) в этом репозитории. **Общаемся по-русски** — это монорепозиторий учебных работ, все README и комментарии тоже на русском, поддерживай язык при редактировании.

## Что это за репозиторий

Полиглот-монорепо с лабами и конспектами по нескольким предметам университета. Каждая верхняя папка — **отдельный предмет** со своим тулчейном и своей нумерацией лаб (`lab-1`, `lab1`, `lab-01`, …). **Единого build-системы нет** — всё делается на уровне конкретной лабы, не на уровне репо.

## Окружение

Хозяин репозитория сидит на NixOS и использует **direnv + flake**: в корне лежит `.envrc` со строкой `use flake`, поэтому `direnv allow` один раз — и `gcc`, `cmake`, `qmake6`, `python3`, `swipl`, `iverilog`, `verilator`, `dotnet`, `mvn` уже в PATH без всякого `nix develop`.

**У Claude (тебя) этого direnv-хука нет**, поэтому в Bash-командах ты получаешь окружение flake одним из двух способов:

```bash
# Вариант 1 (рекомендуемый): тулчейн уже подмешан через .direnv/bin в PATH родительского процесса.
# Просто запускай g++/make/cmake/python3 напрямую — это работает.
make -C software-architecture/lab-4

# Вариант 2 (если что-то не нашлось в PATH): обернуть в nix develop.
nix develop -c make
# или для разовых утилит:
nix shell nixpkgs#poppler-utils -c pdftotext file.pdf out.txt
```

**Важное правило:** если для задачи нужна новая утилита/библиотека (например, `qt6.qtimageformats` для PNG в Qt, или какой-то Python-пакет с C-расширением), **добавляй её в `flake.nix`**, а не ставь через `pip`/`apt`/`nix-env`. Пользователь полагается на flake как на единый источник тулчейна, и любая команда, которую ты прогоняешь у себя, должна потом запуститься у него **без дополнительных шагов**. Если что-то добавил во флэйк — упомяни это явно в чате и в README лабы.

**Про Python и C-расширения:** `psycopg2` задекларирован через `python3.withPackages` в флэйке именно потому, что бинарные wheel'ы `pip`/`uv` на NixOS не работают (нет стандартных путей `/lib`). Если лабе по БД понадобится ещё один C-extension пакет — туда же.

## Команды по предметам

| Предмет | Тулчейн | Как собирать/запускать лабу |
| --- | --- | --- |
| `cpp/phystech/hm-*` | g++ | каждая `hm-*` автономна; обычно `g++ main.cpp && ./a.out` |
| `databases/pgcli/lab-*` | PostgreSQL + pgcli (Python) | см. ниже |
| `digital-circuits/` | Quartus (`.gdf`/`.cnf`) | файлы — артефакты Quartus, не правятся вручную |
| `information-security/lab-*` | Python | `python3 main.py` в директории лабы |
| `information-theory/otik-lab-*` | Python | каждая лаба — отдельный скрипт |
| `logic-programming/lab-*` | SWI-Prolog | `swipl -s lab-N.pl -g "run_lab_tests, halt."` |
| `microprocessor-systems/lab-*` | SystemVerilog | см. ниже |
| `os-and-networks/lab*` | bash | `bash src/<script>.sh` |
| `parallel-programming/` | C# (.NET) + C++ AVX | `dotnet build *.sln`; SIMD-проекты изначально под Windows/MSVC |
| `software-architecture/lab-1..3` | C++ + `Makefile` | `make` в директории лабы (`./transport_factory`, `./transport_system`, `./airplane_control`) |
| `software-architecture/lab-4..6` | C++ (+ Qt6 где нужен GUI) | `make` (см. README конкретной лабы) |
| `software-testing/{tlabs-main,testing-java-lab-*}` | Java 11 + Maven (JUnit 5, Mockito, JaCoCo) | `mvn test` |

Предметы, в которых только `*.md`-отчёты (`electronics/`, `human-machine-interface/`, `internet-programming/`, `math-logic/`, `otik/`, `software-design/`), кода для сборки не содержат.

### Workflow для БД (`databases/pgcli/`)

Лабы работают с демо-БД PostgresPro `demo` (схема `bookings`):

```bash
pg demo                           # alias, запускающий pgcli на демо-БД
# внутри pgcli:
\c demo
SET search_path = bookings;
\i ../lab-3/01_schema_update.sql
```

**Порядок применения скриптов важен:** lab-3 должен быть применён до 4–8 (он добавляет колонки, на которые опираются последующие лабы). Lab-5 — предусловие для lab-8. Lab-7 и lab-8 — это Python-приложения (`python3 lab-7/app.py`) на `psycopg2` из flake. Канонический порядок — в `databases/pgcli/README.md`.

### SystemVerilog (`microprocessor-systems/`)

Два симулятора в зависимости от лабы:

```bash
# iverilog — для лаб 1–4 (простые testbench'и)
iverilog -g2012 -o sim design.sv testbench.sv && vvp sim

# verilator — для лаб с `import pkg::*` (лаба 5+)
verilator --binary --sv --timing alu_opcodes_pkg.sv csr_pkg.sv decoder_pkg.sv design.sv testbench.sv -o simv && ./simv
```

Волновые диаграммы — в `wave.vcd`, смотри через `gtkwave wave.vcd`. В каждой лабе есть `README.md` (практика) и `THEORY.md` (защита/синтаксис) — при правках читай оба.

## Соглашения, которые надо держать

- **Нумерация лаб по разным предметам неконсистентна** (`lab-1` vs `lab1` vs `lab-01`). Не выравнивай — следуй существующему стилю предмета.
- В некоторых лабах рядом лежат `README.md` и `README_OLD.md` (`software-architecture/lab-2`, `lab-3`) — `_OLD` оставлен сознательно, не удаляй.
- В `cpp/phystech/` есть пары вида `hm-2` и `hm-2-fix` — `-fix` это правки после ревью, обе версии нужны.
- Сгенерированные артефакты (`*.o`, `target/`, `obj/`, `build/`, `obj_dir/`, Quartus `*.rpt`/`*.fit`/`*.pin`) уже под `.gitignore`; бинари нескольких лаб (`transport_factory`, `airplane_control`, `transport_system`) явно прописаны в `.gitignore` по пути.

## Особенности предмета "Проектирование и архитектура программных систем" (`software-architecture/`)

Преподаватель по этому предмету **строгий и требователен к точному соответствию методичке** (`ЛР 1-6.pdf`, `ЛР 7-8.pdf`). Типичные претензии, которые он уже высказывал по лабам 1–3:

- **лишние классы вне ролей паттерна** — каждый новый класс должен соответствовать одному из участников паттерна (AbstractFactory/ConcreteFactory/AbstractProduct/ConcreteProduct/Client для AF; Director/Builder/Product для Builder; Component/Leaf/Composite/Client для Composite и т.д.); никаких "дополнительных демонстраций универсальности" (типа PizzaFactory в довесок к Taxi/Bus) и никаких прослоек вроде `Simulation` поверх клиентского кода;
- **несовпадение имён и иерархии с методичкой** — если в методичке `Component` — это абстрактный базовый, а `Picture` — `Composite`, то и в лабе про самолёт `Airplane` должен **сам быть `Composite`**, а не отдельным классом-клиентом со своей коллекцией;
- **слишком абстрактные иерархии для простых атрибутов** — `Passenger` с подклассами `AdultPassenger`/`ChildPassenger`/`BenefitPassenger` оправдан только если задание явно требует разного поведения; если же отличие — это просто атрибут (категория, цена билета), хватит одного класса с enum-полем.

При работе с лабами 4–6:
- Структура классов, имена ролей и сигнатуры методов должны быть **в точности из примера в методичке** для соответствующего паттерна (Proxy/Interpreter/Observer).
- В README обязательны UML-диаграмма классов (Mermaid `classDiagram`) и диаграмма последовательности (Mermaid `sequenceDiagram`) — это явное требование методички ("Разработать UML-диаграммы (диаграмму классов и диаграмму последовательности)").
- В README также должен быть текст работающей программы (или ссылка на исходники) и результат выполнения программы — это формальное требование к отчёту.
- В разделе "Ответы на контрольные вопросы" обязательно покрывать вопросы из конца раздела методички.
- Бинари этих лаб попадают под `.gitignore` — добавляй конкретный путь, если новый.
