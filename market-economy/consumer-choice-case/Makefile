# Сборка PDF решения кейса: make → solution.pdf (графики img/*.svg рисует check.py)
solution.pdf: README.md pdf.yaml $(wildcard img/*.svg)
	pandoc $< -o $@ -f markdown-auto_identifiers --pdf-engine=typst --metadata-file=pdf.yaml --columns=1000

clean:
	rm -f solution.pdf

.PHONY: clean
