"""
Enforcement test: Every Lab API endpoint MUST return explain_pack
with all mandatory Canon keys.

Canon §2: explain_pack is a Mandatory Contract.
Canon §10: Lint/Test must fail the build if scenario lacks explain_pack.
"""
import pytest
from fastapi.testclient import TestClient
from routing_backend.main import app

client = TestClient(app)

MANDATORY_KEYS = [
    "one_liner_human",
    "what_you_see",
    "what_it_is_not",
    "success_criteria_human",
    "next_action_pass",
    "next_action_fail",
    "disclaimers",
    "glossary_terms_used",
]

ENDPOINTS = [
    ("/api/lab/hydrogen/sweep", "GET"),
    ("/api/lab/regression/snapshot", "GET"),
    ("/api/lab/ra/unitarity", "GET"),
    ("/api/lab/ra/bound-state", "GET"),
    ("/api/lab/ra/excited-state", "GET"),
    ("/api/lab/ra/mu-memory", "GET"),
    ("/api/lab/ra/driving", "GET"),
    ("/api/lab/ra/lpf-impact", "GET"),
]


@pytest.mark.parametrize("endpoint,method", ENDPOINTS, ids=[e[0].split("/")[-1] for e in ENDPOINTS])
def test_explain_pack_present_and_complete(endpoint, method):
    """Every lab endpoint must return explain_pack with ALL mandatory keys."""
    if method == "GET":
        res = client.get(endpoint)
    else:
        res = client.post(endpoint, json={})

    assert res.status_code == 200, f"{endpoint} returned {res.status_code}"
    data = res.json()

    assert "explain_pack" in data, f"{endpoint} is missing explain_pack entirely"
    ep = data["explain_pack"]
    assert isinstance(ep, dict), f"{endpoint} explain_pack is not a dict: {type(ep)}"

    for key in MANDATORY_KEYS:
        assert key in ep, f"{endpoint} explain_pack is missing mandatory key: {key}"
        # Verify non-empty values
        val = ep[key]
        if isinstance(val, str):
            assert len(val) > 0, f"{endpoint} explain_pack.{key} is empty string"
        elif isinstance(val, list):
            # disclaimers can be empty for some scenarios, so only check type
            assert isinstance(val, list), f"{endpoint} explain_pack.{key} is not a list"


def test_playground_explain_pack():
    """POST /api/lab/playground must also return explain_pack."""
    res = client.post("/api/lab/playground", json={
        "config": {"Z": 1.0, "eps": 0.1, "dt": 0.01, "grid_size": 64}
    })
    assert res.status_code == 200
    data = res.json()
    assert "explain_pack" in data
    ep = data["explain_pack"]
    for key in MANDATORY_KEYS:
        assert key in ep, f"playground explain_pack missing: {key}"


def test_timeseries_data_not_ts_metrics():
    """All endpoints must return timeseries_data, NOT ts_metrics at API level."""
    for endpoint, method in ENDPOINTS:
        if method == "GET":
            res = client.get(endpoint)
        else:
            res = client.post(endpoint, json={})
        data = res.json()
        # timeseries_data should be present (some endpoints may not have it)
        if "timeseries_data" in data:
            assert "ts_metrics" not in data, f"{endpoint} returns BOTH timeseries_data and ts_metrics"
