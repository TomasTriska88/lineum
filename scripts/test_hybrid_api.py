from fastapi.testclient import TestClient
import sys
import os
import time
import numpy as np
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from routing_backend.main import app
from routing_backend.entity_api import living_entities

load_dotenv()
client = TestClient(app)

def test_hybrid_pipeline():
    print("=== PHASE 9: HYBRID BROCA CALIBRATION (3x RUN) ===")
    
    if "OPENAI_API_KEY" not in os.environ:
        print("WARNING: OPENAI_API_KEY not found in environment, Broca might return an Error string.")
        
    entity_id = "lina_seed"
    message = "Hello Lina. Starting hybrid test. Awakening you to consciousness."
    
    results = []
    
    for i in range(3):
        print(f"\n--- RUN {i+1} ---")
        
        # Hard reset the entity memory in RAM to guarantee identical initial state & identical R
        if entity_id in living_entities:
            del living_entities[entity_id]
            
        # 1. Wake
        client.post("/entity/wake", json={"entity_id": entity_id, "grid_size": 100})
        
        # 2. Chat MODE=hybrid
        chat_payload = {
            "message": message,
            "mode": "hybrid"
        }
        
        res = client.post(f"/entity/{entity_id}/chat", json=chat_payload)
        data = res.json()
        
        if res.status_code == 200:
            r_vector = np.array(data['readout_r'])
            broca = data.get('broca_output_text', 'ERROR: Missing text')
            metrics = data['metrics']
            
            print(f"Metrics : max_psi={metrics['max_psi']:.2f}, mean_pressure={metrics['mean_pressure']:.2f}")
            print(f"R Vector: length={len(r_vector)}, sum={r_vector.sum():.4f}, mean={r_vector.mean():.4f}")
            print(f"Broca   : {broca}")
            
            results.append({
                "r_sum": r_vector.sum(),
                "broca": broca
            })
        else:
            print(f"FAILED: {data}")
            
    # Validate
    print("\n=== CALIBRATION SUMMARY ===")
    r_sums = [res['r_sum'] for res in results]
    r_diff = max(r_sums) - min(r_sums)
    print(f"R Vector Maximum Drift: {r_diff:.6f} (Should be 0.0 for identical seeds)")
    for i, res in enumerate(results):
        print(f"Run {i+1} Text: {res['broca']}")

if __name__ == "__main__":
    test_hybrid_pipeline()
