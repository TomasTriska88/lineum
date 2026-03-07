"""
Tests for the Expectation Checker (P3) — dual-audience labels, schema validity,
and evaluate_expectations correctness.

These tests do NOT require PyTorch/GPU — they test pure Python expectation logic.
"""
import pytest
from scripts.validation_core import (
    evaluate_expectations,
    HYDRO_EXPECTATIONS,
    WAVE_SANITY_EXPECTATIONS,
    MU_REGRESSION_EXPECTATIONS,
    PLAYGROUND_EXPECTATIONS,
    GOLDEN_HYDRO_SWEEP,
)

ALL_EXPECTATIONS = [
    ("hydro", HYDRO_EXPECTATIONS),
    ("wave_sanity", WAVE_SANITY_EXPECTATIONS),
    ("mu_regression", MU_REGRESSION_EXPECTATIONS),
    ("playground", PLAYGROUND_EXPECTATIONS),
]

# ── Schema Tests ──────────────────────────────────────────────


class TestExpectationSchema:
    """Every expectation must conform to the required schema."""

    @pytest.mark.parametrize("scenario,expectations", ALL_EXPECTATIONS)
    def test_every_expectation_has_required_fields(self, scenario, expectations):
        """Each expectation must have: metric, op, value, label, human_label."""
        required = {"metric", "op", "value", "label", "human_label"}
        for i, exp in enumerate(expectations):
            missing = required - set(exp.keys())
            assert not missing, (
                f"[{scenario}] Expectation #{i} missing fields: {missing}\n"
                f"  Got: {exp}"
            )

    @pytest.mark.parametrize("scenario,expectations", ALL_EXPECTATIONS)
    def test_label_and_human_label_are_different(self, scenario, expectations):
        """human_label must NOT be identical to label (that defeats the purpose)."""
        for i, exp in enumerate(expectations):
            assert exp["human_label"] != exp["label"], (
                f"[{scenario}] Expectation #{i}: human_label is identical to label.\n"
                f"  label: '{exp['label']}'\n"
                f"  human_label: '{exp['human_label']}'\n"
                f"  They must be distinct (layperson vs scientific)."
            )

    @pytest.mark.parametrize("scenario,expectations", ALL_EXPECTATIONS)
    def test_human_label_is_layperson_friendly(self, scenario, expectations):
        """human_label should not contain heavy scientific notation like ΔE, ψ, μ."""
        scientific_markers = ["ΔE/E", "N(t)", "E(t)", "ψ"]
        for i, exp in enumerate(expectations):
            hlabel = exp["human_label"]
            for marker in scientific_markers:
                assert marker not in hlabel, (
                    f"[{scenario}] Expectation #{i}: human_label contains "
                    f"scientific notation '{marker}'.\n"
                    f"  human_label: '{hlabel}'\n"
                    f"  human_label must be plain language."
                )

    @pytest.mark.parametrize("scenario,expectations", ALL_EXPECTATIONS)
    def test_valid_operator(self, scenario, expectations):
        """op must be one of <, >, ==, <=, >=."""
        valid_ops = {"<", ">", "==", "<=", ">="}
        for i, exp in enumerate(expectations):
            assert exp["op"] in valid_ops, (
                f"[{scenario}] Expectation #{i}: invalid op '{exp['op']}'"
            )


# ── Evaluate Expectations Engine Tests ────────────────────────


class TestEvaluateExpectations:
    """Tests for the evaluate_expectations() function."""

    def test_all_pass(self):
        """When all metrics satisfy expectations, overall_pass == True."""
        expectations = [
            {"metric": "a", "op": "<", "value": 1.0, "label": "a < 1", "human_label": "a is small"},
            {"metric": "b", "op": ">", "value": 0.5, "label": "b > 0.5", "human_label": "b is big"},
        ]
        measured = {"a": 0.5, "b": 0.8}
        results, overall = evaluate_expectations(expectations, measured)
        assert overall is True
        assert all(r["passed"] for r in results)

    def test_one_fails(self):
        """When one metric fails, overall_pass == False."""
        expectations = [
            {"metric": "a", "op": "<", "value": 1.0, "label": "a < 1", "human_label": "a is small"},
            {"metric": "b", "op": ">", "value": 0.5, "label": "b > 0.5", "human_label": "b is big"},
        ]
        measured = {"a": 0.5, "b": 0.3}  # b fails
        results, overall = evaluate_expectations(expectations, measured)
        assert overall is False
        assert results[0]["passed"] is True
        assert results[1]["passed"] is False

    def test_missing_metric_fails(self):
        """If a metric is missing from measured values, the expectation fails."""
        expectations = [
            {"metric": "x", "op": "<", "value": 1.0, "label": "x < 1", "human_label": "x is small"},
        ]
        measured = {}  # x is missing
        results, overall = evaluate_expectations(expectations, measured)
        assert overall is False
        assert results[0]["measured"] is None
        assert results[0]["passed"] is False

    def test_human_label_propagated(self):
        """evaluate_expectations must propagate human_label into results."""
        expectations = [
            {"metric": "a", "op": "<", "value": 1.0,
             "label": "Scientific label",
             "human_label": "Plain language label"},
        ]
        measured = {"a": 0.5}
        results, _ = evaluate_expectations(expectations, measured)
        assert results[0]["human_label"] == "Plain language label"
        assert results[0]["label"] == "Scientific label"

    def test_human_label_fallback(self):
        """If human_label is missing, it falls back to label."""
        expectations = [
            {"metric": "a", "op": "<", "value": 1.0, "label": "fallback label"},
        ]
        measured = {"a": 0.5}
        results, _ = evaluate_expectations(expectations, measured)
        assert results[0]["human_label"] == "fallback label"

    def test_equality_operator(self):
        """The == operator works correctly."""
        expectations = [
            {"metric": "flag", "op": "==", "value": 1.0, "label": "flag==1", "human_label": "flag on"},
        ]
        measured = {"flag": 1.0}
        results, overall = evaluate_expectations(expectations, measured)
        assert overall is True

    def test_measured_values_rounded(self):
        """Measured values are rounded to 6 decimal places."""
        expectations = [
            {"metric": "a", "op": "<", "value": 1.0, "label": "a<1", "human_label": "a small"},
        ]
        measured = {"a": 0.123456789}
        results, _ = evaluate_expectations(expectations, measured)
        assert results[0]["measured"] == 0.123457  # rounded to 6 dp


# ── Golden Sweep Config Tests ─────────────────────────────────


class TestGoldenConfig:
    """Tests for the golden validate sweep configuration."""

    def test_golden_hydro_sweep_is_conservative(self):
        """Golden sweep must NOT contain Z > 2.0 or grid > 64."""
        for entry in GOLDEN_HYDRO_SWEEP:
            grid, Z, eps = entry[0], entry[1], entry[2]
            wave_dt = entry[3] if len(entry) > 3 else 0.01
            assert Z <= 2.0, f"Golden sweep has aggressive Z={Z}"
            assert grid <= 64, f"Golden sweep has large grid={grid}"
            assert eps > 0, f"Golden sweep has invalid eps={eps}"
            assert wave_dt <= 0.05, f"Golden sweep wave_dt too large: {wave_dt}"

    def test_golden_hydro_sweep_nonempty(self):
        """Golden sweep must contain at least one configuration."""
        assert len(GOLDEN_HYDRO_SWEEP) >= 1
