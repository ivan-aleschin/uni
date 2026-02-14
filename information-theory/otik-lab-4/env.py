from pathlib import Path
import os

base_dir = Path("test_environment")
source_dir = base_dir / "source_data"
archives_dir = base_dir / "archives"
output_dir = base_dir / "output_data"

source_dir.mkdir(parents=True, exist_ok=True)
(source_dir / "subdir").mkdir(exist_ok=True)
archives_dir.mkdir(exist_ok=True)
output_dir.mkdir(exist_ok=True)

print("Структура каталогов создана.")


# 1. Маленький текстовый файл (хорошо сжимается)
(source_dir / "small.txt").write_text(
    "Это тестовый файл для проверки базовой функциональности архиватора.",
    encoding='utf-8'
)

# 2. Большой текстовый файл (хорошо сжимается)
(source_dir / "book.txt").write_text(
    ("Это пример текста, который должен хорошо сжиматься. "
     "Повторение слов и символов создает избыточность, "
     "которую алгоритмы энтропийного сжатия, такие как Хаффман или "
     "арифметическое кодирование, эффективно устраняют. "
     "Чем длиннее текст и чем более предсказуемы в нем последовательности, "
     "тем выше будет степень сжатия. Проверка, проверка, проверка.\n") * 500,
    encoding='utf-8'
)

# 3. Файл с плохой сжимаемостью (почти случайные данные)
(source_dir / "random.dat").write_bytes(os.urandom(2048))

# 4. Файл с высокой избыточностью (для проверки максимального сжатия)
(source_dir / "repeat.txt").write_bytes(b'A' * 1024 + b'B' * 512)

# 5. Файл во вложенной папке
(source_dir / "subdir" / "nested_file.txt").write_text("Файл во вложенном каталоге.")

print("Тестовые файлы созданы в 'test_environment/source_data'.")