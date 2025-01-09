m4opt.pdf: m4opt.tex m4opt.bib figures/fov.pdf figures/piecewise-linear-exptime.pdf figures/skygrid.png figures/etc.pdf
	latexmk -pdf m4opt.tex

m4opt.bib: m4opt.tex
	adstex $<

figures/fov.pdf: scripts/fov.py scripts/plots.py
	python scripts/fov.py

figures/piecewise-linear-exptime.pdf: scripts/piecewise-linear-exptime.py scripts/plots.py
	python scripts/piecewise-linear-exptime.py

figures/skygrid.png: scripts/skygrid.py scripts/plots.py
	python scripts/skygrid.py

figures/etc.pdf: scripts/etc.py scripts/plots.py
	python scripts/etc.py
