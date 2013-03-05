#
# Basic makefile for general targets
#
PACKAGE = @@project_name@@
MODULE = @@python_module@@

##
## NOTE: Anything changed below this line should be changed in base_service.git
## and then merged into individual projects.  This prevents conflicts and
## maintains consistency between projects.
##
ENVDIR = ./env
SHELL = BASH_ENV=$(ENVDIR)/bin/activate /bin/bash

COVERAGE = coverage
COVERAGE_ARGS := --with-coverage --cover-erase --cover-package=$(MODULE) --cover-branches
DEVELOPMENT_ENV = $(shell echo $(PACKAGE) | tr 'a-z\-' 'A-Z_')_CONF=configuration/development.conf
EASY_INSTALL = easy_install
PEP8 = pep8
PIP = C_INCLUDE_PATH="/opt/local/include:/usr/local/include" pip
PIPOPTS=$(patsubst %,-r %,$(wildcard $(HOME)/.requirements.pip requirements.pip)) --index-url=http://pypi.colo.lair/simple/
PYLINT = pylint
PYTHON = python
PYTHON_VERSION = python2.6
REPORTDIR = reports
RUN_TEST_SUITE_SUBSET = $(DEVELOPMENT_ENV) $(SETUP) -q test --where=tests/$(SCOPE)
SCP = scp
SETUP := $(PYTHON) setup.py
# Work around a bug in git describe: http://comments.gmane.org/gmane.comp.version-control.git/178169
VERSION = $(shell git status >/dev/null 2>/dev/null && git describe --abbrev=6 --tags --dirty --match="v*" | cut -c 2-)
VIRTUALENV = virtualenv
VIRTUALENVOPTS = --distribute --python=$(PYTHON_VERSION) --no-site-packages

APT_REQ_FILE = requirements.apt
DIST_FILE = dist/$(PACKAGE)-$(VERSION).tar.gz
EGG_LINK := $(ENVDIR)/lib/$(PYTHON_VERSION)/site-packages/$(PACKAGE).egg-link

# Requirements that cannot be installed via pip (packages
# listed here will be installed via easy_install)
ADDTLREQS = nose_machineout readline

## Testing ##
TESTS = unit-test integration-test acceptance-test
.PHONY: test $(TESTS)
test: $(TESTS)
$(TESTS):SCOPE = $(word 1,$(subst -, ,$@))
$(TESTS): $(REPORTDIR)
	@echo Running $(SCOPE) tests
	@$(RUN_TEST_SUITE_SUBSET) --with-xunit --xunit-file=$(REPORTDIR)/$(SCOPE)-xunit.xml

.PHONY: coverage unit-coverage integration-coverage
coverage: unit-coverage
unit-coverage integration-coverage:SCOPE = $(word 1,$(subst -, ,$@))
unit-coverage integration-coverage:COVERAGE_ARGS += $(if $(shell $(PIP) freeze | grep '^rednose'),--no-color)
unit-coverage integration-coverage: $(REPORTDIR)
	$(RUN_TEST_SUITE_SUBSET) $(COVERAGE_ARGS)
	$(COVERAGE) html -d $(REPORTDIR)/htmlcov-$(SCOPE) --omit=$(ENVDIR)/*
	$(COVERAGE) xml -o $(REPORTDIR)/$(SCOPE)-coverage.xml --omit=$(ENVDIR)/*

$(REPORTDIR): $(EGG_LINK)
	[[ -d $@ ]] && touch $@ || mkdir -p $@

## Documentation ##
.PHONY: doc deploy-docs
doc: $(EGG_LINK)
	$(MAKE) --always-make RELEASE-VERSION
	mkdir -p $(CURDIR)/doc/source/_static
	$(SETUP) build_sphinx

$(PACKAGE)_docs.tar.gz: doc
	cd doc/html; tar czf ../../$@ *

deploy-docs: $(PACKAGE)_docs.tar.gz
	fab set_documentation_host deploy_docs:$(PACKAGE),`cat RELEASE-VERSION` -u ubuntu

## Static Analysis ##
.PHONY: lint pep8 pylint
lint: pep8 pylint

pylint: $(REPORTDIR) .tests.pylintrc
	$(PYLINT) --reports=y --output-format=parseable --rcfile=pylintrc $(MODULE) | tee $(REPORTDIR)/$(MODULE)_pylint.txt
	$(PYLINT) --reports=y --output-format=parseable --rcfile=.tests.pylintrc tests | tee $(REPORTDIR)/tests_pylint.txt

.tests.pylintrc: pylintrc pylintrc-tests-overrides
	cat $^ > $@

pep8: $(REPORTDIR)
	# Strip out warnings about long lines in tests. We loosen the
	# limitation for long lines in tests and Pylint already checks line
	# length for us.
	$(PEP8) --filename="*.py" --repeat $(MODULE) tests | grep -v '^tests/.*E501' | tee $(REPORTDIR)/pep8.txt

## Local Setup ##
.PHONY: requirements req virtualenv dev
requirements:
	@rm -f .req
	$(MAKE) .req

req: .req
.req: $(ENVDIR) requirements.pip
	$(EASY_INSTALL) -U distribute
	$(PIP) install $(PIPOPTS)
	$(EASY_INSTALL) -U $(ADDTLREQS)
	@touch .req

setup.py: RELEASE-VERSION
RELEASE-VERSION:
	@echo Updating $@ "($(VERSION))"
	@echo $(VERSION) > $@

dev: $(EGG_LINK)
$(EGG_LINK): setup.py .req
	$(SETUP) develop

virtualenv: $(ENVDIR)
$(ENVDIR):
	$(VIRTUALENV) $(VIRTUALENVOPTS) $(ENVDIR)

## Packaging ##
.PHONY: dist upload $(DIST_FILE)
dist: test sdist
sdist: $(DIST_FILE)
$(DIST_FILE):MAKEFLAGS=--always-make
$(DIST_FILE): setup.py
	$(SETUP) sdist

upload:
	@if echo $(VERSION) | grep -q dirty; then \
	    echo "Stubbornly refusing to upload a dirty package! Tag a proper release!" >&2; \
	    exit 1; \
	fi
	$(MAKE) dist
	$(SETUP) register --repository aweber sdist upload --repository aweber

## Housekeeping ##
.PHONY: clean maintainer-clean
clean:
	rm -rf $(ENVDIR) RELEASE-VERSION dist $(REPORTDIR) *.egg *.egg-info
	rm -f .coverage .nose-stopwatch-times .req .tests.pylintrc chef_script pip-log.txt
	find . -type f -name '*.pyc' -delete

maintainer-clean: clean
	rm -rf doc/doctrees doc/html

## Service Deployment ##
.PHONY: vagrant-env chef-roles deploy-vagrant deploy-staging deploy-production
vagrant-env:
	caterer vagrant $(PACKAGE) Procfile > chef_script; sh chef_script

chef-roles:
	caterer production $(PACKAGE) Procfile >/dev/null

deploy-vagrant: dist
	fab set_hosts:'vagrant','api' deploy_api:'$(DIST_FILE)','$(APT_REQ_FILE)' -u vagrant -p vagrant

deploy-staging: dist
	caterer staging $(PACKAGE) Procfile > chef_script; sh chef_script
	fab set_hosts:'staging','api' deploy_api:'$(DIST_FILE)','$(APT_REQ_FILE)' -u ubuntu

deploy-production: dist
	caterer production $(PACKAGE) Procfile > chef_script; sh chef_script
	fab set_hosts:'production','api' deploy_api:'$(DIST_FILE)','$(APT_REQ_FILE)' -u ubuntu
