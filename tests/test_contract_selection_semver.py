import pytest
from tools.whitepaper_contract import select_latest_contract

def test_select_latest_contract_prefers_1_0_18_over_1_0_9():
    candidates = [
        "lineum-core-1.0.9-core.contract.json",
        "lineum-core-1.0.18-core.contract.json"
    ]
    
    # Explicit protection against return to lexicographic sorting
    # Demonstrate that pure sorted() gets it wrong (1.0.9 comes after 1.0.18 lexicographically)
    assert sorted(candidates)[-1] == "lineum-core-1.0.9-core.contract.json", (
        "This assertion ensures we document WHY this test exists: string sorting fails on 1.0.9 vs 1.0.18"
    )
    
    selected = select_latest_contract(candidates)
    assert selected == "lineum-core-1.0.18-core.contract.json", "Should select 1.0.18 based on semver"

def test_select_latest_contract_mixed_order():
    candidates = [
        "lineum-core-1.0.2-core.contract.json",
        "lineum-core-1.0.15-core.contract.json",
        "lineum-core-1.0.9-alpha.contract.json",
        "lineum-core-1.0.18-beta.contract.json"
    ]
    # Mix them up. Note suffix is ignored for version parsing, just compares numbers.
    selected = select_latest_contract(candidates)
    assert selected == "lineum-core-1.0.18-beta.contract.json"

def test_select_latest_contract_invalid_names():
    candidates = [
        "garbage.json",
        "lineum-core-X.Y.Z-core.contract.json",
        "lineum-core-1.0.9-core.contract.json"
    ]
    selected = select_latest_contract(candidates)
    # The valid one should be picked
    assert selected == "lineum-core-1.0.9-core.contract.json"
    
    # All invalid should raise ValueError
    with pytest.raises(ValueError, match="No valid semver contracts found among candidates."):
        select_latest_contract(["garbage.json", "some-other-file.txt"])

def test_select_latest_contract_empty():
    with pytest.raises(ValueError, match="No candidates provided."):
        select_latest_contract([])
