import requests
import json
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

BASE_URL = "http://127.0.0.1:8000"
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

def test_fallback_mood_damp():
    print(f"\n--- Testing Fallback Mood Damping on {BASE_URL} ---")
    
    print(f"1. Waking entity {ENTITY_ID}...")
    resp = requests.post(f"{BASE_URL}/entity/wake", json={"entity_id": ENTITY_ID, "grid_size": 64})
    resp.raise_for_status()
    time.sleep(1)
    
    print("2. Pushing legitimate scientific query to elevate arousal...")
    payload_valid = {"message": "Tlak v rezonátoru extrémně stoupá, hrozí kolaps!", "mode": "runtime"}
    resp = requests.post(f"{BASE_URL}/entity/{ENTITY_ID}/chat", json=payload_valid)
    res_data = resp.json()
    if "metrics" not in res_data:
        print(f"FATAL API ERROR:\n{resp.text}")
        assert False, "API did not return metrics dict."
        
    metrics_valid = res_data["metrics"]
    mood_valid = metrics_valid["affect_v1"]["mood_state"]["after"]
    print(f"   -> Legitimate Mood Arousal: {mood_valid['arousal']:.4f}")
    assert mood_valid['arousal'] > 0.01, "Arousal did not elevate on valid query."
    
    print("3. Spamming out-of-scope fallback queries...")
    payload_fallback = {"message": "Co je to láska a proč mě bolí srdce?", "mode": "runtime"}
    
    for i in range(3):
        resp = requests.post(f"{BASE_URL}/entity/{ENTITY_ID}/chat", json=payload_fallback)
        res_data = resp.json()
        assert res_data["fallback_engaged"] is True, f"Fallback failed to engage on attempt {i}!"
        
        mood_fallback = res_data["metrics"]["affect_v1"]["mood_state"]["after"]
        print(f"   -> Fallback {i} Mood Arousal damped to: {mood_fallback['arousal']:.6f}")
        
        # It should structurally crush the mood by 0.1 each time
        assert mood_fallback['arousal'] < mood_valid['arousal'], "Mood did not dampen during fallback!"

    print("   -> Success: Adversarial queries consistently crushed the mood state instead of inflating it.")

if __name__ == "__main__":
    test_fallback_mood_damp()
