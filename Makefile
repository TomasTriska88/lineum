# --- Configuration ---
PYTHON = python
TOOLS  = tools

# --- Whitepaper Verification ---

# Default: complete whitepaper suite check (docs + contract)
check:
	$(PYTHON) $(TOOLS)/whitepaper_check.py

# Verify a specific run (usage: make verify RUN_DIR=output_wp/runs/...)
verify:
	$(PYTHON) $(TOOLS)/whitepaper_contract.py --run-dir $(RUN_DIR)

# --- Development ---

# Run comprehensive test suite
test:
	$(PYTHON) -m pytest tests/

# Install dependencies
install:
	pip install -r requirements.txt

# Clean temporary files and suite reports
clean:
	rm -rf .pytest_cache
	rm -rf __pycache__
	rm -rf $(TOOLS)/__pycache__
	rm -rf output_wp/runs/_whitepaper_contract/
	rm -f contract_*.txt

.PHONY: check verify test install clean
