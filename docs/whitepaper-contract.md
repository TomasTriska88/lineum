# Whitepaper Contract Runner

This tool (`tools/whitepaper_contract.py`) validates that an audit run meets the specific numerical and metadata anchors defined in the Lineum Core whitepaper.

It is designed to be a standalone verification step, decoupled from the application test suite, ensuring that the "scientific claims" of the paper (e.g., specific frequency anchors, tolerances) are met by the generated evidence.

## Usage

<!-- CLI_DOC_START -->
Usage:
  python tools/whitepaper_contract.py [--run-dir <path> | --runs-root <path>] [--contract <path>] [--strict]

Arguments:
  --run-dir <path>      Verify a single audit run directory (must be inside output_wp).
  --runs-root <path>    Verify all runs in this root directory (default: output_wp/runs).
  --contract <path>     Path to contract JSON (default: contracts/lineum-core-*.contract.json).
  --strict              Fail on any warning (default: Fail only on FATAL error).
  --backfill-analysis-config Backfill missing analysis_config metadata to manifest.json
  --force               Force overwrite of existing metadata during backfill
<!-- CLI_DOC_END -->

### Entry Points

The recommended way to run the full suite check is via the `Makefile`:

```bash
make check
```

Alternatively, you can call the orchestrator directly:

```bash
python tools/whitepaper_check.py
```

## Contract Definition

The contract is defined in `contracts/lineum-core-1.0.9-core.contract.json`. It specifies:
- **Metadata**: Equation ID, Grid size, Time step, Boundary conditions.
- **Code Identity**: `expected.code_fingerprint_sha256` (SHA256 of enforced core files).
- **Anchors**: Numerical values for $f_0$, SBR, Half-life, etc., with specific absolute or relative tolerances.
- **Derived Checks**: Consistency checks for SI-derived values ($E$, $\lambda$, etc.).

> **Security**: The `code_fingerprint` enforces that the simulation and verification code have not been tampered with. It uses repo-root-relative paths (with `/` separators) and normalizes newlines (CRLF to LF) before hashing.

## Discovery & Duplicates

The runner scans all subdirectories in `--runs-root` (default `output_wp/runs/`), ignoring any starting with `_` (e.g. `_whitepaper_contract`).

**Duplicate Detection**:
Runs are identified by a hash of:
- `run_tag`
- `seed`
- `steps`
- `code_fingerprint`

If multiple runs share this identity, the first one encountered is processed, and subsequent ones are marked as `DUPLICATE` (status: `SKIP`) in the report. The suite does **not** automatically delete duplicates.

## Output

**Per Run:**
- `_<run_tag>_whitepaper_contract_result.json` is saved *inside* each run directory.

**Suite:**
- `whitepaper_contract_suite.json`: Aggregated results for all runs.

## Example Run

To verify all runs in `output_wp/runs`:

```bash
python tools/whitepaper_contract.py
```
