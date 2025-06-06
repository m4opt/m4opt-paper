LATEXDEPS = \
	m4opt.tex \
	m4opt.bib \
	figures/example.pdf \
	figures/area-distance-O5.pdf \
	figures/area-distance-O6.pdf \
	figures/etc.pdf \
	figures/fov.pdf \
	figures/max-weighted-coverage.pdf \
	figures/nominal-roll.pdf \
	figures/overlapping-fields.pdf \
	figures/piecewise-linear-exptime.pdf \
	figures/prob-exptime.pdf \
	figures/skygrid.png \
	figures/slew.pdf \
	figures/uvex-tiling.pdf \
	figures/UVEXrender.png \
	tables/example.tex \
	tables/events.tex \
	tables/selected-detected.tex

ANIMATIONS = \
	and/skygrid.gif \
	and/example.gif

LICENSES = licenses/*.txt

m4opt.pdf: $(LATEXDEPS)
	latexmk -pdf m4opt.tex

# m4opt.bib: m4opt.tex
# 	adstex $<

m4opt-arxiv.zip: $(LATEXDEPS) $(ANIMATIONS) m4opt.bbl $(LICENSES)
	rm -f $@ && zip $@ $^

m4opt-zenodo.zip: $(LATEXDEPS) $(ANIMATIONS) m4opt.bbl m4opt.pdf data/O?/*.fits data/O?/*.ecsv data/events.ecsv $(LICENSES)
	rm -f $@ && zip $@ $^

runs_SNR-10.zip:
	curl -OL https://zenodo.org/records/14585837/files/runs_SNR-10.zip

data/observing-scenarios.ecsv: runs_SNR-10.zip scripts/unpack-observing-scenarios.py
	python scripts/unpack-observing-scenarios.py

figures/fov.pdf: scripts/fov.py scripts/plots.py
	python scripts/fov.py

figures/piecewise-linear-exptime.pdf: scripts/piecewise-linear-exptime.py scripts/plots.py
	python scripts/piecewise-linear-exptime.py

figures/prob-exptime.pdf: scripts/prob-exptime.py scripts/plots.py
	python scripts/prob-exptime.py

figures/skygrid.png: scripts/skygrid.py scripts/plots.py
	python scripts/skygrid.py

figures/etc.pdf: scripts/etc.py scripts/plots.py
	python scripts/etc.py

tables/selected-detected.tex: scripts/selected-detected.py data/events.ecsv
	python scripts/selected-detected.py

data/events.ecsv: scripts/events-ecsv.py
	python scripts/events-ecsv.py

tables/events.tex: scripts/events-tex.py data/events.ecsv
	python scripts/events-tex.py

figures/nominal-roll.pdf: scripts/nominal-roll.py scripts/plots.py
	python scripts/nominal-roll.py

figures/slew.pdf: scripts/slew.py scripts/plots.py
	python scripts/slew.py

tables/example.tex: scripts/plan-table.py data/O5/4678.ecsv
	python scripts/plan-table.py

figures/example.pdf: data/O5/4678.ecsv
	m4opt animate data/O5/4678.ecsv and/example.gif --still figures/example.pdf --dpi 300 --time-step 2.5min --inset-center='35d -31d' --inset-radius=11deg
