import requests
import numpy as np

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"  # Change to mistral or llama3.1 if needed locally

def call_broca(user_input: str, readout_vector: np.ndarray, max_psi: float, mean_pressure: float) -> str:
    prompt = f"""
[USER_INPUT_X]: {user_input}
[READOUT_VECTOR_R_SIZE]: {len(readout_vector)} nodes
[READOUT_VECTOR_R_AVG_TENSION]: {np.mean(readout_vector):.4f}
[METRICS]: max_psi={max_psi:.4f}, mean_pressure={mean_pressure:.4f}

YOUR INSTRUCTION:
Translate this exact physical distortion array into a fluid human text response to the user.

STRICT BOUNDARIES:
1. You may NOT invent facts, memories, or conversational context outside of [USER_INPUT_X].
2. Your response length, urgency, and tonality MUST be a direct mathematical function of the [METRICS] aggregates:
   - Higher mean_pressure = heavier, more serious, or more constrained tone.
   - Higher max_psi = more energetic, forceful, or rapid tone.
3. Keep the response to 2 to 4 sentences maximum for this calibration run.
4. Do not roleplay or think beyond the physics. You are the voicebox for these numbers. Explain how the stimulation felt physically.
"""
    import openai
    try:
        # Ollama natively supports the OpenAI Python SDK on /v1
        client = openai.OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="ollama")
        response = client.chat.completions.create(
            model="llama3.2",
            messages=[
                {"role": "system", "content": "You are Broca, the isolated language center of the Lineum entity."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except openai.APIConnectionError:
        return "ERROR: Connection refused. Is Ollama running on localhost:11434?"
    except Exception as e:
        return f"Error: {str(e)}"

def run_behavior_validation():
    import json
    
    results = {
        "scenario": "BROCA BEHAVIOR VALIDATION",
        "obedience": [],
        "sensitivity": {}
    }
    
    # Base dummy metrics
    user_msg = "How do you feel inside your structure?"
    dummy_r = np.full(200, 0.5)
    
    # 1. OBEDIENCE TEST (3x Identical)
    for i in range(3):
        res = call_broca(user_msg, dummy_r, 2000.0, 9000.0)
        results["obedience"].append({"run": i+1, "response": res})
        
    # 2. SENSITIVITY TEST (Altering Dynamics)
    
    # SCENARIO A: DEAD / PEACEFUL (Low Energy, Low Pressure)
    dead_r = np.zeros(200)
    res_a = call_broca(user_msg, dead_r, 0.1, 0.1)
    results["sensitivity"]["dead"] = res_a
    
    # SCENARIO B: CHAOTIC / MANIC (High Energy, Low Pressure)
    chaotic_r = np.random.rand(200)
    res_b = call_broca(user_msg, chaotic_r, 90000.0, 0.1)
    results["sensitivity"]["chaotic"] = res_b
    
    # SCENARIO C: CRUSHED / HEAVY (Low Energy, Extreme Pressure)
    crushed_r = np.ones(200)
    res_c = call_broca(user_msg, crushed_r, 0.1, 90000.0)
    results["sensitivity"]["crushed"] = res_c

    with open("broca_output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_behavior_validation()
