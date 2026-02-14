import argparse
import logging
import math
from pathlib import Path
from collections import Counter
import heapq
import matplotlib.pyplot as plt
import pandas as pd

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        if self.freq == other.freq:
            if self.char is None:
                return True
            if other.char is None:
                return False
            return self.char < other.char
        return self.freq < other.freq


def get_huffman_codes(freqs):
    if not freqs:
        return {}

    pq = [HuffmanNode(c, f) for c, f in freqs.items() if f > 0]
    if not pq:
        return {}
    heapq.heapify(pq)

    while len(pq) > 1:
        left = heapq.heappop(pq)
        right = heapq.heappop(pq)
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left, merged.right = left, right
        heapq.heappush(pq, merged)

    codes = {}

    def generate(node, code=""):
        if node is None:
            return
        if node.char is not None:
            codes[node.char] = code if code else "0"
        else:
            generate(node.left, code + "0")
            generate(node.right, code + "1")

    generate(pq[0])
    return codes


def normalize_freqs(freqs_64, B):
    max_freq_64 = max(freqs_64.values()) if freqs_64 else 0
    if max_freq_64 == 0:
        return {i: 0 for i in range(256)}

    max_b_val = (1 << B) - 1

    norm_freqs = {}
    for char_code in range(256):
        freq = freqs_64.get(char_code, 0)
        if freq == 0:
            norm_freqs[char_code] = 0
        else:
            if max_freq_64 == 1:
                norm_val = max_b_val if freq == 1 else 0
            else:
                norm_val = round((freq / max_freq_64) * max_b_val)

            norm_freqs[char_code] = max(1, int(norm_val))

    return norm_freqs


def analyze_file(filepath: Path):
    logging.info(f"Анализ файла: {filepath}")
    data = filepath.read_bytes()
    if not data:
        logging.warning(f"Файл {filepath} пуст, пропуск.")
        return None

    freqs_64 = Counter(data)
    full_freqs_64 = {i: freqs_64.get(i, 0) for i in range(256)}

    results = []
    for B in range(1, 65):
        norm_freqs = normalize_freqs(full_freqs_64, B)
        codes = get_huffman_codes(norm_freqs)

        if not codes:
            continue

        e_b_bits = sum(
            full_freqs_64.get(char, 0) * len(code) for char, code in codes.items()
        )
        E_B = math.ceil(e_b_bits / 8)
        G_B = E_B + math.ceil(256 * B / 8)

        results.append({"B": B, "E_B": E_B, "G_B": G_B})

    if not results:
        logging.warning(f"Не удалось получить результаты для {filepath}")
        return None

    df = pd.DataFrame(results)
    B_star_row = df.loc[df["G_B"].idxmin()]
    B_star = int(B_star_row["B"])

    print(f"\n--- Результаты для файла: {filepath.name} ---")
    print(
        f"Оптимальная разрядность B* = {B_star} (минимальный G_B = {int(B_star_row['G_B'])} байт)"
    )

    print("\nСравнение для B = 4, 8, 32, 64:")
    print(" B | Сжатые данные (E_B) | Полный архив (G_B)")
    print("---|-----------------------|--------------------")
    for B_val in [4, 8, 32, 64]:
        res = df[df["B"] == B_val].iloc[0]
        print(f"{int(res['B']):2} | {int(res['E_B']):<21} | {int(res['G_B'])}")

    return df


def plot_results(all_dfs, output_path: Path):
    if not all_dfs or len(all_dfs) < 10:
        logging.warning("Для построения графиков необходимо 10 или более файлов.")
        return

    logging.info("Построение графиков...")
    df_concat = pd.concat(all_dfs)

    base_64 = (
        df_concat[df_concat["B"] == 64]
        .set_index("file_name")[["E_B", "G_B"]]
        .rename(columns={"E_B": "E_64", "G_B": "G_64"})
    )
    df_merged = pd.merge(df_concat, base_64, on="file_name", how="left")

    df_merged = df_merged[df_merged["E_64"] > 0]
    df_merged = df_merged[df_merged["G_64"] > 0]

    df_merged["E_ratio"] = df_merged["E_B"] / df_merged["E_64"]
    df_merged["G_ratio"] = df_merged["G_B"] / df_merged["G_64"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), sharex=True)

    # --- Бонус ---
    df_merged.boxplot(column="E_ratio", by="B", ax=ax1, showfliers=False)
    ax1.set_title("Зависимость относительного размера сжатых данных (E_B/E_64) от B")
    ax1.set_ylabel("Отношение E_B/E_64")
    ax1.grid(axis="y", linestyle="--", alpha=0.7)

    df_merged.boxplot(column="G_ratio", by="B", ax=ax2, showfliers=False)
    ax2.set_title("Зависимость относительного размера архива (G_B/G_64) от B")
    ax2.set_xlabel("Разрядность частот (B)")
    ax2.set_ylabel("Отношение G_B/G_64")
    ax2.grid(axis="y", linestyle="--", alpha=0.7)

    plt.suptitle(
        f"Анализ влияния разрядности частот на сжатие Хаффмана ({len(all_dfs)} файлов)",
        fontsize=16,
    )
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    plot_filepath = output_path / "bit_depth_analysis.png"
    plt.savefig(plot_filepath)
    logging.info(f"Графики сохранены в '{plot_filepath}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Анализатор оптимальной разрядности частот для сжатия Хаффмана (ЛР4.№2)."
    )
    parser.add_argument(
        "paths",
        type=Path,
        nargs="+",
        help="Путь к одному или нескольким файлам/каталогам для анализа.",
    )
    parser.add_argument(
        "--plot-output",
        type=Path,
        default=Path("."),
        help="Каталог для сохранения графика.",
    )
    args = parser.parse_args()

    all_files = []
    for path in args.paths:
        if path.is_file():
            all_files.append(path)
        elif path.is_dir():
            all_files.extend([
                p for p in path.rglob("*") if p.is_file() and p.stat().st_size > 0
            ])

    if not all_files:
        logging.error("Не найдено файлов для анализа.")
    else:
        all_dfs = []
        for file in all_files:
            try:
                df = analyze_file(file)
                if df is not None:
                    df["file_name"] = file.name
                    all_dfs.append(df)
            except Exception as e:
                logging.error(f"Не удалось проанализировать файл {file}: {e}")

        if len(all_dfs) >= 10:
            plot_results(all_dfs, args.plot_output)
