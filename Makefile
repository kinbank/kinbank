# define version:
GLOTTOLOG=v4.2.1
CONCEPTICON=v2.3.0

# old repositories:
#PARABANK_REPO=https://github.com/parabank/parabank-kinship-data
#VARIKIN_REPO=https://github.com/SamPassmore/varikin-kinbank

.PHONY: help clean update test

help:
	@echo "1. Run 'make install' to install the python requirements"
	@echo "2. Run 'make update' to update to latest versions of Glottolog, Concepticon, and CLDF libraries."
	@echo "3. Run 'make cldf' to generate a CLDF dataset"

# install python venv and install python libraries
env:
	python -m venv env
	./env/bin/python ./env/bin/pip3 install -r requirements.txt
	./env/bin/cldfbench catconfig

update: env
	./env/bin/python ./env/bin/pip3 install --upgrade -r requirements.txt
	./env/bin/cldfbench catupdate

# Install kinbank into venv
install: env
	cd kinbank && ../env/bin/python setup.py develop && cd ..


# generate CLDF
cldf: env ./kinbank/raw/
	./env/bin/python ./env/bin/cldfbench lexibank.makecldf --glottolog-version $(GLOTTOLOG) --concepticon-version $(CONCEPTICON) kinbank

test: env
	cd kinbank && pytest
