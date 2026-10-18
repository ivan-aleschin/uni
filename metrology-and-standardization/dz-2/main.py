"""
ДЗ-2. Анализ точных сопряжений. Вариант 1-А (схема А).

d1 = 3,6h6; d2 = 4js8; d3 = 4 L5-js5; d4 = 4,5 E9-m5; d5 = 4,5 H6-m5;
L = 46, l1 = 6, l2 = 22, l3 = 38 (мм).

Скрипт считает все посадки по порядку из УМП (п. 2.4) и рисует картинки
для отчёта: эскиз узла, схемы полей допусков и эскиз вала (SVG).
Отклонения - в мкм, размеры на эскизах - в мм.
"""

import math
from pathlib import Path

HERE = Path(__file__).parent

# Табл. 2.3 и 2.5 УМП, интервал св. 3 до 6 мм
IT = {5: 5, 6: 8, 8: 18, 9: 30}
IT12 = {6: 120, 22: 210, 38: 250, 46: 250}   # св.3-6, 18-30, 30-50 мм
L5_EI = -5                                   # табл. 2.7, d = 4 мм, класс 5

RZ_RA = [(0.05, 0.01), (0.1, 0.02), (0.2, 0.04), (0.4, 0.08), (0.8, 0.16),
         (1.6, 0.32), (3.2, 0.63), (6.3, 1.25), (10, 2.5), (20, 5), (40, 10)]
FORM = [0.1, 0.12, 0.16, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.2, 1.6, 2.0]


def laplace(z):
    """Интегральная функция Ф(z) (табл. 2.9)."""
    return 0.5 * math.erf(z / math.sqrt(2))


def pick_le(values, limit):
    """Наибольшее предпочтительное значение, не превышающее limit."""
    return max(v for v in values if v <= limit + 1e-9)


def rz_ra(*limits):
    rz = pick_le([p[0] for p in RZ_RA], min(limits))
    return rz, dict(RZ_RA)[rz]


def fit(name, hole, shaft):
    es_h, ei_h = hole        # ES, EI
    es_s, ei_s = shaft       # es, ei
    td_h = es_h - ei_h
    td_s = es_s - ei_s
    smax = es_h - ei_s
    smin = ei_h - es_s
    sm = (smax + smin) / 2
    ts = smax - smin
    tsp = math.sqrt(td_h ** 2 + td_s ** 2)
    half = round(tsp / 2, 1)
    r = dict(name=name, ES=es_h, EI=ei_h, es=es_s, ei=ei_s, TD=td_h, Td=td_s,
             Smax=smax, Smin=smin, Sm=sm, TS=ts, TSp=tsp, half=half,
             Spmax=sm + half, Spmin=sm - half)
    if smin < 0 < smax:
        z = 6 * abs(sm) / tsp
        f = round(laplace(round(z, 2)), 5)   # как по табл. 2.9
        big, small = 0.5 + f, 0.5 - f
        r.update(z=z, F=f,
                 PS=big if sm > 0 else small,
                 PN=small if sm > 0 else big)
    return r


def calc():
    fits = {
        "d3": fit("∅4 L5-js5", (0, L5_EI), (IT[5] / 2, -IT[5] / 2)),
        "d4": fit("∅4,5 E9-m5", (20 + IT[9], 20), (4 + IT[5], 4)),
        "d5": fit("∅4,5 H6-m5", (IT[6], 0), (4 + IT[5], 4)),
    }
    # круглость цапфы под ПК класса 5: T0 <= Td/8
    t0 = pick_le(FORM, fits["d3"]["Td"] / 8)
    rough = {
        "d1": rz_ra(0.3 * IT[6]),
        "d2": rz_ra(0.3 * IT[8]),
        "d3": rz_ra(0.3 * IT[5], 0.4 * t0),
        "m5": rz_ra(0.3 * IT[5]),
        "E9": rz_ra(0.3 * IT[9]),
        "H6": rz_ra(0.3 * IT[6]),
    }
    return fits, t0, rough


def report(fits, t0, rough):
    print("Точные размеры вала:")
    print(f"  d1 ∅3,6h6: es = 0, ei = -{IT[6]}, Td = {IT[6]} мкм")
    print(f"  d2 ∅4js8: es = +{IT[8] / 2:g}, ei = -{IT[8] / 2:g}, Td = {IT[8]} мкм")
    for key, f in fits.items():
        print(f"{key} {f['name']}:")
        print(f"  отверстие ES = {f['ES']:+g}, EI = {f['EI']:+g}, TD = {f['TD']:g}")
        print(f"  вал       es = {f['es']:+g}, ei = {f['ei']:+g}, Td = {f['Td']:g}")
        print(f"  Smax = {f['Smax']:+g}, Smin = {f['Smin']:+g}, Sm = {f['Sm']:+g}, "
              f"TS = {f['TS']:g}")
        print(f"  TSp = {f['TSp']:.3f}, 0,5TSp = {f['TSp'] / 2:.3f} ≈ {f['half']}, "
              f"Spmax = {f['Spmax']:+.1f}, Spmin = {f['Spmin']:+.1f}")
        if "z" in f:
            print(f"  z = {f['z']:.3f}, Ф(z) = {f['F']:.5f}, "
                  f"PS = {f['PS']:.5f}, PN = {f['PN']:.5f}")
    print(f"Круглость цапфы d3: Td/8 = {fits['d3']['Td'] / 8} -> T0 = {t0} мкм")
    for k, (rz, ra) in rough.items():
        print(f"  шероховатость {k}: Rz = {rz}, Ra = {ra} мкм")
    print("Свободные размеры (12-й квалитет):")
    for size, it in IT12.items():
        if size == 46:   # габарит вала - как размер вала h12
            print(f"  {size} мм: IT12 = {it} мкм, h12: 0 / −{it / 1000:.2f} мм")
        else:
            print(f"  {size} мм: IT12 = {it} мкм, ±{it / 2000:.3f} мм")


# ---------------- картинки ----------------

def sign(v):
    """Отклонение со знаком и десятичной запятой: +2,5 / −5 / 0."""
    if v == 0:
        return "0"
    return f"{v:+g}".replace("-", "−").replace(".", ",")


def svg(width, height, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}mm" '
            f'height="{height}mm" viewBox="0 0 {width} {height}" '
            f'font-family="Libertinus Serif, serif">\n{body}\n</svg>\n')


def text(x, y, s, size=3.6, anchor="middle", italic=False, rotate=None):
    style = ' font-style="italic"' if italic else ""
    rot = f' transform="rotate({rotate} {x} {y})"' if rotate else ""
    return (f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" '
            f'text-anchor="{anchor}"{style}{rot}>{s}</text>')


def line(x1, y1, x2, y2, w=0.3, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="black" stroke-width="{w}"{d}/>')


def rect(x, y, w, h, sw=0.4, fill="none"):
    return (f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
            f'fill="{fill}" stroke="black" stroke-width="{sw}"/>')


def arrow_dim(x1, x2, y, label, size=3.0):
    """Горизонтальный размер со стрелками и подписью над линией."""
    a = 1.4
    body = [line(x1, y, x2, y, 0.25),
            f'<path d="M{x1},{y} l{a},{-a / 3} v{2 * a / 3} z" fill="black"/>',
            f'<path d="M{x2},{y} l{-a},{-a / 3} v{2 * a / 3} z" fill="black"/>',
            text((x1 + x2) / 2, y - 0.8, label, 3.6)]
    return "\n".join(body)


HATCH = ('<defs><pattern id="h" width="1.6" height="1.6" '
         'patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         '<line x1="0" y1="0" x2="0" y2="1.6" stroke="black" stroke-width="0.25"/>'
         '</pattern></defs>')

K = 3.0          # масштаб 3:1
# профиль вала: (x от, x до, диаметр), мм
SHAFT = [(0, 6, 3.6), (6, 22, 4.0), (22, 38, 4.5), (38, 46, 4.0)]


def shaft_outline(x0, yc, k=K):
    parts = []
    for a, b, d in SHAFT:
        r = d / 2 * k
        parts.append(rect(x0 + a * k, yc - r, (b - a) * k, 2 * r, 0.45))
    # шпоночные пазы: на хвостовике и под ступицей колеса
    parts.append(rect(x0 + 1 * k, yc - 0.5 * k, 4 * k, 1.0 * k, 0.25))
    parts.append(rect(x0 + 28.5 * k, yc - 0.5 * k, 8 * k, 1.0 * k, 0.25))
    parts.append(line(x0 - 4, yc, x0 + 46 * k + 4, yc, 0.2, "4 1 1 1"))
    return parts


def bearing(x0, yc, a, b, k=K, d=4.0, dd=13.0):
    """Упрощённое изображение подшипника: прямоугольник с диагоналями."""
    out = []
    for sgn in (-1, 1):
        y1 = yc + sgn * d / 2 * k
        y2 = yc + sgn * dd / 2 * k
        top, bot = min(y1, y2), max(y1, y2)
        out.append(rect(x0 + a * k, top, (b - a) * k, bot - top, 0.45))
        out.append(line(x0 + a * k, top, x0 + b * k, bot, 0.3))
        out.append(line(x0 + a * k, bot, x0 + b * k, top, 0.3))
    return out


def hatched_ring(x0, yc, a, b, r_in, r_out, k=K):
    out = []
    for sgn in (-1, 1):
        y1, y2 = yc + sgn * r_in * k, yc + sgn * r_out * k
        top, bot = min(y1, y2), max(y1, y2)
        out.append(rect(x0 + a * k, top, (b - a) * k, bot - top, 0.45, "url(#h)"))
    return out


def leader(x, y_from, y_to, label):
    return "\n".join([line(x, y_from, x, y_to, 0.25),
                      text(x, y_to - 1.0, label, 3.6)])


def rough_sign(x, y, label, size=3.0):
    """Знак шероховатости √ с полкой; (x, y) - вершина знака."""
    return "\n".join([
        f'<path d="M{x - 1.6},{y - 2.6} L{x},{y} L{x + 3},{y - 5.2} L{x + 13},{y - 5.2}" '
        f'fill="none" stroke="black" stroke-width="0.25"/>',
        text(x + 3.4, y - 5.9, label, size, "start")])


def dia_dim(x, yc, d, y_text, main, up=None, low=None, k=K):
    """Диаметр: размерная линия со стрелками, выноска вверх и надпись.
    Отклонения up/low пишутся друг над другом в скобках."""
    r = d / 2 * k
    a = 1.2
    out = [line(x, yc - r, x, y_text + 1.2, 0.25),
           f'<path d="M{x},{yc - r} l-0.45,{-a} h0.9 z" fill="black"/>',
           line(x, yc - r, x, yc + r, 0.25),
           f'<path d="M{x},{yc + r} l-0.45,{a} h0.9 z" fill="black"/>']
    if up is None:
        out.append(text(x, y_text, main, 3.6))
        return out
    w = 0.55 * 2.6 * max(len(up), len(low))
    left = x - (0.55 * 3.6 * len(main) + w) / 2
    tx = left + 0.55 * 3.6 * len(main)
    out += [text(tx, y_text, main + "(", 3.6, "end"),
            text(tx + 0.2, y_text - 1.6, up, 2.6, "start"),
            text(tx + 0.2, y_text + 1.2, low, 2.6, "start"),
            text(tx + 0.4 + w, y_text, ")", 3.6, "start")]
    return out


def draw_unit():
    x0, yc = 12, 52
    body = [HATCH]
    body += shaft_outline(x0, yc)
    body += bearing(x0, yc, 17, 22)
    body += bearing(x0, yc, 38, 43)
    body += hatched_ring(x0, yc, 22, 27, 2.25, 3.6)          # распорная втулка
    body += hatched_ring(x0, yc, 27, 38, 2.25, 4.2)          # ступица колеса
    body += hatched_ring(x0, yc, 33, 38, 4.2, 10.0)          # венец колеса
    # обозначения посадок (выноски вверх)
    labels = [(3, "∅3,6h6"), (12, "∅4js8"), (19.5, "∅4 L5/js5"),
              (24.5, "∅4,5 E9/m5"), (30, "∅4,5 H6/m5"), (40.5, "∅4 L5/js5")]
    tops = [20, 20, 12, 20, 6, 12]
    for (x, s), ty in zip(labels, tops):
        body.append(leader(x0 + x * K, yc - 2.5, ty + 2, s))
    body.append(line(x0, yc + 7, x0, yc + 36, 0.2))
    body.append(line(x0 + 46 * K, yc + 7, x0 + 46 * K, yc + 36, 0.2))
    body.append(arrow_dim(x0, x0 + 46 * K, yc + 34, "46"))
    body.append(text(x0 + 46 * K - 2, yc + 44, "М 3:1", 3.6, "end"))
    return svg(165, 100, "\n".join(body))


def draw_shaft(t0, rough):
    x0, yc = 12, 60
    body = [HATCH]
    body += shaft_outline(x0, yc)
    k = K
    body.append(line(x0 + 17 * k, yc - 2 * k, x0 + 17 * k, yc + 2 * k, 0.2))
    # диаметры
    body += dia_dim(x0 + 3 * k, yc, 3.6, 34, "∅3,6h6", "0", "−0,008")
    body += dia_dim(x0 + 12 * k, yc, 4.0, 42, "∅4js8(±0,009)")
    body += dia_dim(x0 + 19.5 * k, yc, 4.0, 30, "∅4js5(±0,0025)")
    body += dia_dim(x0 + 30 * k, yc, 4.5, 34, "∅4,5m5", "+0,009", "+0,004")
    body += dia_dim(x0 + 42 * k, yc, 4.0, 30, "∅4js5(±0,0025)")
    # допуск круглости на цапфах под подшипники
    for x in (19.5, 42):
        bx, by = x0 + x * k - 9, 17
        body.append(rect(bx, by, 6, 5, 0.3))
        body.append(f'<circle cx="{bx + 3}" cy="{by + 2.5}" r="1.6" fill="none" '
                    f'stroke="black" stroke-width="0.3"/>')
        body.append(rect(bx + 6, by, 12, 5, 0.3))
        body.append(text(bx + 12, by + 3.7, f"{t0 / 1000:.4f}".replace(".", ","), 2.8))
        body.append(line(bx + 9, by + 5, bx + 9, 25, 0.2))
    # шероховатость на образующих
    ra = [(0.8, rough["d1"][1]), (9, rough["d2"][1]), (17.1, rough["d3"][1]),
          (26, rough["m5"][1]), (43.2, rough["d3"][1])]
    for x, v in ra:
        cx = x0 + x * k
        yb = yc + 2.25 * k + 1.0
        body.append(f'<path d="M{cx - 2},{yb + 3} L{cx},{yb} L{cx + 1.2},{yb + 2} '
                    f'L{cx + 10},{yb + 2}" fill="none" stroke="black" stroke-width="0.25"/>')
        body.append(text(cx + 1.6, yb + 1.6, f"Ra {v:g}".replace(".", ","), 3.0, "start"))
    # торцы, в которые упираются подшипники: Ra вдвое больше, чем на цапфе
    ra_end = f"Ra {2 * rough['d3'][1]:g}".replace(".", ",")
    for x, dx in ((22, -15), (38, 3)):
        fx, fy = x0 + x * k, yc - 2.25 * k
        body.append(line(fx, fy + 1.5, fx + dx + 1.6, fy - 3.5, 0.2))
        body.append(rough_sign(fx + dx + 1.6, fy - 3.5, ra_end, 2.8))
    # осевые размеры (свободные, 12-й квалитет)
    dims = [(6, "6±0,06", 20), (22, "22±0,105", 28), (38, "38±0,125", 36),
            (46, "46<tspan baseline-shift=\"sub\" font-size=\"2.6\">−0,25</tspan>", 44)]
    body.append(line(x0, yc + 6, x0, yc + 46, 0.2))
    for x, s, dy in dims:
        body.append(line(x0 + x * k, yc + 6, x0 + x * k, yc + dy + 2, 0.2))
        body.append(arrow_dim(x0, x0 + x * k, yc + dy, s))
    body.append(rough_sign(136, 11, "Ra 5", 3.2))
    body.append(text(160, 9, "(√)", 3.2, "end"))
    body.append(text(x0 + 46 * k - 2, yc + 54, "М 3:1", 3.6, "end"))
    return svg(165, 120, "\n".join(body))


def draw_fields(f, title, hole_lbl, shaft_lbl):
    """Схема полей допусков, общий масштаб 1 мкм = 1 мм."""
    lo = min(f["EI"], f["ei"], 0) - 6
    hi = max(f["ES"], f["es"], 0) + 6
    h = hi - lo + 14
    width = 90
    y0 = 7 + hi                   # нулевая линия
    y = lambda v: y0 - v
    body = [line(10, y0, width - 4, y0, 0.4),
            text(6, y0 - 1.5, "+", 3.4), text(6, y0 + 3.5, "−", 3.4),
            text(9, y0 + 1.2, "0", 3.2, "end")]
    hx, sx, bw = 30, 56, 16
    body.append(rect(hx, y(f["ES"]), bw, f["ES"] - f["EI"], 0.5, "url(#h)"))
    body.append(rect(sx, y(f["es"]), bw, f["es"] - f["ei"], 0.5))
    body.append(text(hx + bw / 2, y(f["ES"]) - 1.5, hole_lbl, 3.2, italic=True))
    body.append(text(sx + bw / 2, y(f["es"]) - 1.5, shaft_lbl, 3.2, italic=True))
    for v, x in ((f["ES"], hx - 1), (f["EI"], hx - 1)):
        body.append(text(x, y(v) + 1.2, sign(v), 2.8, "end"))
    for v, x in ((f["es"], sx + bw + 1), (f["ei"], sx + bw + 1)):
        body.append(text(x, y(v) + 1.2, sign(v), 2.8, "start"))
    body.append(text(width / 2, h - 1, title, 3.0))
    return svg(width, h, HATCH + "\n" + "\n".join(body))


def draw_shaft_fields():
    """Поля допусков точных размеров вала d1 и d2 (тот же масштаб)."""
    hi, lo = 14, -14
    h = hi - lo + 14
    y0 = 7 + hi
    y = lambda v: y0 - v
    body = [line(10, y0, 86, y0, 0.4), text(6, y0 - 1.5, "+", 3.4),
            text(6, y0 + 3.5, "−", 3.4), text(9, y0 + 1.2, "0", 3.2, "end")]
    for x, top, bot, lbl in ((26, 0, -8, "h6"), (56, 9, -9, "js8")):
        body.append(rect(x, y(top), 16, top - bot, 0.5))
        body.append(text(x + 8, y(top) - 1.5, lbl, 3.2, italic=True))
        body.append(text(x + 17, y(top) + 1.2, sign(top), 2.8, "start"))
        body.append(text(x + 17, y(bot) + 1.2, sign(bot), 2.8, "start"))
    body.append(text(48, h - 1, "∅3,6h6 и ∅4js8, мкм", 3.0))
    return svg(90, h, "\n".join(body))


def main():
    fits, t0, rough = calc()
    report(fits, t0, rough)
    fig = HERE / "fig"
    fig.mkdir(exist_ok=True)
    (fig / "unit.svg").write_text(draw_unit())
    (fig / "shaft.svg").write_text(draw_shaft(t0, rough))
    (fig / "fields_d1_d2.svg").write_text(draw_shaft_fields())
    (fig / "fields_d3.svg").write_text(draw_fields(fits["d3"], "∅4 L5-js5, мкм", "L5", "js5"))
    (fig / "fields_d4.svg").write_text(draw_fields(fits["d4"], "∅4,5 E9-m5, мкм", "E9", "m5"))
    (fig / "fields_d5.svg").write_text(draw_fields(fits["d5"], "∅4,5 H6-m5, мкм", "H6", "m5"))


if __name__ == "__main__":
    main()
