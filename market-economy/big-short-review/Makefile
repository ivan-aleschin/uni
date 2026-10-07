# Сборка PDF рецензии: make → review.pdf
review.pdf: review.md
	pandoc $< -o $@ --pdf-engine=typst -V papersize=a4 -V fontsize=12pt -V lang=ru -V mainfont="Libertinus Serif" -V margin.x=2cm -V margin.y=2cm --columns=1000

clean:
	rm -f review.pdf

.PHONY: clean
