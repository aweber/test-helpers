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
COVERAGE_ARGS = --with-coverage --cover-erase --cover-package=$(MODULE) --cover-branches --cover-tests
DEVELOPMENT_ENV = $(shell echo $(PACKAGE) | tr 'a-z\-' 'A-Z_')_CONF=configuration/development.conf
EASY_INSTALL = easy_install
PEP8 = pep8
PIP = C_INCLUDE_PATH="/opt/local/include:/usr/local/include" pip
PIPOPTS=$(patsubst %,-r %,$(wildcard $(HOME)/.requirements.pip requirements.pip)) --index-url=http://pypi.colo.lair/simple/
PYLINT = pylint
PYTHON = python
PYTHON_VERSION = python2.6
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
TEST_TARGETS := $(foreach scope, unit integration acceptance, $(scope)-test)
COVERAGE_TARGETS := $(foreach scope, unit integration, $(scope)-coverage)
SCOPED_TARGETS := $(TEST_TARGETS) $(COVERAGE_TARGETS)

.PHONY: test coverage $(SCOPED_TARGETS)
test: $(TEST_TARGETS)
coverage: unit-coverage

$(SCOPED_TARGETS):SCOPE = $(word 1,$(subst -, ,$@))
$(TEST_TARGETS): reports
	$(DEVELOPMENT_ENV) $(SETUP) test $(SCOPE) --with-xunit --xunit-file=reports/$(SCOPE)-xunit.xml
$(COVERAGE_TARGETS): reports
	$(DEVELOPMENT_ENV) $(SETUP) test $(COVERAGE_ARGS) $(SCOPE)
	$(COVERAGE) xml -o  --include="*.py" reports/$(SCOPE)-coverage.xml

reports: dev
	mkdir -p $@

## Documentation ##
.PHONY: doc
doc: dev
	$(SETUP) build_sphinx

## Static Analysis ##
.PHONY: lint pep8 pylint
lint: pep8 pylint
pylint: reports .tests.pylintrc
	-$(PYLINT) --reports=y --output-format=parseable --rcfile=pylintrc $(MODULE) | tee reports/$(MODULE)_pylint.txt
	-$(PYLINT) --reports=y --output-format=parseable --rcfile=.tests.pylintrc tests | tee reports/tests_pylint.txt

.tests.pylintrc: pylintrc pylintrc-tests-overrides
	cat $^ > $@

pep8: reports
	# Strip out warnings about long lines in tests. We loosen the
	# limitation for long lines in tests and Pylint already checks line
	# length for us.
	-$(PEP8) --filename="*.py" --repeat $(MODULE) tests | grep -v '^tests/.*E501' | tee reports/pep8.txt

## Local Setup ##
.PHONY: requirements req virtualenv dev
requirements: virtualenv
	@rm -f .req
	$(MAKE) .req
req: .req
.req: $(ENVDIR) requirements.pip
	$(EASY_INSTALL) -U distribute
	# need ports libevent and libevent1 for mac_dev
	$(PIP) install $(PIPOPTS)
	$(EASY_INSTALL) -U $(ADDTLREQS)
	@touch .req

virtualenv: RELEASE-VERSION $(ENVDIR)
$(ENVDIR):
	$(VIRTUALENV) $(VIRTUALENVOPTS) $(ENVDIR)

dev: RELEASE-VERSION $(EGG_LINK)
$(EGG_LINK): setup.py .req
	$(SETUP) develop

## Packaging ##
.PHONY: RELEASE-VERSION
RELEASE-VERSION:
	echo $(VERSION) > $@

.PHONY: dist upload $(DIST_FILE)
dist: $(DIST_FILE)
$(DIST_FILE): RELEASE-VERSION
	$(SETUP) sdist

upload: dist
	@if echo $(VERSION) | grep -q dirty; then \
	    echo "Stubbornly refusing to upload a dirty package! Tag a proper release!" >&2; \
	    exit 1; \
	fi
	$(SETUP) register --repository aweber sdist upload --repository aweber

deploy-docs: $(PACKAGE)_docs.tar.gz
	fab set_documentation_host deploy_docs:$(PACKAGE),`cat RELEASE-VERSION` -u ubuntu

$(PACKAGE)_docs.tar.gz: doc
	cd doc/html; tar czf ../../$@ *

## Housekeeping ##
.PHONY: clean maintainer-clean
clean:
	rm -rf $(ENVDIR) RELEASE-VERSION dist reports *.egg *.egg-info
	rm -f .coverage .nose-stopwatch-times .req .tests.pylintrc chef_script nosetests.xml pip-log.txt
	find . -type f -name '*.pyc' -delete

maintainer-clean: clean
	rm -rf doc/doctrees doc/html

## Service Deployment ##
.PHONY: vagrant-env chef-roles deploy-vagrant deploy-staging deploy-production
vagrant-env: Procfile
	caterer vagrant $(PACKAGE) Procfile > chef_script; sh chef_script

chef-roles: Procfile
	caterer production $(PACKAGE) Procfile > /dev/null

deploy-vagrant: dist
	fab set_hosts:'vagrant','api' deploy_api:'$(DIST_FILE)','$(APT_REQ_FILE)' -u vagrant -p vagrant

deploy-staging: dist Procfile
	caterer staging $(PACKAGE) Procfile > chef_script; sh chef_script
	fab set_hosts:'staging','api' deploy_api:'$(DIST_FILE)','$(APT_REQ_FILE)' -u ubuntu

deploy-production: dist Procfile
	caterer production $(PACKAGE) Procfile > chef_script; sh chef_script
	fab set_hosts:'production','api' deploy_api:'$(DIST_FILE)','$(APT_REQ_FILE)' -u ubuntu
