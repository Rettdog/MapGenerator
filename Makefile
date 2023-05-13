.DEFAULT_GOAL=help

VENVPATH=venv
PYTHON=$(VENVPATH)/bin/python3

.PHONY: venv
venv: $(VENVPATH)/bin/activate
$(VENVPATH)/bin/activate: requirements.txt
	test -d $(VENVPATH) || python3 -m venv $(VENVPATH); \
	. $(VENVPATH)/bin/activate; \
	pip install -r requirements.txt; \
	touch $(VENVPATH)/bin/activate;

##install-deps: setup your dev environment
.PHONY: install-deps
install-deps: venv

##run: run the map generator 
.PHONY: run
run: install-deps
	$(PYTHON) map-generator.py

.PHONY: clean
clean:
	rm -rf $(VENVPATH)

##help: show help
.PHONY: help
help : Makefile
	@sed -n 's/^##//p' $<