# Сборка PDF отчёта: make → report.pdf
# Шапка и оформление (A4, 12pt, поля 2 см) — в общем шаблоне ../report.typst.
# pandoc превращает десятичную запятую в формулах в «0 \, 5» (с пробелом),
# поэтому сначала получаем .typ и склеиваем такие числа обратно в "0,5".
TEMPLATE := ../report.typst

report.pdf: report.md $(TEMPLATE)
	pandoc $< -f markdown-auto_identifiers -s -t typst --template=$(TEMPLATE) --columns=1000 \
		| sed -E 's/([0-9]+) \\, ([0-9]+)/"\1,\2"/g' > report.typ
	typst compile report.typ $@
	rm -f report.typ

clean:
	rm -f report.pdf report.typ

.PHONY: clean
