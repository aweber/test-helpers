override PIP = PIP_CONFIG_FILE=./pip.conf C_INCLUDE_PATH="/opt/local/include:/usr/local/include" $(ENVDIR)/bin/pip
TOX = $(ENVDIR)/bin/tox

## Testing ##
.PHONY: test sql-test setup-test-db unit-test integration-test acceptance-test coverage integration-coverage

test:

unit-test: RELEASE-VERSION $(REPORTDIR)
	$(DEVELOPMENT_ENV) $(TOX) -- tests/unit --with-xunit --xunit-file=$(REPORTDIR)/unit-xunit.xml

integration-test: RELEASE-VERSION $(REPORTDIR)
	$(DEVELOPMENT_ENV) $(TOX) -- tests/integration --with-xunit --xunit-file=$(REPORTDIR)/integration-xunit.xml

unit-coverage: $(REPORTDIR)
	$(DEVELOPMENT_ENV) $(NOSE) $(COVERAGE_ARGS) --with-coverage --with-xunit --cover-package=tests.unit,$(MODULE) tests/unit
	$(COVERAGE) xml -o $(REPORTDIR)/unit-coverage.xml --include="*.py"

integration-coverage: $(REPORTDIR)
	$(DEVELOPMENT_ENV) $(NOSE) $(COVERAGE_ARGS) --with-coverage --with-xunit --xunit-file=$(REPORTDIR)/integration-xunit.xml --cover-package=tests.integration tests/integration
	$(COVERAGE) xml -o $(REPORTDIR)/integration-coverage.xml --include="*.py"

clean-tox:
	rm -rf .tox

maintainer-clean: clean-tox
