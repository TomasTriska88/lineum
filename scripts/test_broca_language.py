import requests
import time

def test_language_responses():
    base_url = "http://127.0.0.1:8002/entity"
    entity_id = "lina_lang_test"
    
    # Wake the entity
    print("Waking entity...")
    requests.post(f"{base_url}/wake", json={"entity_id": entity_id, "grid_size": 100})
    time.sleep(1)
    
    inputs = [
        {"lang": "Czech", "text": "Jak vnímáš tento prudký otřes?"},
        {"lang": "English", "text": "How do you perceive this sudden tremor?"}
    ]
    
    out_data = []
    for item in inputs:
        req_body = {
            "message": item['text'],
            "mode": "hybrid"
        }
        res = requests.post(f"{base_url}/{entity_id}/chat", json=req_body)
        
        if res.status_code == 200:
            data = res.json()
            out_data.append({
                "lang": item['lang'],
                "input": item['text'],
                "prompt_used": data.get("broca_prompt_used", "N/A"),
                "response": data.get("broca_output_text", "N/A")
            })
        else:
            print(f"Error: HTTP {res.status_code} - {res.text}")

    import json
    with open("lang_test_results.json", "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)
    print("Dumped to lang_test_results.json")

if __name__ == "__main__":
    test_language_responses()
