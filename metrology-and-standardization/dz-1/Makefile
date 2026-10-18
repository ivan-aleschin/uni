# Сборка PDF отчёта: make → report.pdf
# pandoc превращает десятичную запятую в формулах в «0 \, 5» (с пробелом),
# поэтому сначала получаем .typ и склеиваем такие числа обратно в "0,5".
report.pdf: report.md
	pandoc $< -s -t typst -V papersize=a4 -V fontsize=12pt -V lang=ru -V mainfont="Libertinus Serif" -V margin.x=2cm -V margin.y=2cm --columns=1000 \
		| sed -E 's/([0-9]+) \\, ([0-9]+)/"\1,\2"/g' > report.typ
	typst compile report.typ $@
	rm -f report.typ

clean:
	rm -f report.pdf report.typ

.PHONY: clean
