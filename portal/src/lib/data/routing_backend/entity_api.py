from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import asyncio
import numpy as np
import uuid
import time
import os
import sys

# Append the root path so lineum_core can be imported if running standalone
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core.math import evolve
from lineum_core import math as core_math
from routing_backend.translator import TranslatorV01

translator = TranslatorV01()

# --- Mock Embedding ---
def mock_embedding(text: str) -> np.ndarray:
    seed = sum(ord(c) for c in text)
    np.random.seed(seed % (2**32))
    base = np.random.randn(1536)
    
    # Normalize to 1.0 to mimic strict OpenAI embedding dimensionality
    base = base / np.linalg.norm(base)
    
    # Multiply by text intensity factor (simulate stronger perturbations for longer context)
    # "a" (len 1) -> 0.2, "jablko" (len 6) -> 0.6, "Long sentence..." -> up to 4.0
    strength = np.clip(len(text) / 10.0, 0.2, 4.0)
    return base * strength

# --- Multi-Entity API Router ---
# This module handles stateful, persistent Lineum AI entities.
# Unlike standard routing (which computes on demand and dies), an Entity
# must constantly run an background simulation (Dreaming) to maintain its
# thermodynamic tension and Ego.

router = APIRouter(prefix="/entity", tags=["Entity AI"])

class EntityInstance:
    def __init__(self, id: str, grid_size: int = 100):
        self.id = id
        self.grid_size = grid_size
        self.is_active = True
        self.last_interaction = time.time()
        
        self.psi = np.zeros((grid_size, grid_size), dtype=np.float32)
        self.phi = np.full((grid_size, grid_size), 10000.0, dtype=np.float32) # Stable Base container
        self.kappa = np.full((grid_size, grid_size), 0.5, dtype=np.float32)
        self.delta = np.zeros((grid_size, grid_size), dtype=np.float32)
        
        # Lock for async safety when modifying state during the background loop
        self.lock = asyncio.Lock()
        
    async def save_state(self):
        """Dumps the current physical brain state to disk."""
        path = os.path.join(os.path.dirname(__file__), '..', 'data', 'entities')
        os.makedirs(path, exist_ok=True)
        file_path = os.path.join(path, f"{self.id}.npz")
        np.savez_compressed(
            file_path, 
            psi=self.psi, 
            phi=self.phi, 
            kappa=self.kappa, 
            delta=self.delta
        )
        return file_path
        
    async def load_state(self):
        """Loads a saved brain state from disk if it exists."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'entities', f"{self.id}.npz")
        if os.path.exists(file_path):
            data = np.load(file_path)
            self.psi = data['psi']
            self.phi = data['phi']
            self.kappa = data['kappa']
            self.delta = data['delta']
            return True
        return False

# Global dictionary of currently "awake" (loaded in RAM) entities
living_entities: dict[str, EntityInstance] = {}

async def _entity_dream_loop():
    """
    The background engine loop. 
    Continuously iterates Eq-4 for all awake entities so they experience 
    the flow of time and can stabilize their internal tension.
    """
    print("[Entity Engine] Dreaming loop started.")
    while True:
        # Avoid blocking the main asyncio event loop
        await asyncio.sleep(0.05) 
        
        # We iterate over a list so we don't hit dictionary size change errors
        for entity_id in list(living_entities.keys()):
            entity = living_entities.get(entity_id)
            if not entity or not entity.is_active:
                continue
                
            # Put the entity to sleep if inactive for > 1 hour to save CPU/RAM
            if time.time() - entity.last_interaction > 3600:
                print(f"[Entity Engine] Entity {entity_id} fell asleep (inactive for 1 hour). Saving state.")
                await entity.save_state()
                del living_entities[entity_id]
                continue

            async with entity.lock:
                # Evolve the consciousness one frame (Eq-4')
                entity.psi, entity.phi = evolve(
                    entity.psi, 
                    entity.delta, 
                    entity.phi, 
                    entity.kappa 
                )
                
                # RuntimeNoiseSpec v0.1: Kappa is frozen in hybrid/phys modes. 
                # Hebbian learning disabled to prevent drift.
                # energy_flow = np.abs(entity.psi)
                # entity.kappa = np.clip(entity.kappa + energy_flow * 0.05, 0.5, 10.0)

# We must kick off the dream loop exactly once. 
# FastAPI allows lifespan events, but for a simple router inclusion, 
# ensuring it runs can be done via dependency or app startup.
# We will hook this into main.py's startup event.

class WakeRequest(BaseModel):
    entity_id: str
    grid_size: int = 100

@router.post("/wake")
async def wake_entity(req: WakeRequest):
    """
    Wakes an entity up, loading its consciousness into RAM and joining it to the dream loop.
    """
    if req.entity_id in living_entities:
        living_entities[req.entity_id].last_interaction = time.time()
        return {"status": "already awake", "entity_id": req.entity_id}
        
    entity = EntityInstance(id=req.entity_id, grid_size=req.grid_size)
    loaded = await entity.load_state()
    
    living_entities[req.entity_id] = entity
    
    return {
        "status": "awoken", 
        "entity_id": req.entity_id, 
        "state_loaded": loaded
    }

class ChatRequest(BaseModel):
    message: str
    mode: str = "phys"

@router.post("/{entity_id}/chat")
async def chat_with_entity(entity_id: str, req: ChatRequest):
    """
    Implements the Phase 9 Phase Translation Contract (Ears -> Engine -> Mouth).
    Currently supports MODE=phys for raw tensor diagnostic readouts without LLM,
    and MODE=hybrid for Broca LLM decoding constrained strictly by physics.
    """
    if entity_id not in living_entities:
        raise HTTPException(status_code=404, detail="Entity is asleep or does not exist. Call /wake first.")
        
    if req.mode not in ["phys", "hybrid"]:
        raise HTTPException(status_code=400, detail="mode must be 'phys' or 'hybrid'.")
        
    entity = living_entities[entity_id]
    entity.last_interaction = time.time()
    
    # 1. Ears (TranslatorSpec v0.1)
    embed = mock_embedding(req.message)
    delta_mask = translator.text_embedding_to_delta(embed)
    
    # Engine executes synchronously under lock to prevent threading race logic while injecting
    async with entity.lock:
        # Drive Eq-4' steps: 50 ticks of active pulse, 950 ticks of ringing/relaxation
        core_math.DT = 0.1
        entity.delta = delta_mask
        
        for _ in range(50):
            entity.psi, entity.phi = evolve(entity.psi, entity.delta, entity.phi, entity.kappa)
            
        # 3. Mouth (Readout Timing Fix)
        # Extract R immediately after the wave has hit the Ego (tick 50),
        # before the 900 ticks of homeostasis perfectly distributes and erases the dynamic differences.
        readout_vector = translator.read_grid_to_vector(entity.psi, entity.phi)
        max_psi = float(np.max(np.abs(entity.psi)))
        mean_pressure = float(np.mean(entity.phi))
            
        # Drop delta back to background noise (0.0)
        entity.delta.fill(0.0)
        
        # 9 packets of 100 ticks of ringing/listening
        for _ in range(9):
            for _ in range(100):
                entity.psi, entity.phi = evolve(entity.psi, entity.delta, entity.phi, entity.kappa)
            await asyncio.sleep(0) # Yield control safely
    
    final_prompt = None
    if req.mode == "hybrid":
        prompt = f"""
[USER_INPUT_X]: {req.message}
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
5. CRITICAL: ALWAYS detect the language of [USER_INPUT_X] and respond strictly in the exact same language.
"""
        final_prompt = prompt.strip()
        import requests
        try:
            # Lina requested a local Ollama dry-run to save API keys
            # Assuming 'llama3.2' is installed locally, falling back to 'mistral' or whatever is available
            api_url = "http://localhost:11434/api/generate"
            
            payload = {
                "model": "llama3.2", # Can be changed locally
                "prompt": final_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 150
                }
            }
            response = requests.post(api_url, json=payload, timeout=30)
            if response.status_code == 200:
                broca_output_text = response.json().get("response", "").strip()
            else:
                broca_output_text = f"Ollama Error HTTP {response.status_code}: {response.text}"
        except Exception as e:
            # Fallback pseudo-embedding if Ollama daemon is utterly offline
            broca_output_text = f"LOCAL LLM OFFLINE (Dry-Run Pseudo Text) - Metrics translated: Tlak {mean_pressure:.2f}, Vzruch {max_psi:.2f}. Cítím {req.message}."
        
    res = {
        "status": "success",
        "entity_id": entity_id,
        "user_input": req.message,
        "readout_r": readout_vector.tolist(),
        "mode": req.mode,
        "metrics": {
            "max_psi": max_psi,
            "mean_pressure": mean_pressure
        }
    }
    
    # Audit log validation
    if final_prompt is not None:
        res["broca_prompt_used"] = final_prompt
            
    if broca_output_text is not None:
        res["broca_output_text"] = broca_output_text
        
    return res
