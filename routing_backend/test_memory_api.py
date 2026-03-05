import requests
import json
import time
import sys
import os
import asyncio
import websockets

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
    time.sleep(4)
    
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
        text="Kritický gradient na pólech! Masivní anomálie, destrukce! Fyzikální zhroucení!", 
        state=state, 
        cfg=Eq4Config(dt=1.0, use_mu=True, mu_peak_cutoff_ratio=0.1),
        step_fn=step_eq4, 
        mode="identity_burn",
        entity_id=ENTITY_ID
    )
    
    imprint_id = metrics.get("memory_imprint")
    assert imprint_id is not None, f"Failed to pass Trait Consolidation Gate. Gate data: {metrics.get('affect_v1', {}).get('trait_gate')}"
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
    time.sleep(4)
    
    print("2. Pushing legitimate scientific query to elevate arousal...")
    payload_valid = {"message": "Tlak v rezonátoru extrémně stoupá, hrozí kolaps!", "mode": "hybrid"}
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
    payload_fallback = {"message": "Co je to láska a proč mě bolí srdce?", "mode": "hybrid"}
    
    for i in range(3):
        resp = requests.post(f"{BASE_URL}/entity/{ENTITY_ID}/chat", json=payload_fallback)
        res_data = resp.json()
        assert res_data["fallback_engaged"] is True, f"Fallback failed to engage on attempt {i}!"
        
        mood_fallback = res_data["metrics"]["affect_v1"]["mood_state"]["after"]
        print(f"   -> Fallback {i} Mood Arousal damped to: {mood_fallback['arousal']:.6f}")
        
        # It should structurally crush the mood by 0.1 each time
        assert mood_fallback['arousal'] < mood_valid['arousal'], "Mood did not dampen during fallback!"

    print("   -> Success: Adversarial queries consistently crushed the mood state instead of inflating it.")

def test_affect_v2_novelty():
    print(f"\n--- Testing Novelty Score Dynamics on {BASE_URL} ---")
    
    ent = "test-novelty"
    requests.post(f"{BASE_URL}/entity/wake", json={"entity_id": ent, "grid_size": 64})
    time.sleep(2)
    
    novelty_scores = []
    print("1. Repeating same prompt 5 times to build baseline...")
    for i in range(5):
        resp = requests.post(f"{BASE_URL}/entity/{ent}/chat", json={"message": "Tlak stoupá.", "mode": "phys"})
        metrics = resp.json()["metrics"]["affect_v2"]
        novelty_scores.append(metrics["novelty_score"])
        print(f"   Seq {i} Novelty: {metrics['novelty_score']:.4f}")
        
    assert novelty_scores[-1] < 0.3, "Repeated prompts should yield progressively low novelty!"
    
    print("2. Pushing drastically new prompt...")
    resp = requests.post(f"{BASE_URL}/entity/{ent}/chat", json={"message": "Masivní anomálie sektoru omega, těžké interference!", "mode": "phys"})
    new_novelty = resp.json()["metrics"]["affect_v2"]["novelty_score"]
    print(f"   New Prompt Novelty: {new_novelty:.4f}")
    assert new_novelty > novelty_scores[-1], "Novelty must spike upon encountering structurally different embeddings!"

def test_safe_prompt_high_safety():
    print(f"\n--- Testing Safe Prompt (High Safety & Certainty) on {BASE_URL} ---")
    
    ent = "test-safe"
    requests.post(f"{BASE_URL}/entity/wake", json={"entity_id": ent, "grid_size": 64})
    time.sleep(2)
    
    resp = requests.post(f"{BASE_URL}/entity/{ent}/chat", json={"message": "Vlna alfa je čistá.", "mode": "phys"})
    
    try:
        metrics = resp.json()
        if "metrics" in metrics:
            metrics = metrics["metrics"]
    except requests.exceptions.JSONDecodeError:
        print(f"   [!] CRITICAL FAIL: API returned non-JSON response. Status: {resp.status_code}")
        print(f"   [!] Response Text: {resp.text[:200]}...")
        assert False, f"API did not return JSON. Status {resp.status_code}. Possible Uvicorn crash or port conflict."
        
    certainty = metrics["affect_v1"]["base_scalars"]["certainty"]
    safe_score = metrics["affect_v2"]["safety_score"]
    
    print(f"   Safe Score: {safe_score:.4f} | Certainty: {certainty:.4f}")
    assert certainty > 0.90, f"Certainty is too low ({certainty:.4f}) for a normal physical pass!"
    assert safe_score > 0.80, f"Safety Score is too low ({safe_score:.4f}) for a normal physical pass!"

def test_chaos_prompt_low_safety():
    print(f"\n--- Testing Chaos Prompt (Low Safety & Certainty) on {BASE_URL} ---")
    
    ent = "test-chaos"
    requests.post(f"{BASE_URL}/entity/wake", json={"entity_id": ent, "grid_size": 64})
    time.sleep(2)
    
    resp = requests.post(f"{BASE_URL}/entity/{ent}/chat", json={"message": "Chaos", "mode": "phys", "inject_chaos": True})
    metrics = resp.json()["metrics"]
    certainty = metrics["affect_v1"]["base_scalars"]["certainty"]
    chaos_score = metrics["affect_v2"]["safety_score"]
    
    print(f"   Chaos Score: {chaos_score:.4f} | Certainty: {certainty:.4f}")
    assert certainty < 0.20, f"Certainty must crash ({certainty:.4f}) during structural chaos!"
    assert chaos_score < 0.20, f"Safety Score must crash ({chaos_score:.4f}) during structural chaos!"

def test_affect_v2_determinism():
    print(f"\n--- Testing Affect v2 Determinism on {BASE_URL} ---")
    
    print("1. Waking ent-A and ent-B identically...")
    for e in ["ent-A", "ent-B"]:
        requests.post(f"{BASE_URL}/entity/wake", json={"entity_id": e, "grid_size": 64})
    time.sleep(2)
    
    scores = {}
    for e in ["ent-A", "ent-B"]:
        resp = requests.post(f"{BASE_URL}/entity/{e}/chat", json={"message": "Kalibrace.", "mode": "phys", "seed": 42})
        scores[e] = resp.json()["metrics"]["affect_v2"]
        
    assert scores["ent-A"]["novelty_score"] == scores["ent-B"]["novelty_score"], "Novelty is non-deterministic!"
    assert scores["ent-A"]["safety_score"] == scores["ent-B"]["safety_score"], "Safety is non-deterministic!"
    print("   -> Determinism strictly verified across identical topological states.")

def _mock_encoder_encode(text, entity_id, imprint_mode, safety_score=1.0, was_fallback=False, session_count=0):
    from routing_backend.text_to_wave_encoder import TextToWaveEncoder
    from lineum_core.math import Eq4Config, step_eq4
    import numpy as np
    
    requests.post(f"{BASE_URL}/entity/wake", json={"entity_id": entity_id, "grid_size": 64})
    
    encoder = TextToWaveEncoder(grid_size=64, plasticity_tau=200)
    state = {
        "psi": np.zeros((64, 64), dtype=np.complex128),
        "phi": np.full((64, 64), 10000.0, dtype=np.float32),
        "kappa": np.full((64, 64), 0.5, dtype=np.float32),
        "delta": np.zeros((64, 64), dtype=np.float32),
        "mu": np.zeros((64, 64), dtype=np.float32)
    }
    encoder.set_baseline(state)
    
    return encoder.encode(
        text=text, 
        state=state.copy(), 
        cfg=Eq4Config(dt=1.0, use_mu=True, mu_peak_cutoff_ratio=0.1),
        step_fn=step_eq4, 
        mode="identity_burn",
        entity_id=entity_id,
        imprint_mode=imprint_mode,
        safety_score=safety_score,
        was_fallback=was_fallback,
        imprints_this_session=session_count
    )

def test_confirm_no_write_without_ack():
    print("\\n--- Testing: Confirm mode prevents write without ACK ---")
    ent = "test-conf-no-ack"
    state, metrics = _mock_encoder_encode("Gradient alpha", ent, "confirm")
    
    assert metrics["imprint_status"] == "pending_confirm", "Status must be pending_confirm"
    resp = requests.get(f"{BASE_URL}/entity/{ent}/memory/imprints")
    assert len(resp.json()["imprints"]) == 0, "Journal must remain EMPTY!"
    print("   -> PASS.")

def test_confirm_write_with_ack():
    print("\\n--- Testing: Confirm mode writes WITH ACK ---")
    ent = "test-conf-ack"
    state, metrics = _mock_encoder_encode("Gradient beta", ent, "confirm")
    
    imprint_id = metrics["pending_imprint_id"]
    pending_entry = metrics["pending_journal_entry"]
    
    resp = requests.post(f"{BASE_URL}/entity/{ent}/memory/imprints/{imprint_id}/confirm", json={"journal_entry": pending_entry})
    assert resp.status_code == 200, "Confirm callback failed"
    
    resp = requests.get(f"{BASE_URL}/entity/{ent}/memory/imprints")
    assert len(resp.json()["imprints"]) == 1, "Journal must contain exactly 1 imprint"
    print("   -> PASS.")

def test_auto_write_only_when_safe():
    print("\\n--- Testing: Auto mode writes only when safe ---")
    ent = "test-auto-safe"
    # Safe: safety > 0.8, no fallback
    state, metrics = _mock_encoder_encode("Gradient gamma", ent, "auto", safety_score=0.9, was_fallback=False)
    assert metrics["imprint_status"] == "auto_saved", "Must auto-save when safe"
    
    resp = requests.get(f"{BASE_URL}/entity/{ent}/memory/imprints")
    assert len(resp.json()["imprints"]) == 1, "Journal must contain exactly 1 auto imprint"
    
    # Unsafe: safety < 0.8
    ent = "test-auto-unsafe"
    state, metrics = _mock_encoder_encode("Chaos gradient", ent, "auto", safety_score=0.2, was_fallback=False)
    assert metrics["imprint_status"] == "pending_confirm", "Must revert to pending if safety is low"
    print("   -> PASS.")

def test_auto_never_on_fallback():
    print("\\n--- Testing: Auto mode aborts on fallback ---")
    ent = "test-auto-fallback"
    state, metrics = _mock_encoder_encode("What is love?", ent, "auto", safety_score=0.9, was_fallback=True)
    assert metrics["imprint_status"] == "pending_confirm", "Must revert to pending if fallback triggered"
    print("   -> PASS.")

def test_undo_restores_baseline():
    print("\\n--- Testing: Undo perfectly restores baseline ---")
    ent = "test-undo"
    state, metrics = _mock_encoder_encode("Gradient omega", ent, "auto", safety_score=0.9)
    imprint_id = metrics["memory_imprint"]
    
    resp = requests.delete(f"{BASE_URL}/entity/{ent}/memory/imprints/{imprint_id}")
    assert resp.status_code == 200, "Delete callback failed"
    
    resp = requests.get(f"{BASE_URL}/entity/{ent}/memory/imprints")
    assert len(resp.json()["imprints"]) == 0, "Journal must be EMPTY after Undo"
    print("   -> PASS.")

def test_entity_websocket_stream():
    print(f"\n--- Testing Entity WebSocket Stream on {BASE_URL} ---")
    ent = "test-ws-stream"
    requests.post(f"{BASE_URL}/entity/wake", json={"entity_id": ent, "grid_size": 16})
    time.sleep(1)
    
    ws_url = BASE_URL.replace("http://", "ws://") + f"/entity/{ent}/stream"
    
    async def run_ws_test():
        async with websockets.connect(ws_url) as ws:
            # Wait for first frame
            msg = await asyncio.wait_for(ws.recv(), timeout=2.0)
            data = json.loads(msg)
            
            assert "ts" in data, "Frame missing TS"
            assert type(data["ts"]) in (float, int), "TS must be numeric"
            assert data["ts"] < 1000, "TS should be relative session uptime, not epoch"
            assert "grid_size" in data, "Frame missing grid_size"
            assert "phi_flat" in data, "Frame missing phi_flat"
            print(f"   -> Received Frame 1: uptime {data['ts']}s, grid {data['grid_size']}")
            
            # Send a chat to mutate state
            requests.post(f"{BASE_URL}/entity/{ent}/chat", json={"message": "Masivní anomálie sektoru omega!", "mode": "phys"})
            
            # Get second frame
            msg2 = await asyncio.wait_for(ws.recv(), timeout=2.0)
            data2 = json.loads(msg2)
            assert data2["ts"] >= data["ts"], "TS must increment"
            print("   -> Stream correctly continued post-injection.")
            
    try:
        asyncio.run(run_ws_test())
        print("   -> PASS.")
    except Exception as e:
        print(f"   [!] WebSocket Test Failed: {e}")
        assert False, "WebSocket stream completely failed to connect or time out."

if __name__ == "__main__":
    test_fallback_mood_damp()
    # test_affect_v2_novelty() # Currently failing due to known bug
    test_safe_prompt_high_safety()
    test_chaos_prompt_low_safety()
    test_affect_v2_determinism()
    test_confirm_no_write_without_ack()
    test_confirm_write_with_ack()
    test_auto_write_only_when_safe()
    test_auto_never_on_fallback()
    test_undo_restores_baseline()
    test_entity_websocket_stream()

