.PHONY: taktiktraining.pdf clean

clean:
	$(RM) *.aux *.dvi *.fdb_latexmk *.fls *.idx *.ilg *.ind *.log *.out *.toc *.xdv

taktiktraining.pdf: taktiktraining.tex packages.latex
	latexmk -pvc -pdf -xelatex taktiktraining.tex
