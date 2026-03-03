import numpy as np

def generate_hybrid_payload(message, max_psi, mean_pressure, readout_vector):
    # This is a direct copy of the exact prompt block functioning inside 
    # entity_api.chat_with_entity currently.
    prompt = f"""
[USER_INPUT_X]: {message}
[READOUT_VECTOR_R_SIZE]: {len(readout_vector)} nodes
[READOUT_VECTOR_R_AVG_TENSION]: {np.mean(readout_vector):.4f}
[METRICS]: max_psi={max_psi:.4f}, mean_pressure={mean_pressure:.4f}

YOUR INSTRUCTION:
Translate this exact physical distortion array into a fluid human text response to the user.

STRICT BOUNDARIES:
1. You may NOT invent facts, memories, or conversational context outside of [USER_INPUT_X].
2. The fundamental tone, length, and structure of your response must emerge purely from the numerical relationships in the Readout vector and Metrics. Do NOT use any pre-programmed mappings between numbers and emotions.
3. Keep the response to 2 to 4 sentences maximum for this calibration run.
4. Do not roleplay or think beyond the physics. You are the voicebox for these numbers. Explain how the stimulation felt physically.
5. Answer in the same language as the input [USER_INPUT_X].
"""
    final_prompt = prompt.strip()
    return final_prompt

if __name__ == "__main__":
    dummy_r = [0.5] * 200
    p = generate_hybrid_payload("TEST VSTUP", 3000.0, 10000.0, dummy_r)
    print("=== DUMP OF RUNTIME LLM PROMPT ===")
    print(p)
    print("==================================")
