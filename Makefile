# Common commands. Run `make help`.
.PHONY: help setup fake test lint run-fake run status

help:
	@echo "make setup     install the package and dev tools (do this once, inside a virtualenv)"
	@echo "make fake      write synthetic versions of every data file to data/fake/"
	@echo "make test      run all tests on fake data"
	@echo "make lint      ruff check"
	@echo "make run-fake  run every stage on fake data, skipping ones not built yet"
	@echo "make run       full run on real data (needs LRREP_DATA_DIR set)"
	@echo "make status    list stages and owners"

setup:
	python -m pip install -e ".[dev]"

fake:
	python -m lrrep.fake

test:
	python -m pytest

lint:
	ruff check src tests

run-fake:
	python -m lrrep.pipeline --all --fake --keep-going

run:
	python -m lrrep.pipeline --all

status:
	python -m lrrep.pipeline --list
