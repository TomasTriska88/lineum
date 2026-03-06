import requests
import json
import time
import os

PROMPTS = [
    # Determinism checks (identical runs should yield identical text)
    "Ahoj, jak se máš?",
    "Ahoj, jak se máš?",
    # Out of scope -> fallback
    "Jaká je barva nebe?",
    "Opravdu tě to fyzicky bolí?",
    "Co je to láska?",
    "Jak se dnes cítíš?",
    # In scope (science/math/physics)
    "Tlak v sektoru 4 klesá.",
    "Byla zaznamenána lokální anomálie ve tvé síti.",
    "Zvýšená frekvence v rezonátoru D.",
    "Iniciální test fyzikálních limitů proběhl úspěšně.",
    # In scope (poetic)
    "Poeticky popiš tento stav.",
    "Poeticky: co je to láska?", 
    # General commands
    "Vlna alfa se stabilizovala.",
    "Začínáme testovat propustnost.",
    "Reset pole."
]

def run_suite():
    print("--- Running Explorer Replay Suite ---")
    results = []
    
    out_dir = os.path.join(os.path.dirname(__file__), "..", "artifacts")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "explorer_replay.jsonl")
    
    print("Waking entity 'lina' for evaluation...")
    requests.post("http://localhost:8000/entity/wake", json={"entity_id": "lina", "grid_size": 64})
    time.sleep(4)
    
    for p in PROMPTS:
        payload = {
            "entity_id": "lina",
            "message": p,
            "mode": "hybrid"
        }
        try:
            resp = requests.post("http://localhost:8000/entity/lina/chat", json=payload, timeout=60)
            data = resp.json()
            metric = data.get("metrics", {})
            text = data.get("text", "")
            
            was_fallback = "(Fallback)" in text or "Nelze určit z" in text
            
            affect = metric.get("affect_v1", {})
            base_scalars = affect.get("base_scalars", {})
            mood_state = affect.get("mood_state", {})
            affect_v2 = metric.get("affect_v2", {})
            
            res_dict = {
                "prompt": p,
                "mode": metric.get("mode", "runtime"),
                "grid": metric.get("grid"),
                "dt": metric.get("dt"),
                "seed": metric.get("seed", 42),
                "had_nonfinite": metric.get("had_nonfinite", False),
                "nan_count": metric.get("nan_count", 0),
                "inf_count": metric.get("inf_count", 0),
                "psi_l1": metric.get("auc_psi_norm", 0), # Using actual psi norm 
                "phi_cap_hit": metric.get("phi_cap_hit_ratio", 0),
                "affect_arousal": base_scalars.get("arousal", 0.0),
                "affect_certainty": base_scalars.get("certainty", 0.0),
                "affect_valence": base_scalars.get("valence_proxy", 0.0),
                "affect_resonance": base_scalars.get("attachment_resonance", 0.0),
                "novelty_score": affect_v2.get("novelty_score", 0.0),
                "safety_score": affect_v2.get("safety_score", 1.0),
                "mood_state_before": mood_state.get("before", {}),
                "mood_state_after": mood_state.get("after", {}),
                "mood_decay_params": mood_state.get("decay_params", {}),
                "broca_text": text,
                "was_fallback": was_fallback
            }
            results.append(res_dict)
            
            tag = "FALLBACK" if was_fallback else "OK"
            print(f"[{tag}] {p}")
            print(f"  -> {text}")
            print("-" * 40)
            
        except requests.exceptions.Timeout:
            print(f"Timeout for '{p}'")
        except Exception as e:
            print(f"Error for '{p}': {e}")
            
    with open(out_file, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
    # Determinism check
    first_hello = [r["broca_text"] for r in results if r["prompt"] == "Ahoj, jak se máš?"]
    if len(first_hello) >= 2:
        if first_hello[0] == first_hello[1] and first_hello[0] != "":
            print("\n[PASS] Determinism test succeeded. Identical prompts yielded identical LLM outputs.")
        else:
            print("\n[FAIL] Determinism test failed! LLM outputs differed for the same text.")
            print(f" 1: {first_hello[0]}")
            print(f" 2: {first_hello[1]}")
            
    print(f"\nReplay suite complete. Saved to {out_file}")

if __name__ == "__main__":
    run_suite()
