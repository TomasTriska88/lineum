import sys
import os
import json
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from routing_backend.main import app

def test_language_responses():
    client = TestClient(app)
    entity_id = "lina_lang_test"
    
    print("Waking entity...")
    client.post("/entity/wake", json={"entity_id": entity_id, "grid_size": 100})
    
    inputs = [
        {"lang": "Czech", "text": "How do you perceive this sudden shock?"},
        {"lang": "English", "text": "How do you perceive this sudden tremor?"}
    ]
    
    out_data = []
    # Mocking the LLM is needed so it doesn't actually hit Ollama which might be down
    from unittest.mock import patch, MagicMock
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": {"content": "Mocked response."}}
        mock_post.return_value = mock_response

        for item in inputs:
            req_body = {
                "message": item['text'],
                "mode": "hybrid"
            }
            res = client.post(f"/entity/{entity_id}/chat", json=req_body)
            
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

    with open("lang_test_results.json", "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)
    print("Dumped to lang_test_results.json")

if __name__ == "__main__":
    test_language_responses()
