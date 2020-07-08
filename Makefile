# define version:
GLOTTOLOG=v4.2.1
CONCEPTICON=v2.3.0

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
