"""
Расчёт размерной цепи механизма толкателя (Приложение 3), вариант 1.

A1 = 150 (закон Симпсона), A2 = 20 (Симпсона), A3 = 100 (нормальный),
A4 = 100 (нормальный), A5 = 120 (равновероятный), α = 30°,
AΔ с отклонениями (0; +0,1), процент риска 4,5 %.
Прямая задача стандартным способом: максимум-минимум и вероятностный метод.
Размеры в мм.
"""

import math

ALPHA = math.radians(30)
# (имя, номинал, ξ, λ'²)
LINKS = [
    ("A1", 150, +1, 1 / 6),
    ("A2", 20, +1, 1 / 6),
    ("A3", 100, math.cos(ALPHA), 1 / 9),
    ("A4", 100, -1, 1 / 9),
    ("A5", 120, -1, 1 / 3),
]
T_D, C_D = 0.1, 0.05          # допуск и середина поля замыкающего звена
T_RISK = 2.0                  # P = 4,5 %


def nominal():
    a_d = sum(xi * a for _, a, xi, _ in LINKS)
    print(f"AΔ = 150 + 20 + 100·cos30° − 100 − 120 = {a_d:.3f} мм")
    return a_d


def deviations(tol, c0):
    """Отклонения звеньев и проверка замыкающего звена."""
    up = lo = 0.0
    for (name, _, xi, _), t, c in zip(LINKS, tol, c0):
        b, h = c + t / 2, c - t / 2
        print(f"    {name}: T = {t:.4f}, Δ0 = {c:+.4f}, ΔВ = {b:+.4f}, ΔН = {h:+.4f}")
        if xi > 0:
            up += xi * b
            lo += xi * h
        else:
            up += xi * h
            lo += xi * b
    return up, lo


def solve(tol, title):
    print(title)
    # середины: A1 охватываемый (−T/2), A2, A3, A4 - прочие (0), A5 - из (3.2)
    c0 = [-tol[0] / 2, 0.0, 0.0, 0.0]
    rest = sum(xi * c for (_, _, xi, _), c in zip(LINKS, c0))
    c5 = (C_D - rest) / LINKS[4][2]
    c0.append(c5)
    print(f"    Δ05 = ({C_D} − ({rest:+.4f})) / (−1) = {c5:+.4f}")
    return deviations(tol, c0)


def main():
    nominal()
    s_xi = sum(abs(xi) for _, _, xi, _ in LINKS)
    t_avg = T_D / s_xi
    print(f"max-min: Σ|ξ| = {s_xi:.3f}, Tср = {t_avg:.5f}")
    tol = [0.025, 0.016, 0.020, 0.020]
    t5 = T_D - sum(abs(xi) * t for (_, _, xi, _), t in zip(LINKS, tol))
    print(f"    T5 из (3.6) = {t5:.5f} -> 0,021")
    tol.append(0.021)
    t_sum = sum(abs(xi) * t for (_, _, xi, _), t in zip(LINKS, tol))
    print(f"    проверка TΔ = {t_sum:.5f}")
    up, lo = solve(tol, "  отклонения (max-min):")
    print(f"    проверка: ΔВΔ = {up:+.4f}, ΔНΔ = {lo:+.4f}")

    s_l = sum(xi ** 2 * lam for _, _, xi, lam in LINKS)
    t_avg = T_D / (T_RISK * math.sqrt(s_l))
    print(f"вероятн.: Σξ²λ² = {s_l:.5f}, Tср = {t_avg:.5f}")
    tol = [0.06, 0.04, 0.05, 0.05]
    part = sum(xi ** 2 * lam * t ** 2 for (_, _, xi, lam), t in zip(LINKS, tol))
    t5 = math.sqrt(((T_D / T_RISK) ** 2 - part) / LINKS[4][3])
    print(f"    Σ(первые 4) = {part:.7f}, T5 из (3.15) = {t5:.5f} -> 0,056")
    tol.append(0.056)
    check = T_RISK * math.sqrt(sum(xi ** 2 * lam * t ** 2
                                   for (_, _, xi, lam), t in zip(LINKS, tol)))
    print(f"    проверка TΔ = {check:.5f} ({(T_D - check) / T_D * 100:.1f} % меньше)")
    solve(tol, "  отклонения (вероятн.):")
    print(f"    границы замыкающего звена: {C_D - check / 2:+.4f} ... {C_D + check / 2:+.4f}")


if __name__ == "__main__":
    main()
