"""Проверочный расчёт кейса «Кто съел все пирожные?» и графики для README.

Запуск: python3 check.py — печатает все числа из README, падает на assert,
если что-то не сходится, и перерисовывает img/*.svg (только стандартная библиотека).
"""

from pathlib import Path

IMG = Path(__file__).parent / "img"


# ---------- Этап 2: общая и предельная полезность ----------

TU = [0, 10, 18, 24, 28, 30, 30, 28]
MU = [TU[q] - TU[q - 1] for q in range(1, len(TU))]  # MU = ΔTU / ΔQ при ΔQ = 1
assert MU == [10, 8, 6, 4, 2, 0, -2]
assert sum(MU) == TU[-1]  # сумма предельных = общая
assert max(TU) == 30 and TU.index(30) == 5  # насыщение: TU max на 5–6-м


# ---------- Этап 3: бюджетная линия ----------

def intercepts(income, p1, p2):
    """Крайние точки бюджетной линии: (всё на пирожные, всё на кофе)."""
    return income / p1, income / p2


I, P1, P2 = 8000, 100, 50
assert intercepts(I, P1, P2) == (80, 160)
assert intercepts(10000, P1, P2) == (100, 200)       # доход вырос — сдвиг вправо
assert intercepts(I, 150, P2) == (8000 / 150, 160)   # пирожные дороже — поворот
assert intercepts(I, P1, 40) == (80, 200)            # кофе дешевле — поворот


def optimum(income, p1, p2):
    """Оптимум для U = Q1·Q2: на каждое благо уходит половина дохода."""
    return income / (2 * p1), income / (2 * p2)


q1, q2 = optimum(I, P1, P2)
assert (q1, q2) == (40, 80)
assert P1 * q1 + P2 * q2 == I                    # точка D лежит на бюджетной линии
assert q2 / P1 == q1 / P2 == 0.8                 # MU1/P1 = MU2/P2 (MU1 = Q2, MU2 = Q1)


# ---------- Эффект дохода и замещения (Слуцкий), P1: 100 → 150 ----------

P1_new = 150
a1, a2 = optimum(I, P1_new, P2)                  # новый оптимум
comp_income = P1_new * q1 + P2 * q2              # столько стоит старый набор по новым ценам
assert comp_income == 10000
c1, c2 = optimum(comp_income, P1_new, P2)        # компенсированный набор
sub1, inc1 = c1 - q1, a1 - c1
sub2, inc2 = c2 - q2, a2 - c2
assert round(sub1 + inc1, 9) == round(a1 - q1, 9)
assert (round(a2), round(c2), round(sub2), round(inc2)) == (80, 100, 20, -20)
real_income_drop = 1 - I / comp_income
assert round(real_income_drop, 9) == 0.2


# ---------- Эффект Гиффена: доширак и котлета ----------

def giffen(price_noodles, price_cutlet=150, budget=1600, meals=20):
    """Ровно meals приёмов пищи на budget ₽: x доширака + y котлет."""
    x = (price_cutlet * meals - budget) / (price_cutlet - price_noodles)
    return x, meals - x


x0, y0 = giffen(50)
x1, y1 = giffen(60)
assert (x0, y0) == (14, 6)
assert x1 > x0  # доширак подорожал, а его покупают больше — товар Гиффена
assert 26 * P1_new + q2 * P2 <= I < 27 * P1_new + q2 * P2  # совет: 26 пирожных, не 27


# ---------- Этап 4: рыночный спрос ----------

BUYERS = {"Аня": (50, 6), "Борис": (80, 4), "Вера": (100, 5),
          "Гриша": (120, 3), "Дина": (150, 2), "Елена": (200, 1)}


def market(price, buyers):
    """Покупает каждый, у кого цена спроса не ниже рыночной цены."""
    return sum(q for p, q in buyers.values() if p >= price)


PRICES = [50, 80, 100, 120, 150, 200]
demand = [market(p, BUYERS) for p in PRICES]
assert demand == [21, 15, 11, 6, 3, 1]
BUYERS_NEW = BUYERS | {"Новый": (90, 3)}
demand_new = [market(p, BUYERS_NEW) for p in [50, 80, 90, 100, 120, 150, 200]]
assert demand_new == [24, 18, 14, 11, 6, 3, 1]
assert market(90, BUYERS) == 11  # при 90 ₽ до прихода нового студента


# ---------- Графики (ручной SVG без зависимостей) ----------

W, H, L, B, R, T = 520, 300, 50, 40, 20, 20  # размер и поля области графика
COLORS = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e"]


def svg(name, xmax, ymin, ymax, series, xlabel, ylabel, xticks, yticks, notes=(), legend_y=T + 6):
    """series: [(подпись, [(x, y), …], цвет, пунктир?)], notes: [(x, y, текст)]."""
    def sx(x):
        return L + (x / xmax) * (W - L - R)

    def sy(y):
        return H - B - (y - ymin) / (ymax - ymin) * (H - B - T)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'font-family="sans-serif" font-size="11">',
           f'<rect width="{W}" height="{H}" fill="white"/>']
    for x in xticks:  # сетка и подписи осей
        out.append(f'<line x1="{sx(x)}" y1="{T}" x2="{sx(x)}" y2="{H - B}" stroke="#eee"/>')
        out.append(f'<text x="{sx(x)}" y="{H - B + 14}" text-anchor="middle">{x:g}</text>')
    for y in yticks:
        out.append(f'<line x1="{L}" y1="{sy(y)}" x2="{W - R}" y2="{sy(y)}" stroke="#eee"/>')
        out.append(f'<text x="{L - 5}" y="{sy(y) + 4}" text-anchor="end">{y:g}</text>')
    out.append(f'<line x1="{L}" y1="{sy(max(ymin, 0))}" x2="{W - R}" y2="{sy(max(ymin, 0))}" stroke="black"/>')
    out.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{H - B}" stroke="black"/>')
    out.append(f'<text x="{(L + W - R) / 2}" y="{H - 6}" text-anchor="middle">{xlabel}</text>')
    out.append(f'<text x="12" y="{(T + H - B) / 2}" text-anchor="middle" '
               f'transform="rotate(-90 12 {(T + H - B) / 2})">{ylabel}</text>')
    for i, (label, pts, color, dashed) in enumerate(series):
        path = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in pts)
        dash = ' stroke-dasharray="5,4"' if dashed else ""
        out.append(f'<polyline points="{path}" fill="none" stroke="{color}" stroke-width="2"{dash}/>')
        ly = legend_y + 15 * i  # легенда справа (по умолчанию сверху)
        out.append(f'<line x1="{W - R - 175}" y1="{ly}" x2="{W - R - 155}" y2="{ly}" '
                   f'stroke="{color}" stroke-width="2"{dash}/>')
        out.append(f'<text x="{W - R - 150}" y="{ly + 4}">{label}</text>')
    for x, y, text in notes:
        out.append(f'<circle cx="{sx(x)}" cy="{sy(y)}" r="3.5"/>')
        out.append(f'<text x="{sx(x) + 6}" y="{sy(y) - 6}">{text}</text>')
    out.append("</svg>")
    (IMG / name).write_text("\n".join(out) + "\n", encoding="utf-8")


def stairs(points):
    """Ступенчатая кривая спроса: при цене p покупают q (от высокой цены к низкой)."""
    pts = []
    for (p, q), (p_next, _) in zip(points, points[1:] + [(0, 0)]):
        pts += [(q, p), (q, p_next)] if p_next else [(q, p)]
    return [(0, points[0][0])] + pts


def draw():
    IMG.mkdir(exist_ok=True)
    q = list(range(len(TU)))
    svg("utility.svg", 7, -4, 32,
        [("TU — общая", list(zip(q, TU)), COLORS[0], False),
         ("MU — предельная", list(zip(q[1:], MU)), COLORS[1], False)],
        "Q, пирожные", "ютили", q, [-4, 0, 10, 20, 30],
        [(5, 30, "насыщение"), (6, 0, "MU = 0")], legend_y=130)

    xs = [x / 2 for x in range(0, 201)]
    curve = [(x, 3200 / x) for x in xs if x >= 16 and 3200 / x <= 200]  # U = Q1·Q2 = 3200
    svg("budget.svg", 100, 0, 200,
        [("I=8000, P₁=100, P₂=50", [(0, 160), (80, 0)], COLORS[0], False),
         ("I=10000", [(0, 200), (100, 0)], COLORS[2], True),
         ("P₁=150", [(0, 160), (8000 / 150, 0)], COLORS[1], True),
         ("P₂=40", [(0, 200), (80, 0)], COLORS[3], True),
         ("кривая безразличия U=3200", curve, COLORS[4], False)],
        "Q₁, пирожные", "Q₂, кофе", [0, 20, 40, 53.3, 80, 100], [0, 40, 80, 120, 160, 200],
        [(40, 80, "D (40; 80)")])

    old = sorted(((p, d) for p, d in zip(PRICES, demand)), reverse=True)
    new = sorted(zip([50, 80, 90, 100, 120, 150, 200], demand_new), reverse=True)
    svg("demand.svg", 26, 0, 220,
        [("рыночный спрос", stairs(old), COLORS[0], False),
         ("+ студент (90 ₽, 3 шт.)", stairs(new), COLORS[1], True)],
        "Q, пирожные, шт.", "P, ₽", [0, 1, 3, 6, 11, 15, 21, 24], [0, 50, 80, 100, 120, 150, 200])


if __name__ == "__main__":
    print("Этап 2. MU:", MU)
    print("Этап 3. Оптимум D:", (q1, q2), "MU/P =", q2 / P1)
    print(f"Слуцкий, пирожные: замещение {sub1:+.2f}, доход {inc1:+.2f}, итог {a1 - q1:+.2f}")
    print(f"Слуцкий, кофе:     замещение {sub2:+.2f}, доход {inc2:+.2f}, итог {a2 - q2:+.2f}")
    print(f"Реальный доход упал на {real_income_drop:.0%}")
    print(f"Гиффен: доширак {x0:g} → {x1:.1f} шт., котлеты {y0:g} → {y1:.1f} шт.")
    print("Этап 4. Рыночный спрос:", dict(zip(PRICES, demand)))
    print("С новым студентом:", dict(zip([50, 80, 90, 100, 120, 150, 200], demand_new)))
    draw()
    print("Графики: img/utility.svg, img/budget.svg, img/demand.svg")
