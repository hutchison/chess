.PHONY: taktiktraining.pdf konzept.pdf clean

clean:
	$(RM) *.aux *.bbl *.blg *.dvi *.fdb_latexmk *.fls *.idx *.ilg *.ind *.log *.out *.toc *.xdv

taktiktraining.pdf: taktiktraining.tex packages.latex
	latexmk -pvc -pdf -xelatex taktiktraining.tex

konzept.pdf: konzept.tex
	latexmk -pvc -pdf -xelatex konzept.tex

mate_puzzles.pdf: mate_puzzles.tex packages.latex
	latexmk -pvc -pdf -xelatex mate_puzzles.tex
