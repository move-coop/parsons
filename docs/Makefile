PYTHON     := python3
SCRIPT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
SCRIPT     := $(SCRIPT_DIR)make.py

.PHONY: % check_python

%: check_python
	@$(PYTHON) "$(SCRIPT)" $@ $(filter-out $@,$(MAKECMDGOALS))

check_python:
	@$(PYTHON) --version > /dev/null 2>&1 || (echo "Error: Python not found."; exit 1)

$(filter-out $(firstword $(MAKECMDGOALS)),$(MAKECMDGOALS)):
	@:
