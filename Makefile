# define version:
GLOTTOLOG=v4.2.1
CONCEPTICON=v2.3.0

# define repositories:
PARABANK_REPO=https://github.com/parabank/parabank-kinship-data
VARIKIN_REPO=https://github.com/SamPassmore/varikin-kinbank

VARIKIN=raw/varikin
PARABANK=raw/parabank

.PHONY: help clean update test

help:
	@echo "1. Run 'make install' to install the python requirements"
# 	@echo "2. Run 'make data' to clone and update the datasets"
# 	@echo "3. Run 'make merge' to merge the datasets"
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


# install data from kinbank
$(VARIKIN):
	mkdir -p raw
	git clone $(VARIKIN_REPO) $@

# install data from parabank
$(PARABANK):
	mkdir -p raw
	git clone $(PARABANK_REPO) $@

# Install kinbank into venv
install: env
	cd kinbank && ../env/bin/python setup.py develop && cd ..

# # Clone and Update the data
# data: $(VARIKIN) $(PARABANK)
# 	cd $(VARIKIN) && git pull
# 	cd $(PARABANK) && git pull

# #  merge datasets into kinbank
# merge: env
# 	@rm -rf ./kinbank/raw/  # remove any preexisiting stuff in raw
# 	@mkdir -p ./kinbank/raw
# 	./env/bin/python ./import.py

# generate CLDF
cldf: env ./kinbank/raw/
	./env/bin/python ./env/bin/cldfbench lexibank.makecldf --glottolog-version $(GLOTTOLOG) --concepticon-version $(CONCEPTICON) kinbank


test: env
	cd kinbank && pytest
