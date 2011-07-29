#
# Basic makefile for general targets
#
PACKAGE = flaskapi
VERSION = $(shell git describe --tags)
PYTHON_VERSION = py2.6

COVERAGE_ARGS = --with-coverage --cover-package=$(package)
EASY_INSTALL = bin/easy_install
IPYTHON = bin/ipython
NOSE = bin/nosetests
NOSYD = bin/nosyd -1
PIP = bin/pip
PYREVERSE = pyreverse -o png -p
PYTHON = bin/python
PYTHON_DOCTEST = $(PYTHON) -m doctest

## Testing ##
unit-test:
	$(NOSE) tests/unit

coverage:
	-rm -f .coverage
	$(NOSE) --no-color $(COVERAGE_ARGS) tests/unit
	-rm -f .coverage

test: unit-test

tdd:
	$(NOSYD)


## Documentation ##
.PHONY: doc
doc:
	$(PYTHON) setup.py build_sphinx


## Static analysis ##
.PHONY: lint uml metrics
lint:
	bin/pylint --rcfile pylintrc flaskapi


## Local Setup ##
requirements: virtualenv clean-requirements
	$(EASY_INSTALL) -U distribute
	# need ports libevent and libevent1 for mac_dev
	C_INCLUDE_PATH="/opt/local/include:/usr/local/include" $(PIP) install --find-links=https://nebula.ofc.lair/python-dist -r requirements.pip
	-rm README.txt
	# These libs don't work when installed via pip.
	$(EASY_INSTALL) nose_machineout
	$(EASY_INSTALL) readline

virtualenv:
	virtualenv --distribute --no-site-packages --python=python2.6 .

clean-requirements:
	-rm -rf src


## Packaging ##
.PHONY: dist upload
dist: dist/$(PACKAGE)-$(VERSION)-$(PYTHON_VERSION).egg dist/$(PACKAGE)-$(VERSION).tar.gz
dist/$(PACKAGE)-$(VERSION)-$(PYTHON_VERSION).egg dist/$(PACKAGE)-$(VERSION).tar.gz: $(PYTHON_SOURCES)
	$(PYTHON) setup.py sdist

upload: dist
	fab upload_package

deploy-docs: $(PACKAGE)_docs.tar.gz
	fab deploy_docs

$(PACKAGE)_docs.tar.gz: doc
	tar zcf $@ doc/html
