import json
import os
import unittest
import numpy as np

class TestLabData(unittest.TestCase):
    base_path = r"c:\Users\Tomáš\Documents\GitHub\lineum-core\lab\public\data"
    
    def test_files_exist(self):
        expected_files = [
            "phi_frames.json",
            "trajectories.json",
            "resonance.json",
            "metadata.json",
            "harmonics.json"
        ]
        for f in expected_files:
            path = os.path.join(self.base_path, f)
            with self.subTest(file=f):
                self.assertTrue(os.path.exists(path), f"File {f} is missing from {self.base_path}")

    def test_json_validity(self):
        files = [f for f in os.listdir(self.base_path) if f.endswith(".json")]
        for f in files:
            path = os.path.join(self.base_path, f)
            with self.subTest(file=f):
                try:
                    with open(path, "r", encoding="utf-8") as jf:
                        data = json.load(jf)
                    self.assertIsInstance(data, (dict, list), f"{f} should be a JSON object or array")
                except Exception as e:
                    self.fail(f"Failed to parse {f}: {e}")

    def test_metadata_fields(self):
        path = os.path.join(self.base_path, "metadata.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
            self.assertIn("run_tag", data)
            self.assertIn("birth_frame", data)
            
    def test_phi_metadata(self):
        path = os.path.join(self.base_path, "phi_frames.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
            self.assertIn("metadata", data)
            self.assertIn("frames", data)
            self.assertGreater(len(data["frames"]), 0)

class TestExtractionLogic(unittest.TestCase):
    def test_golden_ratio_constant(self):
        phi = (1 + 5**0.5) / 2
        self.assertAlmostEqual(phi, 1.61803398875)

    def test_spiral_score_calculation(self):
        # Mock trajectory data for a perfect golden spiral
        phi = (1 + 5**0.5) / 2
        golden_b = np.log(phi) / (np.pi / 2)
        theta = np.linspace(0, 10, 50)
        r = 1.0 * np.exp(golden_b * theta)
        
        # Invert to x, y
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        
        # Calculate b
        coeffs = np.polyfit(theta, np.log(r), 1)
        b = coeffs[0]
        
        score = 1 - abs(b - golden_b) / golden_b
        self.assertGreater(score, 0.99)

if __name__ == "__main__":
    unittest.main()
