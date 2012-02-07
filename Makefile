#
# Basic makefile for general targets
#
PACKAGE = @@baseservice@@
MODULE = $(PACKAGE)

##
## NOTE: Anything changed below this line should be changed in base_service.git
## and then merged into individual projects.  This prevents conflicts and
## maintains consistency between projects.
##
COVERAGE = bin/coverage
COVERAGE_ARGS = --with-coverage --cover-package=$(MODULE) --cover-tests --cover-erase
DEVELOPMENT_ENV = source bin/activate; $(shell echo $(PACKAGE) | tr 'a-z\-' 'A-Z_')_CONF=configuration/development.conf
DIST_FILE = dist/$(PACKAGE)-$(VERSION).tar.gz
EASY_INSTALL = bin/easy_install
FLASKAPI_DOCS = PYTHONPATH=. bin/flaskapi-docs
IPYTHON = bin/ipython
NOSE = bin/nosetests
NOSYD = bin/nosyd -1
PIP = bin/pip
PYREVERSE = pyreverse -o png -p
PYTHON = bin/python
PYTHON_DIST_SITE = nebula.ofc.lair:/var/www/secure/python-dist/
PYTHON_DOCTEST = $(PYTHON) -m doctest
SCP = scp
# Work around a bug in git describe: http://comments.gmane.org/gmane.comp.version-control.git/178169
VERSION = $(shell git status >/dev/null 2>/dev/null && git describe --abbrev=4 --tags --dirty --match="v*" | cut -c 2-)

## Testing ##
.PHONY: test unit-test integration-test system-test acceptance-test tdd coverage coverage-html
test: unit-test integration-test system-test acceptance-test
unit-test: reports
	$(DEVELOPMENT_ENV) $(NOSE) tests/unit --with-xunit --xunit-file=reports/unit-xunit.xml

integration-test: reports
	$(DEVELOPMENT_ENV) $(NOSE) tests/integration --with-xunit --xunit-file=reports/integration-xunit.xml

system-test: reports
	$(DEVELOPMENT_ENV) $(NOSE) tests/system --with-xunit --xunit-file=reports/system-xunit.xml

acceptance-test: reports
	$(DEVELOPMENT_ENV) $(NOSE) tests/acceptance --with-xunit --xunit-file=reports/acceptance-xunit.xml

tdd:
	$(DEVELOPMENT_ENV) $(NOSYD)

coverage: reports
	$(DEVELOPMENT_ENV) $(NOSE) $(COVERAGE_ARGS) --cover-package=tests.unit tests/unit
	$(COVERAGE) xml -o reports/unit-coverage.xml --include="*.py"

integration-coverage: reports
	$(DEVELOPMENT_ENV) $(NOSE) $(COVERAGE_ARGS) --cover-package=tests.integration tests/integration
	$(COVERAGE) xml -o reports/integration-coverage.xml --include="*.py"

coverage-html:
	$(COVERAGE) html

reports:
	mkdir -p $@


## Documentation ##
.PHONY: doc generated_api_doc
doc: RELEASE-VERSION generated_api_doc
	$(PYTHON) setup.py build_sphinx

generated_api_doc:
	# Generate the docs for API views if the appropriate module is present.
ifneq "$(strip $(wildcard $(MODULE)/api/views))" ""
	$(FLASKAPI_DOCS) $(MODULE).api.views > ./doc/source/generated_api_doc.rst
endif


## Static analysis ##
.PHONY: lint uml metrics
lint: reports
	bin/pylint --rcfile pylintrc $(MODULE) | tee reports/$(MODULE)_pylint.txt


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


.PHONY: foreman
foreman:
	$(DEVELOPMENT_ENV) foreman start


## Packaging ##
.PHONY: RELEASE-VERSION
RELEASE-VERSION:
	echo $(VERSION) > $@

.PHONY: dist upload $(DIST_FILE)
dist: $(DIST_FILE)
$(DIST_FILE): RELEASE-VERSION
	$(PYTHON) setup.py sdist

upload: dist
	@if echo $(VERSION) | grep -q dirty; then \
	    echo "Stubbornly refusing to upload a dirty package! Tag a proper release!" >&2; \
	    exit 1; \
	fi
	$(SCP) $(DIST_FILE) $(PYTHON_DIST_SITE)

deploy-docs: $(PACKAGE)_docs.tar.gz
	fab set_documentation_host deploy_docs

$(PACKAGE)_docs.tar.gz: doc
	tar zcf $@ doc/html


## Housekeeping ##
clean:
	# clean python bytecode files
	-find . -type f -name '*.pyc' -o -name '*.tar.gz' | xargs rm -f
	-rm -f pip-log.txt
	-rm -f .nose-stopwatch-times .coverage
	-rm -rf reports
	#
	-rm -rf build dist tmp uml/* *.egg-info RELEASE-VERSION htmlcov

maintainer-clean: clean
	rm -rf bin include lib man share src doc/doctrees doc/html

## Service Deployment ##
.PHONY: deploy-staging deploy-production
deploy-staging: dist Procfile
	caterer staging $(PACKAGE) Procfile > chef_script; sh chef_script
	fab set_hosts:'staging','api' deploy_api:$(DIST_FILE)

deploy-production: dist Procfile
	caterer production $(PACKAGE) Procfile > chef_script; sh chef_script
	fab set_hosts:'production','api' deploy_api:$(DIST_FILE)
