from collections import Counter
import math
import heapq
from heapq import heappush, heappop

def to_3bit_binary(num):
    """Преобразование символа в трёхбитный код"""
    return format(int(num), '03b')

def huffman_tree_detailed(freq):
    """Построение кода Хаффмана с выводом этапов"""
    print("ЭТАПЫ ПОСТРОЕНИЯ КОДА ХАФФМАНА:")
    heap = [[weight, [sym, ""]] for sym, weight in freq.items()]
    heapq.heapify(heap)
    step = 1
    
    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        
        print(f"Шаг {step}: объединяем {lo[1:]} (вес {lo[0]}) и {hi[1:]} (вес {hi[0]})")
        
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
            
        new_node = [lo[0] + hi[0]] + lo[1:] + hi[1:]
        heapq.heappush(heap, new_node)
        step += 1
    
    print("Формируем итоговые коды...")
    return sorted(heapq.heappop(heap)[1:], key=lambda p: (len(p[-1]), p))

def shannon_fano_detailed(freq):
    """Построение кода Шеннона-Фано с выводом этапов"""
    symbols = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
    print("ЭТАПЫ ПОСТРОЕНИЯ КОДА ШЕННОНА-ФАНО:")
    print(f"Начальная сортировка: {symbols}")
    
    def build_codes(symbols_list, code_prefix="", level=0):
        indent = "  " * level
        if len(symbols_list) == 1:
            print(f"{indent}Единственный символ: '{symbols_list[0][0]}' → код {code_prefix}")
            return [(symbols_list[0][0], code_prefix)]
        if len(symbols_list) == 0:
            return []
        
        total_freq = sum(f for _, f in symbols_list)
        half = total_freq / 2
        
        current_sum = 0
        split_index = 0
        
        print(f"{indent}Разделение группы {[(s, f) for s, f in symbols_list]} (сумма={total_freq})")
        
        for i, (sym, f) in enumerate(symbols_list):
            current_sum += f
            if current_sum >= half:
                split_index = i + 1
                break
        
        group1 = symbols_list[:split_index]
        group2 = symbols_list[split_index:]
        
        sum1 = sum(f for _, f in group1)
        sum2 = sum(f for _, f in group2)
        
        print(f"{indent}Группа 1 ({sum1}): {[(s, f) for s, f in group1]} → +0")
        print(f"{indent}Группа 2 ({sum2}): {[(s, f) for s, f in group2]} → +1")
        
        codes = []
        codes.extend(build_codes(group1, code_prefix + "0", level + 1))
        codes.extend(build_codes(group2, code_prefix + "1", level + 1))
        return codes
    
    codes = build_codes(symbols)
    return sorted(codes, key=lambda x: x[0])

# Исходные данные
C = "762436265242"
print(f"Сообщение C = {C}")
print(f"Алфавит: 0-7 (трёхбитные символы)\n")

# =========================================================================
# ИСХОДНОЕ ТРЁХБИТНОЕ КОДИРОВАНИЕ
# =========================================================================
print("="*60)
print("ИСХОДНОЕ ТРЁХБИТНОЕ КОДИРОВАНИЕ СИМВОЛОВ")
print("="*60)

print("Таблица трёхбитного кодирования:")
print("Символ | Трёхбитный код")
print("-" * 25)
for i in range(8):
    print(f"  {i}    |     {to_3bit_binary(i)}")

print(f"\nИсходное сообщение: {C}")

# Кодируем сообщение в трёхбитном формате
original_3bit_encoded = ''.join(to_3bit_binary(ch) for ch in C)
print(f"Трёхбитный код сообщения: {original_3bit_encoded}")

symbol_length = len(C)
bit_length_original = len(original_3bit_encoded)

print(f"Исходная длина |C| = {symbol_length} символов = {bit_length_original} бит")
print(f"В трёхбитных байтах: {symbol_length} трёхбитных байт\n")

# Частоты символов
freq = Counter(C)
print("ЧАСТОТЫ СИМВОЛОВ:")
for ch in sorted(freq.keys()):
    print(f"'{ch}': {freq[ch]} (трёхбитный код: {to_3bit_binary(ch)})")
print()

# ОПЦИИ ПОСТРОЕНИЯ (единые для всех методов)
print("ОПЦИИ ПОСТРОЕНИЯ (единые для всех кодов):")
print("- Порядок сортировки при равных частотах: по возрастанию символа")
print("- Схема маркировки ветвей: левая = 0, правая = 1") 
print("- Для Шеннона-Фано: первая группа с суммой частот ≥ половины общей суммы")
print()

# =========================================================================
# КОД ХАФФМАНА
# =========================================================================
print("="*60)
print("КОД ХАФФМАНА (Xf)")
print("="*60)
huff_codes = huffman_tree_detailed(freq)
print("\nИТОГОВЫЕ КОДЫ ХАФФМАНА:")
print("Символ | Частота | Трёхбитный код | Код Хаффмана")
print("-" * 50)
for sym, code in huff_codes:
    print(f"  '{sym}'  |    {freq[sym]}    |      {to_3bit_binary(sym)}     |    {code}")

huff_encoded = ''.join(next(code for s, code in huff_codes if s == ch) for ch in C)
print(f"\nКод сообщения Xf(C) = {huff_encoded}")
huff_bit_length = len(huff_encoded)
huff_tribyte_length = math.ceil(huff_bit_length / 3)
print(f"Длина |Xf(C)| = {huff_bit_length} бит = {huff_tribyte_length} трёхбитных байт")

# =========================================================================
# КОД ШЕННОНА-ФАНО
# =========================================================================
print("\n" + "="*60)
print("КОД ШЕННОНА-ФАНО (ШФ)")
print("="*60)
shannon_fano_codes = shannon_fano_detailed(freq)
print("\nИТОГОВЫЕ КОДЫ ШЕННОНА-ФАНО:")
print("Символ | Частота | Трёхбитный код | Код Шеннона-Фано")
print("-" * 55)
for sym, code in shannon_fano_codes:
    print(f"  '{sym}'  |    {freq[sym]}    |      {to_3bit_binary(sym)}     |       {code}")

sf_encoded = ''.join(next(code for s, code in shannon_fano_codes if s == ch) for ch in C)
print(f"\nКод сообщения ШФ(C) = {sf_encoded}")
sf_bit_length = len(sf_encoded)
sf_tribyte_length = math.ceil(sf_bit_length / 3)
print(f"Длина |ШФ(C)| = {sf_bit_length} бит = {sf_tribyte_length} трёхбитных байт")

# =========================================================================
# КОД ШЕННОНА
# =========================================================================
print("\n" + "="*60)
print("КОД ШЕННОНА (Ш)")
print("="*60)
print("ЭТАПЫ ПОСТРОЕНИЯ (табличный метод):")
total = sum(freq.values())
symbols_sorted = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
codes = []
cumulative_prob = 0

print("Символ | Частота | Вероятность | l = ⌈-log₂(p)⌉ | Накопленная | Код Шеннона")
print("-" * 75)

for sym, count in symbols_sorted:
    prob = count / total
    code_length = math.ceil(-math.log2(prob))
    code_value = int(cumulative_prob * (2 ** code_length))
    code = format(code_value, f'0{code_length}b')
    
    print(f"  '{sym}'  |    {count}    |   {prob:.4f}   |       {code_length}       |   {cumulative_prob:.4f}   |     {code}")
    
    codes.append((sym, code, code_length))
    cumulative_prob += prob

print("\nИТОГОВЫЕ КОДЫ ШЕННОНА:")
print("Символ | Частота | Трёхбитный код | Код Шеннона")
print("-" * 50)
for sym, code, code_len in codes:
    print(f"  '{sym}'  |    {freq[sym]}    |      {to_3bit_binary(sym)}     |    {code}")

shannon_encoded = ''.join(next(code for s, code, _ in codes if s == ch) for ch in C)
print(f"\nКод сообщения Ш(C) = {shannon_encoded}")
shannon_bit_length = len(shannon_encoded)
shannon_tribyte_length = math.ceil(shannon_bit_length / 3)
print(f"Длина |Ш(C)| = {shannon_bit_length} бит = {shannon_tribyte_length} трёхбитных байт")

# =========================================================================
# СРАВНЕНИЕ РЕЗУЛЬТАТОВ
# =========================================================================
print("\n" + "="*60)
print("СРАВНЕНИЕ РЕЗУЛЬТАТОВ")
print("="*60)

print(f"Исходное кодирование:     {bit_length_original:2d} бит = {symbol_length:2d} трёхбитных байт")
print(f"Код Хаффмана (Xf):        {huff_bit_length:2d} бит = {huff_tribyte_length:2d} трёхбитных байт")
print(f"Код Шеннона-Фано (ШФ):    {sf_bit_length:2d} бит = {sf_tribyte_length:2d} трёхбитных байт") 
print(f"Код Шеннона (Ш):          {shannon_bit_length:2d} бит = {shannon_tribyte_length:2d} трёхбитных байт")

# Эффективность сжатия
compression_huff = (1 - huff_bit_length / bit_length_original) * 100
compression_sf = (1 - sf_bit_length / bit_length_original) * 100
compression_sh = (1 - shannon_bit_length / bit_length_original) * 100

print(f"\nЭффективность сжатия:")
print(f"Хаффман:    {compression_huff:.1f}%")
print(f"Шеннон-Фано: {compression_sf:.1f}%") 
print(f"Шеннон:      {compression_sh:.1f}%")

# Оценка информации
entropy = -sum((count / total) * math.log2(count / total) for count in freq.values())
info_bits = entropy * total
info_tribytes = info_bits / 3

print(f"\nОценка I_БП(C) = {info_bits:.2f} бит = {info_tribytes:.2f} трёхбитных байт")