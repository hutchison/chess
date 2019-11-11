LATEX = latexmk -pdf -xelatex
LATEX_OPTS = -pvc

.PHONY: clean all

clean:
	$(RM) *.aux *.bbl *.blg *.dvi *.fdb_latexmk *.fls *.idx *.ilg *.ind *.log *.out *.toc *.xdv

all:
	$(LATEX) *.tex

%.pdf: %.tex
	$(LATEX) $(LATEX_OPTS) $<
