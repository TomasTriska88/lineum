import sys
import os
import json
import pytest

# Extract evaluate_hash globally to formally test invariants independently
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(repo_root, "scripts"))
from verify_repro_run import evaluate_hash

# Mock references based strictly on CI validation and BLAS linkages
MOCK_WINDOWS_PROFILE = "win32_AMD64_py3.11_np1.25.2_openblas"
MOCK_UBUNTU_PROFILE = "linux_x86_64_py3.11_np1.26.4_openblas"

VALID_WINDOWS_HASH = "mock_windows_hash_123"
VALID_UBUNTU_HASH = "mock_ubuntu_hash_456"


@pytest.fixture
def profile_scoped_info():
    return {
        "step": 200,
        "psi_hashes": {
            MOCK_WINDOWS_PROFILE: VALID_WINDOWS_HASH,
            MOCK_UBUNTU_PROFILE: VALID_UBUNTU_HASH
        }
    }


@pytest.fixture
def legacy_scoped_info():
    return {
        "step": 200,
        "psi_hash": "legacy_string_hash_789"
    }


def test_approved_local_windows_profile_passes(profile_scoped_info):
    """Test that validating with the exact approved Windows profile succeeds."""
    ok, expected, src = evaluate_hash("psi", VALID_WINDOWS_HASH, profile_scoped_info, MOCK_WINDOWS_PROFILE)
    assert ok is True
    assert expected == VALID_WINDOWS_HASH
    assert f"Profile ({MOCK_WINDOWS_PROFILE})" in src


def test_approved_github_ubuntu_profile_passes(profile_scoped_info):
    """Test that validating with the exact approved Ubuntu profile succeeds."""
    ok, expected, src = evaluate_hash("psi", VALID_UBUNTU_HASH, profile_scoped_info, MOCK_UBUNTU_PROFILE)
    assert ok is True
    assert expected == VALID_UBUNTU_HASH
    assert f"Profile ({MOCK_UBUNTU_PROFILE})" in src


def test_unknown_profile_fails_clearly(profile_scoped_info):
    """Test that validating with an unknown profile gracefully fails and explicitly logs known profiles."""
    unknown_profile = "darwin_arm64_numpy2.0.0"
    ok, expected, src = evaluate_hash("psi", VALID_WINDOWS_HASH, profile_scoped_info, unknown_profile)
    assert ok is False
    assert expected == "N/A"
    assert "Unknown Profile" in src
    assert MOCK_WINDOWS_PROFILE in src
    assert MOCK_UBUNTU_PROFILE in src


def test_incorrect_hash_fails_safely(profile_scoped_info):
    """Test that providing the exact approved profile but mathematically diverged hash yields standard failure."""
    ok, expected, src = evaluate_hash("psi", "wrong_hash_000", profile_scoped_info, MOCK_WINDOWS_PROFILE)
    assert ok is False
    assert expected == VALID_WINDOWS_HASH
    assert f"Profile ({MOCK_WINDOWS_PROFILE})" in src


def test_legacy_schema_behavior_is_explicit(legacy_scoped_info):
    """Test that the policy perfectly supports the standard legacy 'psi_hash' string fallback."""
    ok, expected, src = evaluate_hash("psi", "legacy_string_hash_789", legacy_scoped_info, MOCK_WINDOWS_PROFILE)
    assert ok is True
    assert expected == "legacy_string_hash_789"
    assert "Legacy Single-Hash" in src


def test_legacy_schema_incorrect_hash_fails(legacy_scoped_info):
    """Test legacy schema failure path enforces strict strict hash verification."""
    ok, expected, src = evaluate_hash("psi", "wrong_hash", legacy_scoped_info, MOCK_WINDOWS_PROFILE)
    assert ok is False
    assert expected == "legacy_string_hash_789"


def test_missing_profile_entry_fails_clearly():
    """Test that a malformed manifest structure missing both dictionary keys entirely fails gracefully."""
    malformed_info = {
        "step": 200
        # Neither psi_hashes nor psi_hash are present
    }
    ok, expected, src = evaluate_hash("psi", "any_hash", malformed_info, MOCK_WINDOWS_PROFILE)
    assert ok is False
    assert expected == "N/A"
    assert "Missing Schema Keys" in src


def test_strict_manifest_json_file_schema():
    """Reads the actual reference_manifest_spec6_false_s41.json and verifies its execution profile coverage."""
    manifest_path = os.path.join(repo_root, "portal", "src", "lib", "data", "docs", "reference_manifest_spec6_false_s41.json")
    assert os.path.exists(manifest_path), "Canonical manifest JSON file must permanently exist."
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    assert manifest["metadata"]["schema_version"] == "1.1.0", "Manifest must formally denote 1.1.0 execution profile schema."
    snapshots = manifest["snapshots"]
    
    for key, info in snapshots.items():
        assert "psi_hashes" in info, f"Snapshot {key} structurally missing 'psi_hashes' dict schema"
        assert "phi_hashes" in info, f"Snapshot {key} structurally missing 'phi_hashes' dict schema"
        
        # Verify both local and CI execution profiles are rigorously registered
        assert "win32_AMD64_py3.11_np1.25.2_openblas" in info["psi_hashes"], f"Windows Execution Profile missing from {key}"
        assert "linux_x86_64_py3.11_np1.26.4_openblas" in info["psi_hashes"], f"Ubuntu CI Execution Profile missing from {key}"
        assert "win32_AMD64_py3.11_np1.25.2_openblas" in info["phi_hashes"], f"Windows Execution Profile missing from {key}"
        assert "linux_x86_64_py3.11_np1.26.4_openblas" in info["phi_hashes"], f"Ubuntu CI Execution Profile missing from {key}"
