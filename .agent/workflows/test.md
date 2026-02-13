---
description: How to run the test suite after code changes
---

# Running Tests

## Full suite (unit + integration)
// turbo
```bash
pytest tests/ -v
```

## Unit tests only (fast, ~1s)
// turbo
```bash
pytest tests/ -v -m "not integration"
```

## Integration tests only (slower, ~20s, runs lineum.py as subprocess)
// turbo
```bash
pytest tests/ -v -m integration
```

## When to run
- **Always** after modifying `lineum.py`
- **Always** before committing
- After adding new tests
