.PHONY: install run debug clean lint lint-strict

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
MAIN = main.py
SRC = dijkstra.py models.py parser.py simulation.py visualizer/

install:
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) $(MAIN)

debug:
	$(PYTHON) -m pdb $(MAIN)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf $(VENV)

lint:
	$(VENV)/bin/flake8 $(MAIN) $(SRC)
	$(VENV)/bin/mypy $(MAIN) $(SRC) \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(VENV)/bin/flake8 $(MAIN) $(SRC)
	$(VENV)/bin/mypy $(MAIN) $(SRC) --strict
