# define version:
GLOTTOLOG=v4.4
CONCEPTICON=v2.5.0

# Repositories:
PARABANK_REPO=https://github.com/kinbank/parabank
VARIKIN_REPO=https://github.com/kinbank/varikin
KINURA_REPO=https://github.com/kinbank/kinura
GOELDI_REPO=https://github.com/kinbank/goeldi

.PHONY: help clean update test

help:
	@echo "1. Run 'make install' to install the python requirements"
	@echo "2. Run 'make update' to update to latest versions of Glottolog, Concepticon, and CLDF libraries."
	@echo "3. Run 'make merge' to download the separate kinbank datasets and merge them into one."
	@echo "4. Run 'make cldf' to generate a CLDF dataset"

# install python venv and install python libraries
env:
	python -m venv env
	./env/bin/python ./env/bin/pip3 install -r requirements.txt
	./env/bin/cldfbench catconfig

update: env
	./env/bin/python ./env/bin/pip3 install --upgrade -r requirements.txt
	./env/bin/cldfbench catupdate

# Install kinbank into venv and download all collections
install: env
	cd kinbank && ../env/bin/python setup.py develop && cd ..

# bring in all raw files from other databases and copy into own folder
merge: env
	# empty old raw folder
	rm -rf ./kinbank/raw
	# get raw data
	mkdir -p collections
	cd collections/ && git clone $(PARABANK_REPO)
	cd collections/ && git clone $(VARIKIN_REPO)
	cd collections/ && git clone $(KINURA_REPO)
	cd collections/ && git clone $(GOELDI_REPO)
	python merge_collections.py
	rm -rf collections
	cp ./kinbank/etc/sources.bib ./kinbank/cldf/sources.bib
	cp ./kinbank/etc/languages.csv ./kinbank/cldf/languages.csv
	cp ./kinbank/etc/sources.bib ./kinbank/cldf/sources.bib

# generate CLDF
cldf: env ./kinbank/raw/
	./env/bin/python ./env/bin/cldfbench lexibank.makecldf --glottolog-version $(GLOTTOLOG) --concepticon-version $(CONCEPTICON) kinbank

test: env
	cd kinbank && pytest
