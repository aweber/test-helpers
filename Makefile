#
# Basic makefile for general targets
#
PACKAGE = test_helpers
MODULE = test_helpers

##
## NOTE: Anything changed below this line should be changed in base_service.git
## and then merged into individual projects.  This prevents conflicts and
## maintains consistency between projects.
##

# The following definitions describe the target environment.  Test coverage
# reports will target this environment.
PYTHON_VERSION = python2.6
PYTHON_TOX_ENV = py26

ACTIVATE = $(ENVDIR)/bin/activate
ENVDIR = ./env
COVERAGE = $(ENVDIR)/bin/coverage
FABRIC = $(ENVDIR)/bin/fab
NOSE = $(ENVDIR)/bin/nosetests
PIP = C_INCLUDE_PATH="/opt/local/include:/usr/local/include" $(ENVDIR)/bin/pip
PIPOPTS= -r requirements.pip
PYTHON = $(ENVDIR)/bin/python
REPORTDIR = reports
SETUP = . $(ACTIVATE); $(PYTHON) setup.py
TESTS = tests/unit tests/integration
TOX = $(DEVELOPMENT_ENV) $(ENVDIR)/bin/detox
VIRTUALENV = virtualenv
VIRTUALENVOPTS = --python=$(PYTHON_VERSION)

## Testing ##
.PHONY: test coverage
test: $(REPORTDIR) requirements
	@echo Running tests
	$(DEVELOPMENT_ENV) $(TOX) -- --cover-erase --with-coverage --cover-package=$(MODULE) $(TESTS)

coverage: $(REPORTDIR)
	- $(RM) .coverage
	$(DEVELOPMENT_ENV) $(TOX) -e $(PYTHON_TOX_ENV) -- --cover-erase --with-coverage --cover-package=tests,$(PACKAGE) tests
	$(COVERAGE) html -d $(REPORTDIR)/htmlcov
	$(COVERAGE) xml  -o $(REPORTDIR)/coverage.xml

%-test: $(REPORTDIR)
	@echo Running $* tests
	$(DEVELOPMENT_ENV) $(TOX) -- tests/$*
	cp $(REPORTDIR)/$(PYTHON_TOX_ENV)-xunit.xml $(REPORTDIR)/$*-xunit.xml

%-coverage: $(REPORTDIR)
	$(DEVELOPMENT_ENV) $(TOX) -- --cover-erase --with-coverage --cover-package=tests,$(PACKAGE) tests/$*

$(REPORTDIR):
	test -d "$@" || mkdir -p "$@"
	touch "$@"

## Local Setup ##
.PHONY: requirements virtualenv
requirements: $(ENVDIR) requirements.pip
	$(PIP) install $(PIPOPTS)

virtualenv: $(ENVDIR)
$(ENVDIR):
	$(VIRTUALENV) $(VIRTUALENVOPTS) $(ENVDIR)

## Housekeeping ##
.PHONY: clean maintainer-clean
clean:
	@echo "Removing output files"
	$(RM) .nose-stopwatch-times pip-log.txt
	$(RM) -r dist disttest *.egg *.egg-info
	find . -type f -name '*.pyc' -delete
	find . -type d -name __pycache__ -delete
	$(RM) -r $(REPORTDIR) build
	$(RM) .coverage

maintainer-clean: clean
	@echo "Removing all generated and downloaded files"
	$(RM) -r $(ENVDIR)
	$(RM) -r .tox
