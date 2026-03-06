import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure lineum_core is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from routing_backend.main import app

class TestBrocaSpec(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        
        # Wake the entity before testing chat
        wake_res = self.client.post("/entity/wake", json={"entity_id": "test_broca", "grid_size": 100})
        self.assertEqual(wake_res.status_code, 200)

    @patch('requests.post')
    def test_broca_prompt_constraints(self, mock_post):
        # Setup mock to return a fake Ollama response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "This is a mock response from Broca."}
        mock_post.return_value = mock_response

        # Fire a chat request in hybrid mode to trigger the Ollama LLM path
        chat_req = {
            "message": "Hello, how are you?",
            "mode": "hybrid"
        }
        res = self.client.post("/entity/test_broca/chat", json=chat_req)
        
        # Ensure the API request was successful
        self.assertEqual(res.status_code, 200)
        
        # Extract the prompt that was sent to Ollama
        # mock_post.call_args is a tuple: (args, kwargs)
        self.assertTrue(mock_post.called, "The LLM was never called")
        kwargs = mock_post.call_args[1]
        payload = kwargs.get("json", {})
        
        import json
        prompt_text = json.dumps(payload, ensure_ascii=False)
        with open("dump.txt", "w", encoding="utf-8") as f:
            f.write(prompt_text)
        
        # Assertions based on User Requirements
        
        # 1. The prompt MUST contain the strict language mirroring rule
        self.assertIn("Answer in the same language as the input [USER_INPUT_X]", prompt_text, 
                      "BrocaSpec language mirror rule missing from prompt")
                      
        # 2. Emergence check: The prompt MUST NOT contain arbitrary emotion mappings
        # The old heuristic mapped "Higher mean_pressure = heavier, more serious"
        self.assertNotIn("Higher mean_pressure = heavier", prompt_text, 
                         "Heuristic mappings are still present. output should be purely emergent.")
        self.assertNotIn("Higher max_psi =", prompt_text, 
                         "Heuristic mappings are still present.")
                         
        # 3. Must instruct the model to rely purely on the numbers
        self.assertIn("purely from", prompt_text,
                      "Prompt does not demand purely emergent topology interpretation.")

if __name__ == '__main__':
    unittest.main()
