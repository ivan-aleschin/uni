"""
ДЗ-3. Вариант 1.

3.1 - расчёт допусков размерной цепи для точного сопряжения d4 = ∅4,5 E9-m5
      из варианта 1-А ДЗ-2: обратная задача (пример 5 УМП) и прямая задача
      (пример 6 УМП) методами максимума-минимума и теоретико-вероятностным.
3.2 - параметрическая размерная цепь, схема 1, вариант 1-1: пределы
      регулировки подстроечного резистора r* (пример 1 раздела 5 УМП).
Отклонения в 3.1 - в мкм, сопротивления в 3.2 - в кОм.
"""

import math

# λ'² для законов распределения (ГОСТ 16320-80)
LAM2 = {"нормальный": 1 / 9, "Симпсона": 1 / 6, "равновероятный": 1 / 3}


def chain_31():
    print("3.1. Размерная цепь сопряжения ∅4,5 E9-m5")
    # A1 - отверстие E9, A2 - вал m5 (табл. 2.3-2.5 УМП, св. 3 до 6 мм)
    b1, h1 = 50, 20
    b2, h2 = 9, 4
    c1, c2 = (b1 + h1) / 2, (b2 + h2) / 2
    t1, t2 = b1 - h1, b2 - h2
    print(f"  A1: ΔВ = +{b1}, ΔН = +{h1}, ΔС = +{c1:g}, T = {t1}")
    print(f"  A2: ΔВ = +{b2}, ΔН = +{h2}, ΔС = +{c2:g}, T = {t2}")

    # обратная задача, максимум-минимум
    t_d = t1 + t2
    c_d = c1 - c2
    print(f"  max-min: TΔ = {t_d}, Δ0Δ = {c_d:+g}, "
          f"ΔВΔ = {c_d + t_d / 2:+g}, ΔНΔ = {c_d - t_d / 2:+g}")
    # обратная задача, вероятностный метод: нормальный закон, t = 3
    t_p = 3 * math.sqrt(LAM2["нормальный"] * (t1 ** 2 + t2 ** 2))
    print(f"  вероятн.: TΔ = 3·√(1/9·({t1}² + {t2}²)) = {t_p:.3f}, "
          f"ΔВΔ = {c_d + t_p / 2:+.1f}, ΔНΔ = {c_d - t_p / 2:+.1f}")

    # прямая задача: Smax = +46, Smin = +11
    smax, smin = 46, 11
    t_d = smax - smin
    c_d = (smax + smin) / 2
    print(f"  прямая: TΔ = {t_d}, Δ0Δ = {c_d:+g}")

    t_avg = t_d / 2
    print(f"  max-min: Tср = {t_avg:g}")
    a1, a2 = 20, 15                      # отверстие шире, вал уже
    lo2 = 4                              # вал: нижнее отклонение как у m
    c2 = lo2 + a2 / 2
    c1 = c_d + c2
    print(f"    T1 = {a1}, T2 = {a2}, сумма = {a1 + a2}")
    print(f"    вал: Δ02 = {c2:+g}, ΔВ2 = {c2 + a2 / 2:+g}, ΔН2 = {c2 - a2 / 2:+g}")
    print(f"    отв: Δ01 = {c1:+g}, ΔВ1 = {c1 + a1 / 2:+g}, ΔН1 = {c1 - a1 / 2:+g}")
    print(f"    проверка: ΔВΔ = {c1 + a1 / 2 - (c2 - a2 / 2):+g}, "
          f"ΔНΔ = {c1 - a1 / 2 - (c2 + a2 / 2):+g}")

    lam = LAM2["Симпсона"] + LAM2["равновероятный"]
    t_avg = t_d / (3 * math.sqrt(lam))
    print(f"  вероятн.: Tср = {t_d}/(3·√(1/6 + 1/3)) = {t_avg:.2f}")
    a1, a2 = 20, 14
    check = 3 * math.sqrt(a1 ** 2 / 6 + a2 ** 2 / 3)
    c2 = lo2 + a2 / 2
    c1 = c_d + c2
    print(f"    T1 = {a1}, T2 = {a2}, проверка TΔ = {check:.2f} "
          f"({(t_d - check) / t_d * 100:.1f} % меньше заданного)")
    print(f"    вал: Δ02 = {c2:+g}, ΔВ2 = {c2 + a2 / 2:+g}, ΔН2 = {c2 - a2 / 2:+g}")
    print(f"    отв: Δ01 = {c1:+g}, ΔВ1 = {c1 + a1 / 2:+g}, ΔН1 = {c1 - a1 / 2:+g}")
    print(f"    середина и проверка: Δ0Δ = {c1 - c2:+g}, "
          f"границы {c1 - c2 - check / 2:+.1f} ... {c1 - c2 + check / 2:+.1f}")
    print()


def chain_32():
    print("3.2. Параметрическая цепь, схема 1, вариант 1-1")
    r_sum, d_sum = 32, 0.1
    r1, d1 = 10, 1
    rs = [(80, 4), (40, 2), (8, 4)]       # r2, r3, r4 параллельно
    g = sum(1 / r for r, _ in rs)
    rab = 1 / g
    print(f"  1/rab = {' + '.join(f'1/{r}' for r, _ in rs)} = {g:.4f}, rab = {rab:.4f} кОм")
    parts = [(rab / r) ** 2 * d for r, d in rs]
    d_ab = sum(parts)
    print("  Δrab = Σ(rab/ri)²·Δri = " + " + ".join(f"{p:.4f}" for p in parts)
          + f" = {d_ab:.4f} кОм")
    rab_r, dab_r = round(rab, 2), round(d_ab, 2)
    print(f"  rab = ({rab_r} ± {dab_r}) кОм")

    r_star = r_sum - r1 - rab_r
    print(f"  r* = {r_sum} - ({r1} + {rab_r}) = {r_star:.2f} кОм")
    # максимум-минимум: в rmin все звенья минимальны, в rmax - максимальны
    rs_1 = (r_sum - d_sum) - ((r1 - d1) + (rab_r - dab_r))
    rs_2 = (r_sum + d_sum) - ((r1 + d1) + (rab_r + dab_r))
    print(f"  r*' = {r_sum - d_sum} - ({r1 - d1} + {rab_r - dab_r:.2f}) = {rs_1:.2f} кОм")
    print(f"  r*'' = {r_sum + d_sum} - ({r1 + d1} + {rab_r + dab_r:.2f}) = {rs_2:.2f} кОм")
    lo, hi = min(rs_1, rs_2), max(rs_1, rs_2)
    print(f"  r*min = {lo:.2f}, r*max = {hi:.2f}, 2Δr* = {hi - lo:.2f}, "
          f"r* = ({(lo + hi) / 2:.2f} ± {(hi - lo) / 2:.2f}) кОм")
    print(f"  проверка: {r1 - d1} + {rab_r - dab_r:.2f} + {rs_1:.2f} = "
          f"{r1 - d1 + rab_r - dab_r + rs_1:.2f}; "
          f"{r1 + d1} + {rab_r + dab_r:.2f} + {rs_2:.2f} = {r1 + d1 + rab_r + dab_r + rs_2:.2f}")


# ---------------- схемы цепей (SVG) ----------------

def _svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" '
            f'viewBox="0 0 {w} {h}" font-family="Libertinus Serif, serif">\n'
            + "\n".join(body) + "\n</svg>\n")


def _arrow(x1, x2, y, label, up=True):
    """Звено цепи: стрелка от x1 к x2 (направление показывает знак звена)."""
    d = 1 if x2 > x1 else -1
    return [f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="black" stroke-width="0.35"/>',
            f'<path d="M{x2},{y} l{-2.2 * d},-0.9 v1.8 z" fill="black"/>',
            f'<text x="{(x1 + x2) / 2}" y="{y - 1.6 if up else y + 4.4}" font-size="3.8" '
            f'text-anchor="middle" font-style="italic">{label}</text>']


def fig_chain():
    body = []
    for x in (10, 70, 76):
        body.append(f'<line x1="{x}" y1="4" x2="{x}" y2="34" stroke="black" stroke-width="0.25"/>')
    body += _arrow(10, 76, 12, "A₁ (D)")
    body += _arrow(10, 70, 24, "A₂ (d)")
    body += _arrow(70, 76, 32, "A<tspan baseline-shift=\"sub\" font-size=\"2.8\">Δ</tspan> (S)", up=False)
    return _svg(86, 40, body)


def fig_resistors():
    body = []
    def box(x, y, w, h, lbl):
        body.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="black" stroke-width="0.35"/>')
        body.append(f'<text x="{x + w / 2}" y="{y - 1.5}" font-size="3.6" text-anchor="middle" font-style="italic">{lbl}</text>')
    def ln(x1, y1, x2, y2):
        body.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="black" stroke-width="0.35"/>')
    y = 22
    ln(4, y, 14, y); box(14, y - 3, 14, 6, "r*")
    body.append(f'<line x1="16" y1="{y + 5}" x2="27" y2="{y - 6}" stroke="black" stroke-width="0.3"/>')
    body.append(f'<path d="M27,{y - 6} l-2.2,0.8 l1.2,1.2 z" fill="black"/>')
    ln(28, y, 36, y); box(36, y - 3, 14, 6, "r₁"); ln(50, y, 60, y)
    for yy, lbl in ((8, "r₂"), (22, "r₃"), (36, "r₄")):
        ln(60, yy, 66, yy); box(66, yy - 3, 14, 6, lbl); ln(80, yy, 86, yy)
    ln(60, 8, 60, 36); ln(86, 8, 86, 36); ln(86, y, 96, y)
    for x, t in ((60, "a"), (86, "b")):
        body.append(f'<circle cx="{x}" cy="{y}" r="0.9" fill="black"/>')
        body.append(f'<text x="{x - 2.5}" y="{y - 1.5}" font-size="3.6" font-style="italic">{t}</text>')
    return _svg(100, 42, body)


if __name__ == "__main__":
    chain_31()
    chain_32()
    from pathlib import Path
    fig = Path(__file__).parent / "fig"
    fig.mkdir(exist_ok=True)
    (fig / "chain.svg").write_text(fig_chain())
    (fig / "resistors.svg").write_text(fig_resistors())
