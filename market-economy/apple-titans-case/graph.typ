#set document(title: "Продажи устройств Apple по годам")
#set page(paper: "a5", margin: 10mm)
#set text(lang: "ru", font: "DejaVu Sans", size: 9pt, fill: rgb("#172c35"))
#set par(leading: 0.55em)

#let rows = csv("sales.csv").slice(1).map(row => row.map(int))
#let years = rows.map(row => row.first())
#let total = rows.map(row => row.slice(1).sum() / 1000)
#let ink = rgb("#172c35")
#let muted = rgb("#45616b")
#let grid-color = rgb("#d9e3e5")
#let accent = rgb("#14665f")

#let segment(a, b, stroke) = place(top + left, line(start: a, end: b, stroke: stroke))

#let label(body, (x, y), size: 8pt, fill: muted, weight: "regular") = {
  place(top + left, dx: x, dy: y, text(body, size: size, fill: fill, weight: weight))
}

#let series(points, width, radius) = {
  for (a, b) in points.zip(points.slice(1)) {
    segment(a, b, width + accent)
  }
  for (x, y) in points {
    place(top + left, dx: x - radius, dy: y - radius, circle(radius: radius, fill: accent))
  }
}

#text(size: 19pt, weight: "bold")[Продажи устройств Apple]

#text(fill: muted)[Мировые продажи Mac, iPod, iPhone и iPad · 1996–2010]

#let x(year) = 34pt + (year - years.first()) / (years.last() - years.first()) * 288pt
#let y(value) = 192pt - value / 125 * 169pt
#let points = years.zip(total).map(((year, value)) => (x(year), y(value)))

#box(width: 100%, height: 223pt)[
  #label([$Q$, млн устройств за год], (0pt, 4pt), weight: "bold")

  #for tick in (0, 30, 60, 90, 120) {
    segment((x(1996), y(tick)), (x(years.last()), y(tick)), 0.5pt + grid-color)
    label(str(tick), (9pt, y(tick) - 5pt))
  }
  #segment((x(1996), y(125)), (x(1996), y(0)), 0.75pt + ink)
  #segment((x(1996), y(0)), (x(years.last()), y(0)), 0.75pt + ink)

  #for year in (1996, 2000, 2004, 2007, years.last()) {
    segment((x(year), y(0)), (x(year), y(0) + 4pt), 0.65pt + ink)
    label(str(year), (x(year) - 10pt, y(0) + 7pt))
  }

  #series(points, 1.6pt, 1.7pt)
  #for (year, offset) in ((2007, -18pt), (years.last(), 5pt)) {
    let value = total.at(year - years.first())
    label(str(calc.round(value)), (x(year) + offset, y(value) - 9pt), fill: accent, weight: "bold")
  }
  #label([$t$, финансовый год], (255pt, 211pt), weight: "bold")

  // Та же кривая в меньшем диапазоне по вертикали.
  #place(top + left, dx: 49pt, dy: 36pt, box(
    width: 154pt,
    height: 89pt,
    radius: 3pt,
    fill: rgb("#f5f8f9"),
    stroke: 0.5pt + grid-color,
  )[
    #label([1996–2004 · крупнее], (9pt, 8pt), weight: "bold")
    #let early-x(year) = 24pt + (year - 1996) * 14pt
    #let early-y(value) = 68pt - value * 5.1pt
    #let early-points = years.zip(total).slice(0, 9).map(((year, value)) => {
      (early-x(year), early-y(value))
    })
    #for tick in (0, 4, 8) {
      segment((early-x(1996), early-y(tick)), (early-x(2004), early-y(tick)), 0.5pt + grid-color)
      label(str(tick), (11pt, early-y(tick) - 4pt), size: 7pt)
    }
    #series(early-points, 0.9pt, 1.1pt)
    #for year in (1996, 1998, 2001, 2004) {
      label(str(year), (early-x(year) - 9pt, 73pt), size: 7pt)
    }
  ])
]

#v(4pt)
#text(size: 11pt, weight: "bold")[Ключевые события]
#v(2pt)

#table(
  columns: (73pt, 1fr),
  inset: (x: 5pt, y: 3pt),
  stroke: (x: none, y: 0.5pt + grid-color),
  [*1976–1980*], [Первые заказы на Apple I. Готовый Apple II расширил рынок. IPO дало доступ к капиталу на бирже.],
  [*1983–1985*], [Высокая цена Lisa и нехватка приложений для Macintosh ограничили продажи. Джобс ушёл после конфликта со Скалли.],
  [*1985–1997*], [Джобс развивал NeXT и Pixar. На фоне конкуренции Windows Apple купила NeXT ради новой ОС.],
  [*1997–1999*], [Apple сократила ассортимент. Продажи Mac упали до 2,8 млн в 1998-м и восстановились до 3,4 млн в 1999-м после выхода iMac.],
  [*2001–2005*], [iPod, совместимость с Windows и магазин iTunes расширили рынок цифровой музыки.],
  [*2007–2011*], [iPhone и iPad ускорили рост продаж. В июне 2011-го Apple анонсировала iCloud для синхронизации устройств.],
)

#v(3pt)
#text(size: 7.5pt, fill: muted)[По фильму CNBC «Титаны. Стив Джобс» и отчётам Apple (10-K). График охватывает завершённые к июню 2011 года финансовые годы.]
