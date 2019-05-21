.PHONY: taktiktraining.pdf

taktiktraining.pdf: taktiktraining.tex packages.latex
	latexmk -pvc -pdf -xelatex taktiktraining.tex
