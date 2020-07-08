# define version:
GLOTTOLOG=v4.1
CONCEPTICON=v2.2.0

help:
	@echo "1. Run 'make install' to install the python requirements"
	@echo "2. Run 'make cldf' to generate a CLDF dataset"

# install python venv and install python libraries
env:
	python -m venv env
	./env/bin/python ./env/bin/pip3 install -r requirements.txt
	./env/bin/cldfbench catconfig

# Install kinbank into venv
install: env
	cd kinbank && ../env/bin/python setup.py develop && cd ..
	
# generate CLDF
cldf: env ./kinbank/raw/
	./env/bin/python ./env/bin/cldfbench lexibank.makecldf --glottolog-version $(GLOTTOLOG) --concepticon-version $(CONCEPTICON) kinbank

test: env
	cd kinbank && pytest
