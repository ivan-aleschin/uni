"""
ДЗ-1. Обработка результатов измерений. Вариант 1.

Скрипт повторяет ручной расчёт из отчёта (report.md) по шагам УМП:
задача 1 - прямое однократное измерение (сопротивление),
задача 2 - прямое многократное измерение (диаметр валика),
задача 3 - косвенное измерение (g по маятнику).
Промежуточные погрешности округляются вверх так же, как в примерах УМП.
"""

import math
from decimal import Decimal, ROUND_CEILING

# Табличные значения из УМП (раздел 1 и Д.З.-1)
K_ONE_SHOT = {0.95: {1: 1.00, 2: 1.10, 3: 1.10, 4: 1.10}}  # табл. 2, однократное
STUDENT = {(0.95, 15): 2.145}                              # табл. 1.4
GRUBBS = {(0.95, 15): 2.549}                               # табл. 1.1, q = 0,05


def round_up(x: float) -> float:
    """Округление погрешности вверх: первая цифра 1 или 2 - две значащие, иначе одна."""
    d = Decimal(repr(x))
    exp = d.adjusted()                  # порядок первой значащей цифры
    first = int(str(d.scaleb(-exp))[0])
    digits = 2 if first in (1, 2) else 1
    step = Decimal(1).scaleb(exp - digits + 1)
    return float((d / step).to_integral_value(ROUND_CEILING) * step)


def task1():
    print("Задача 1. Прямое однократное измерение сопротивления R")
    r = [7.35, 7.40, 7.33]              # Ом
    r_mean = sum(r) / len(r)
    print(f"  среднее R = {r_mean:.4f} Ом")

    # класс точности 0,2 по приведённой погрешности, предел 10 Ом
    d_si = 0.2 * 10 / 100
    d_met = 0.03
    theta = [d_si, abs(d_met)]
    print(f"  Θ1 = Δси = {d_si:.3f} Ом, Θ2 = |Δмет| = {abs(d_met):.3f} Ом")

    k = K_ONE_SHOT[0.95][len(theta)]
    big_theta = k * math.sqrt(sum(t * t for t in theta))
    delta = round_up(big_theta)
    print(f"  Θ(0,95) = {k:.2f}·√ΣΘi² = {big_theta:.5f} Ом -> Δ = {delta} Ом")
    print(f"  Ответ: R = ({r_mean:.2f} ± {delta:.2f}) Ом, P = 0,95; "
          f"{r_mean - delta:.2f} Ом <= R <= {r_mean + delta:.2f} Ом")
    print()


def task2():
    print("Задача 2. Прямое многократное измерение диаметра d")
    dev = [0, 2, 1, -1, 0, -3, -1, 1, -1, 2, 0, 4, -2, -1, 0]   # мкм от d0
    n = len(dev)
    mean = sum(dev) / n
    s = math.sqrt(sum((x - mean) ** 2 for x in dev) / (n - 1))
    print(f"  n = {n}, Σx = {sum(dev)}, среднее = {mean:.4f} мкм")
    print(f"  Σ(x - x̄)² = {sum((x - mean) ** 2 for x in dev):.4f}, S = {s:.4f} мкм")

    # критерий Граббса для крайних значений ряда
    g_t = GRUBBS[(0.95, n)]
    g1 = (max(dev) - mean) / s
    g2 = (mean - min(dev)) / s
    print(f"  G1 = {g1:.3f}, G2 = {g2:.3f}, Gт = {g_t} -> выбросов "
          f"{'нет' if max(g1, g2) <= g_t else 'есть'}")

    s_mean = s / math.sqrt(n)
    t = STUDENT[(0.95, n)]
    eps_raw = t * s_mean
    eps = round_up(eps_raw)
    print(f"  S(x̄) = {s_mean:.4f} мкм, ε = {t}·{s_mean:.4f} = {eps_raw:.4f} -> {eps} мкм")

    # НСП: основная погрешность СИ и методическая (75 % от неё), m = 2 < 3
    theta = [0.4, 0.75 * 0.4]
    big_theta = sum(abs(x) for x in theta)
    s_theta = big_theta / math.sqrt(3)
    print(f"  Θ1 = {theta[0]:.2f}, Θ2 = {theta[1]:.2f} мкм, ΘΣ = Σ|Θi| = {big_theta:.2f} мкм")

    s_sum = math.sqrt(s_mean ** 2 + s_theta ** 2)
    k = (eps + big_theta) / (s_mean + s_theta)
    delta_raw = k * s_sum
    delta = round_up(delta_raw)
    print(f"  SΘ = {s_theta:.4f}, SΣ = {s_sum:.4f} мкм, K = {k:.3f}")
    print(f"  Δ = K·SΣ = {delta_raw:.4f} -> {delta} мкм")

    d = 100.000 + mean / 1000
    print(f"  Ответ: d = ({d:.4f} ± {delta / 1000:.4f}) мм, P = 0,95; "
          f"{d - delta / 1000:.4f} мм <= d <= {d + delta / 1000:.4f} мм")
    print()


def task3():
    print("Задача 3. Косвенное измерение g по периоду маятника")
    t100, d_t100 = 132, 0.001           # с, время 100 колебаний
    l, d_l = 0.435, 0.005e-3            # м, погрешность 0,005 мм
    t = t100 / 100
    d_t = d_t100 / 100

    g = 4 * math.pi ** 2 * l / t ** 2
    rel_l = d_l / l
    rel_t = d_t / t
    print(f"  T = {t} с, ΔT = {d_t} с, g = 4π²l/T² = {g:.6f} м/с²")
    print(f"  δl = {rel_l:.4e}, δT = {rel_t:.4e}")

    # границы аргументов даны без вероятности, т.е. как предельные (P = 1):
    # для A = a^m·b^n по табл. 5 δA = |m|·δa + |n|·δb
    rel_g = rel_l + 2 * rel_t
    d_g_raw = rel_g * g
    d_g = round_up(d_g_raw)
    print(f"  δg = δl + 2δT = {rel_g:.4e}, Δg = {d_g_raw:.4e} -> {d_g} м/с²")
    print(f"  Ответ: g = ({g:.5f} ± {d_g:.5f}) м/с²; "
          f"{g - d_g:.5f} <= g <= {g + d_g:.5f} м/с²")

    # для сравнения: квадратичное суммирование, если границы считать при P < 1
    rel_q = math.sqrt(rel_l ** 2 + (2 * rel_t) ** 2)
    print(f"  (при P < 1: δg = √(δl² + (2δT)²) = {rel_q:.4e}, "
          f"Δg = {rel_q * g:.4e} -> {round_up(rel_q * g)} м/с²)")


if __name__ == "__main__":
    task1()
    task2()
    task3()
