.PHONY: ingest test eval serve-mcp run

PYTHON ?= python

ingest:
	$(PYTHON) scripts/build_index.py

test:
	$(PYTHON) -m pytest

eval:
	$(PYTHON) evals/run_evals.py

serve-mcp:
	$(PYTHON) -m battery_advisor.mcp_server.server

run:
	$(PYTHON) -m battery_advisor.ui.app
