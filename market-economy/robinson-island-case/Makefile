# Сборка PDF решения кейса: make → solution.pdf
solution.pdf: solution.typ
	typst compile $< $@

clean:
	rm -f solution.pdf

.PHONY: clean
