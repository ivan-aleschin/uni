# Сборка PDF из документов проекта: make → 01-order.pdf, 02-…pdf, 03-…pdf
DOCS := $(wildcard 0*.md)
PDFS := $(DOCS:.md=.pdf)

all: $(PDFS)

%.pdf: %.md ../pdf.yaml
	pandoc $< -o $@ --pdf-engine=typst --metadata-file=../pdf.yaml --columns=1000

clean:
	rm -f $(PDFS)

.PHONY: all clean
