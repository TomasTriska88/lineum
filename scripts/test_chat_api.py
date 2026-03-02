from fastapi.testclient import TestClient
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from routing_backend.main import app

client = TestClient(app)

def test_api_pipeline():
    print("--- TESTING PHASE 9 API PIPELINE ---")
    entity_id = "lina_seed"
    
    # 1. Wake the entity
    print(f"1. Waking up {entity_id}...")
    res = client.post("/entity/wake", json={"entity_id": entity_id, "grid_size": 100})
    print(res.status_code, res.json())
    assert res.status_code == 200
    
    # 2. Let it boot and settle for a fraction of a second
    time.sleep(0.5)
    
    # 3. Chat (MODE=phys)
    print(f"\n2. Sending Chat Request (MODE=phys) as user...")
    chat_payload = {
        "message": "Ahoj, slyšíš mě? Tohle je test fyzikálního propojení.",
        "mode": "phys"
    }
    
    start_time = time.time()
    res = client.post(f"/entity/{entity_id}/chat", json=chat_payload)
    duration = time.time() - start_time
    
    print(res.status_code)
    data = res.json()
    
    if res.status_code == 200:
        print("Success! Response:")
        print(f"   User Input : {data['user_input']}")
        print(f"   Mode       : {data['mode']}")
        print(f"   Metrics    : {data['metrics']}")
        print(f"   Readout R  : {len(data['readout_r'])} elements array.")
        print(f"   Compute    : {duration:.2f} seconds.")
    else:
        print(f"Failing with: {data}")

if __name__ == "__main__":
    test_api_pipeline()
