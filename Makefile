m4opt.pdf: m4opt.tex m4opt.bib
	latexmk -pdf m4opt.tex

m4opt.bib: m4opt.tex
	adstex $<
