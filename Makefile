#
# Basic makefile for general targets
#
PACKAGE = @@baseservice@@

COVERAGE_ARGS = --with-coverage --cover-package=$(PACKAGE) --cover-tests
DIST_FILE = dist/$(PACKAGE)-$(VERSION).tar.gz
EASY_INSTALL = bin/easy_install
IPYTHON = bin/ipython
NOSE = bin/nosetests
NOSYD = bin/nosyd -1
PIP = bin/pip
PYREVERSE = pyreverse -o png -p
PYTHON = bin/python
PYTHON_DIST_SITE = nebula.ofc.lair:/var/www/secure/python-dist/
PYTHON_DOCTEST = $(PYTHON) -m doctest
SCP = scp
VERSION = $(shell $(PYTHON) ./version.py)

## Testing ##
.PHONY: test unit-test integration-test system-test acceptance-test tdd coverage
test: unit-test integration-test system-test acceptance-test
unit-test:
	$(NOSE) tests/unit

integration-test:
	$(NOSE) tests/integration

system-test:
	$(NOSE) tests/system

acceptance-test:
	$(NOSE) tests/acceptance

tdd:
	$(NOSYD)

coverage:
	-rm -f .coverage
	$(NOSE) $(COVERAGE_ARGS) --cover-package=tests.unit tests/unit
	-rm -f .coverage


## Documentation ##
.PHONY: doc
doc:
	$(PYTHON) setup.py build_sphinx


## Static analysis ##
.PHONY: lint uml metrics
lint:
	bin/pylint --rcfile pylintrc $(PACKAGE)


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
.PHONY: dist upload $(DIST_FILE)
dist: $(DIST_FILE)
$(DIST_FILE):
	$(PYTHON) setup.py sdist

upload: dist
	@if echo $(VERSION) | grep -q dirty; then \
	    echo "Stubbornly refusing to upload a dirty package! Tag a proper release!" >&2; \
	    exit 1; \
	fi
	$(SCP) $(DIST_FILE) $(PYTHON_DIST_SITE)

deploy-docs: $(PACKAGE)_docs.tar.gz
	fab deploy_docs

$(PACKAGE)_docs.tar.gz: doc
	tar zcf $@ doc/html


## Housekeeping ##
clean:
	# clean python bytecode files
	-find . -type f -name '*.pyc' -o -name '*.tar.gz' | xargs rm -f
	-rm -f nosetests.xml
	-rm -f pip-log.txt
	-rm -f .nose-stopwatch-times
	#
	-rm -rf build dist tmp uml/* *.egg-info RELEASE-VERSION

maintainer-clean: clean
	rm -rf bin include lib man share src doc/doctrees doc/html
