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
PIP = C_INCLUDE_PATH="/opt/local/include:/usr/local/include" pip
PIPOPTS=$(patsubst %,-r %,$(wildcard $(HOME)/.requirements.pip requirements.pip)) --index-url=http://pypi.colo.lair/simple/
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
.PHONY: test unit-test integration-test acceptance-test coverage coverage-html
test: unit-test integration-test acceptance-test
unit-test: reports
	$(DEVELOPMENT_ENV) $(SETUP) test unit --with-xunit --xunit-file=reports/unit-xunit.xml

integration-test: reports
	$(DEVELOPMENT_ENV) $(SETUP) test integration --with-xunit --xunit-file=reports/integration-xunit.xml

acceptance-test: reports
	$(DEVELOPMENT_ENV) $(SETUP) test acceptance --with-xunit --xunit-file=reports/acceptance-xunit.xml

coverage: reports
	$(DEVELOPMENT_ENV) $(SETUP) test $(COVERAGE_ARGS) --cover-package=tests.unit unit
	$(COVERAGE) xml -o reports/unit-coverage.xml --include="*.py"

integration-coverage: reports
	$(DEVELOPMENT_ENV) $(SETUP) test $(COVERAGE_ARGS) --cover-package=tests.integration integration
	$(COVERAGE) xml -o reports/integration-coverage.xml --include="*.py"

coverage-html:
	$(COVERAGE) html

reports: dev
	mkdir -p $@

## Documentation ##
.PHONY: doc
doc: dev
	$(SETUP) build_sphinx

## Static analysis ##
.PHONY: lint pep8 pylint
lint: pylint pep8
pylint: reports tests.pylintrc
	-pylint --reports=y --output-format=parseable --rcfile=pylintrc $(MODULE) | tee reports/$(MODULE)_pylint.txt
	-pylint --reports=y --output-format=parseable --rcfile=tests.pylintrc tests | tee reports/tests_lint.txt

tests.pylintrc: pylintrc pylintrc-tests-overrides
	cat $^ > $@

pep8: reports
	# Strip out warnings about long lines in tests. We loosen the
	# limitation for long lines in tests and PyLint already checks line
	# length for us.
	-pep8 --filename="*.py" --repeat $(MODULE) tests | grep -v '^tests/.*E501' | tee reports/pep8.txt

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
clean:
	# clean python bytecode files
	-find . -type f -name '*.pyc' -o -name '*.tar.gz' | xargs rm -f
	-rm -f pip-log.txt .req
	-rm -f .nose-stopwatch-times .coverage
	-rm -rf reports
	-rm -f nosetests.xml
	-rm -rf $(ENVDIR) dist *.egg-info RELEASE-VERSION htmlcov

maintainer-clean: clean
	rm -rf doc/doctrees doc/html

## Service Deployment ##
.PHONY: deploy-staging deploy-production
deploy-staging: dist Procfile
	caterer staging $(PACKAGE) Procfile > chef_script; sh chef_script
	fab set_hosts:'staging','api' deploy_api:'$(DIST_FILE)','$(APT_REQ_FILE)' -u ubuntu

deploy-production: dist Procfile
	caterer production $(PACKAGE) Procfile > chef_script; sh chef_script
	fab set_hosts:'production','api' deploy_api:'$(DIST_FILE)','$(APT_REQ_FILE)' -u ubuntu

deploy-vagrant: dist
	fab set_hosts:'vagrant','api' deploy_api:'$(DIST_FILE)','$(APT_REQ_FILE)' -u vagrant -p vagrant

create-vagrant-env: Procfile
	caterer vagrant $(PACKAGE) Procfile > chef_script; sh chef_script

chef-roles: Procfile
	caterer production $(PACKAGE) Procfile > /dev/null
