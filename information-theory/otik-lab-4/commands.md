#### Базовое кодирование (без сжатия)

```bash
python archiver.py encode test_environment/source_data/small.txt test_environment/archives/small_none.arc -a none
python archiver.py decode test_environment/archives/small_none.arc test_environment/output_data
```
  * **Проверка:**
```bash
fc /b "test_environment\source_data\small.txt" "test_environment\output_data\small.txt"
```

#### Сжатие Хаффмана (Л4.№1)

```bash
python archiver.py encode test_environment/source_data/book.txt test_environment/archives/book_huffman.arc -a huffman
python archiver.py decode test_environment/archives/book_huffman.arc test_environment/output_data
```
  * **Проверка:**
```bash
fc /b "test_environment\source_data\book.txt" "test_environment\output_data\book.txt"
```

#### «Интеллектуальный» кодер (Бонус Л4.№4)
```bash
python archiver.py encode test_environment/source_data/random.dat test_environment/archives/random_auto.arc -a huffman

python archiver.py encode test_environment/source_data/random.dat test_environment/archives/random_forced.arc -a huffman --force
```
* **Проверка:** В выводе первой команды появилось сообщение `WARNING: Сжатие неэффективно...`. Сравнив размеры файлов `random_auto.arc` и `random_forced.arc`.

#### Бонусные алгоритмы (Л4.№5, Л4.№6)

```bash
# Арифметический
python archiver.py encode test_environment/source_data/book.txt test_environment/archives/book_arithmetic.arc -a arithmetic
python archiver.py decode test_environment/archives/book_arithmetic.arc test_environment/output_data

# Шеннон
python archiver.py encode test_environment/source_data/book.txt test_environment/archives/book_shannon.arc -a shannon
python archiver.py decode test_environment/archives/book_shannon.arc test_environment/output_data
```
* **Проверка:** Сравнили размеры архивов (`book_huffman.arc`, `book_arithmetic.arc`, `book_shannon.arc`). Арифметический самый маленький.

#### Работа с каталогами (Бонус ЛР3)

```bash
python archiver.py encode test_environment/source_data test_environment/archives/fulldir.arc -a huffman
python archiver.py decode test_environment/archives/fulldir.arc test_environment/output_data/restored_dir
```
* **Проверка:** Визуально проверили, что в папке `test_environment/output_data/restored_dir` воссоздана вся структура, включая `subdir` и все файлы.




### Команды для `analyzer.py`


#### 1\. Анализ одного файла

```bash
python analyzer.py test_environment/source_data/book.txt
```
* **Результат:** В консоли появилась текстовая таблица с результатами для файла `book.txt`, показывающая размеры `E_B` и `G_B` для разрядностей 4, 8, 32, 64, а также вычисленное оптимальное значение `B*`.

#### 2\. Анализ нескольких конкретных файлов


```bash
python analyzer.py test_environment/source_data/book.txt test_environment/source_data/random.dat test_environment/source_data/repeat.txt
```
* **Результат:** В консоли последовательно появились три отдельные таблицы с результатами для каждого из указанных файлов.

#### 3\. Анализ целого каталога и построение графиков (Бонус)

```bash
python analyzer.py ../labs-files
```
* **Результат:**
1.  В консоли вывелось множество таблиц — по одной для каждого файла в каталоге `../labs-files`.
2.  Сохранилось изображение
3.  В папке со скриптом появился файл `bit_depth_analysis.png` с двумя графиками типа "ящик с усами".
