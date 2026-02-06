PYTHON = python3
SCRIPT = make.py

.PHONY: help build_docs clean linkcheck

# Route all unknown targets to the python script
%:
	@$(PYTHON) $(SCRIPT) $@

help:
	@$(PYTHON) $(SCRIPT) help

build_docs:
	@$(PYTHON) $(SCRIPT) build_docs

clean:
	@$(PYTHON) $(SCRIPT) clean
