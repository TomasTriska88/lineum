import requests
import json

def fetch_runtime_broca_prompt():
    # Wake
    requests.post("http://127.0.0.1:8000/entity/wake", json={"entity_id": "lina_prompt_test", "grid_size": 100})
    
    # Chat in hybrid mode to trigger the LLM payload assembly
    print("Testing 'hybrid' mode to fetch raw LLM prompt...\n")
    r = requests.post("http://127.0.0.1:8000/entity/lina_prompt_test/chat", json={"message": "Ahoj, cítíš ten tlak?", "mode": "hybrid"})
    res = r.json()
    
    if "broca_prompt_used" in res:
        print("=== FINAL RUNTIME PAYLOAD SENT TO LLM ===")
        print(res["broca_prompt_used"])
        print("=========================================\n")
    else:
        print("Failed to capture prompt. API returned:", res)

if __name__ == "__main__":
    fetch_runtime_broca_prompt()
