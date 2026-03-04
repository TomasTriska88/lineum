import requests
import json
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

BASE_URL = "http://127.0.0.1:8001"
ENTITY_ID = "test-entity-memory-api"

def test_imprints_api():
    print(f"--- Testing Imprints API on {BASE_URL} ---")
    
    # 1. Wake the entity
    print(f"1. Waking entity {ENTITY_ID}...")
    resp = requests.post(f"{BASE_URL}/entity/wake", json={"entity_id": ENTITY_ID, "grid_size": 64})
    resp.raise_for_status()
    
    # Wait for dream loop to digest
    time.sleep(1)
    
    # We need a way to burn an imprint to test the list.
    # Currently TextToWaveEncoder does identity_burn, but API `chat` doesn't expose it easily.
    # We can use the text_to_wave_encoder to just burn one manually into the artifacts folder, 
    # then test the GET API.
    
    from routing_backend.text_to_wave_encoder import TextToWaveEncoder
    from lineum_core.math import Eq4Config, step_eq4
    
    print("2. Burning a test memory imprint natively...")
    encoder = TextToWaveEncoder(grid_size=64, plasticity_tau=200)
    import numpy as np
    def init_state(grid_size=64):
        return {
            "psi": np.zeros((grid_size, grid_size), dtype=np.complex128),
            "phi": np.full((grid_size, grid_size), 10000.0, dtype=np.float32),
            "kappa": np.full((grid_size, grid_size), 0.5, dtype=np.float32),
            "delta": np.zeros((grid_size, grid_size), dtype=np.float32),
            "mu": np.zeros((grid_size, grid_size), dtype=np.float32)
        }
    state = init_state(64)
    encoder.set_baseline(state)
    
    state_after, metrics = encoder.encode(
        text="The REST API explicitly verifies memory imprints.", 
        state=state, 
        cfg=Eq4Config(dt=1.0, use_mu=True, mu_peak_cutoff_ratio=0.1),
        step_fn=step_eq4, 
        mode="identity_burn"
    )
    
    imprint_id = metrics.get("memory_imprint")
    print(f"   -> Burned imprint ID: {imprint_id}")
    
    # 3. List imprints
    print("3. Fetching list of imprints via HTTP GET...")
    resp = requests.get(f"{BASE_URL}/entity/{ENTITY_ID}/memory/imprints")
    if resp.status_code != 200:
        print(f"GET Failed: {resp.text}")
    resp.raise_for_status()
    
    data = resp.json()
    assert data["status"] == "success", "Failed GET status"
    imprints = data["imprints"]
    
    found = False
    for imp in imprints:
        if imp.get("imprint_id") == imprint_id:
            found = True
            print("   -> Imprint successfully present in REST response.")
            break
            
    assert found, "Imprint was not found in API response."
    
    # 4. Forget imprint via API
    print("4. Forgetting the imprint via HTTP DELETE...")
    resp = requests.delete(f"{BASE_URL}/entity/{ENTITY_ID}/memory/imprints/{imprint_id}")
    if resp.status_code != 200:
        print(f"DELETE Failed: {resp.text}")
    resp.raise_for_status()
    print("   -> Forget HTTP success.")
    
    # 5. Verify it is gone
    print("5. Verifying imprint is no longer listed...")
    resp = requests.get(f"{BASE_URL}/entity/{ENTITY_ID}/memory/imprints")
    resp.raise_for_status()
    
    imprints_after = resp.json()["imprints"]
    for imp in imprints_after:
        assert imp.get("imprint_id") != imprint_id, "Imprint still present after forget!"
        
    print("   -> Verification passed.")
    print("--- Memory API Contract Tests Succeeded! ---")

if __name__ == "__main__":
    test_imprints_api()
