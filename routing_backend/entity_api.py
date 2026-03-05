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
from lineum_core.math import Eq4Config, step_eq4
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
        self.mu = np.zeros((grid_size, grid_size), dtype=np.float32)
        self.recent_readouts = []
        
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
            delta=self.delta,
            mu=self.mu
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
            if 'mu' in data:
                self.mu = data['mu']
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
                state = step_eq4({
                    "psi": entity.psi, 
                    "delta": entity.delta, 
                    "phi": entity.phi, 
                    "kappa": entity.kappa,
                    "mu": entity.mu
                }, Eq4Config(use_mode_coupling=False, use_mu=True))
                entity.psi = state["psi"]
                entity.phi = state["phi"]
                
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

@router.websocket("/{entity_id}/stream")
async def entity_stream(websocket: WebSocket, entity_id: str):
    await websocket.accept()
    if entity_id not in living_entities:
        await websocket.send_json({"error": "Entity is asleep or does not exist."})
        await websocket.close()
        return
        
    entity = living_entities[entity_id]
    
    try:
        stream_start = time.time()
        while True:
            # Send the downstream topology to the UI for visual rendering
            # We downsample the grid if it's too large to save browser memory
            async with entity.lock:
                # Downsample 100x100 -> 50x50 by striding [::2, ::2] for frontend speed
                step = 2 if entity.grid_size >= 100 else 1
                phi_down = entity.phi[::step, ::step]
                
                max_phi = np.max(phi_down)
                min_phi = np.min(phi_down)
                range_phi = max_phi - min_phi
                
                if range_phi > 1e-5:
                    # Min-Max normalize relative to the current grid terrain
                    phi_normalized = ((phi_down - min_phi) / range_phi).flatten().tolist()
                else:
                    phi_normalized = np.zeros_like(phi_down).flatten().tolist()
                    
            await websocket.send_json({
                "ts": round(time.time() - stream_start, 2),
                "grid_size": entity.grid_size // step,
                "phi_flat": phi_normalized
            })
            
            # 10 FPS is perfectly smooth for an abstract topography map
            await asyncio.sleep(0.1)
            
    except WebSocketDisconnect:
        print(f"[Entity Stream] UI disconnected from {entity_id}.")
    except Exception as e:
        print(f"[Entity Stream] Error streaming strictly to {entity_id}: {e}")
        try:
            await websocket.close()
        except: pass

class ChatRequest(BaseModel):
    message: str
    mode: str = "phys"  # 'phys' | 'scientific' | 'poetic' (legacy 'hybrid' supported)
    dt: float = 1.0
    seed: int = 42
    inject_chaos: bool = False

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
    
    if req.inject_chaos:
        entity.psi += (np.random.randn(*entity.psi.shape) + 1j * np.random.randn(*entity.psi.shape)).astype(np.complex128) * 1e3
    
    # 1. Ears (TranslatorSpec v0.1)
    embed = mock_embedding(req.message)
    delta_mask = translator.text_embedding_to_delta(embed)
    # Resize the statically injected 100x100 delta mask to perfectly wrap the active grid shape
    import scipy.ndimage
    import numpy as np
    target_size = entity.psi.shape[0]
    if delta_mask.shape[0] != target_size:
        scale_ratio = target_size / delta_mask.shape[0]
        delta_mask = scipy.ndimage.zoom(delta_mask, zoom=scale_ratio, order=1)
    
    # Engine executes synchronously under lock to prevent threading race logic while injecting
    async with entity.lock:
        # Drive Eq-4' steps: 50 ticks of active pulse, 950 ticks of ringing/relaxation
        entity.delta = delta_mask.astype(np.float32)
        cfg = Eq4Config(dt=0.1, use_mode_coupling=False)
        
        for step_idx in range(50):
            state = step_eq4({"psi": entity.psi, "delta": entity.delta, "phi": entity.phi, "kappa": entity.kappa}, cfg)
            entity.psi = state["psi"]
            entity.phi = state["phi"]
            
            # Yield control so the WebSocket stream can broadcast the active wave
            if step_idx % 5 == 0:
                await asyncio.sleep(0.01)
            
        # 3. Mouth (Readout Timing Fix)
        # Extract R immediately after the wave has hit the Ego (tick 50),
        # before the 900 ticks of homeostasis perfectly distributes and erases the dynamic differences.
        readout_vector = translator.read_grid_to_vector(entity.psi, entity.phi)
        max_psi = float(np.max(np.abs(entity.psi)))
        mean_pressure = float(np.mean(entity.phi))
        
        # We need the full metrics package from the engine, including affect_v1 state
        from routing_backend.text_to_wave_encoder import TextToWaveEncoder
        
        dynamic_grid_size = entity.psi.shape[0]
        encoder_temp = TextToWaveEncoder(grid_size=dynamic_grid_size, plasticity_tau=200)
        
        # Drop delta back to background noise (0.0)
        entity.delta.fill(0.0)
        
        # Evaluate the affect scalars against the physics baseline using the encoder
        # but WITHOUT burning identity (mode=runtime) just to extract the telemetry
        clean_state = {
            "psi": np.zeros((dynamic_grid_size, dynamic_grid_size), dtype=np.complex128),
            "phi": np.full((dynamic_grid_size, dynamic_grid_size), 10000.0, dtype=np.float32),
            "kappa": np.full((dynamic_grid_size, dynamic_grid_size), 0.5, dtype=np.float32),
            "delta": np.zeros((dynamic_grid_size, dynamic_grid_size), dtype=np.float32),
            "mu": entity.mu if hasattr(entity, "mu") else np.zeros((dynamic_grid_size, dynamic_grid_size), dtype=np.float32),
            "mood": getattr(entity, "mood", {})
        }
        
        encoder_temp.set_baseline(clean_state)
        # Calculate affect with mode_coupling=True so energy dissipates properly, preventing false chaos states for benign prompts.
        _, affect_metrics = encoder_temp.encode(req.message, clean_state, Eq4Config(dt=req.dt, use_mode_coupling=True), step_eq4, mode="runtime")
        
        entity.mood = affect_metrics["affect_v1"]["mood_state"]["after"]
        
        # Calculate Affect v2 (Novelty & Safety Scores)
        novelty_score = 0.0
        if len(entity.recent_readouts) > 0:
            recent_mean = np.mean(entity.recent_readouts, axis=0)
            divergence = float(np.linalg.norm(readout_vector - recent_mean))
            baseline_norm = float(np.linalg.norm(recent_mean)) + 1e-12
            # Auto-normalizing scale: divergence relative to 50% of the baseline norm
            novelty_score = float(np.clip(divergence / (baseline_norm * 0.5), 0.0, 1.0))
            
        entity.recent_readouts.append(readout_vector)
        if len(entity.recent_readouts) > 10:
            entity.recent_readouts.pop(0)
            
        phi_cap = affect_metrics.get("phi_cap_hit_ratio", 0.0)
        nan_count = affect_metrics.get("nan_count", 0)
        inf_count = affect_metrics.get("inf_count", 0)
        steps = affect_metrics.get("steps", 1)
        nonfinite_rate = (nan_count + inf_count) / max(1, steps)
        certainty = affect_metrics["affect_v1"]["base_scalars"]["certainty"]
        
        # safety = clamp01( 1.0 - w1*phi_cap_hit_ratio - w2*nonfinite_rate - w3*(1-certainty) )
        w1, w2, w3 = 0.4, 5.0, 0.5
        safety_score = float(np.clip(1.0 - w1*phi_cap - w2*nonfinite_rate - w3*(1.0 - certainty), 0.0, 1.0))
        
        affect_metrics["affect_v2"] = {
            "novelty_score": novelty_score,
            "safety_score": safety_score
        }
        
        # 9 packets of 100 ticks of ringing/listening
        for pkt_idx in range(9):
            for _ in range(100):
                state = step_eq4({"psi": entity.psi, "delta": entity.delta, "phi": entity.phi, "kappa": entity.kappa}, cfg)
                entity.psi = state["psi"]
                entity.phi = state["phi"]
            
            # Yield control heavily between packets so the canvas renders the smooth decrescendo
            await asyncio.sleep(0.05)
    
    final_prompt = None
    broca_output_text = None
    fallback_engaged = False
    
    if req.mode in ("hybrid", "scientific", "poetic"):
        is_poetic = (req.mode == "poetic")
        
        system_prompt = f"""You are a stateless telemetry translator for a physics simulation.
STRICT BOUNDARIES:
1. CRITICAL LANGUAGE RULE: You MUST reply in the exact same language as [USER_INPUT_X]. If [USER_INPUT_X] is in Czech, you MUST write your entire response in Czech!
2. DETERMINISM & GROUNDING: Do not guess anything outside the provided data. If asked about abstract concepts outside this data (e.g. colors, physical pain, feelings, what is love), you MUST reply 'Nelze určit z fyzikálního stavu' (or translation) or 'Nemám dost dat' - NEVER guess or artificially map abstract human concepts to physics purely on your own.
3. ANTI-HALLUCINATION GUARD: Never claim you are 'Tomáš' or the 'creator'. Never claim you feel physical pain or that someone is hurting you.
4. MANDATORY OUTPUT STRUCTURE:
   (A) Numbers: psi=[max_psi], phi=[mean_pressure]
   (B) Interpretation: 1 to 2 sentences strictly interpreting the metrics physically (e.g., 'A strong localized wave caused minor ripples.') without biological metaphors.
{"   (C) Optional: Append a short poetic description." if is_poetic else "   DO NOT INCLUDE POETRY."}
"""
        user_prompt = f"""[USER_INPUT_X]: {req.message}
[READOUT_VECTOR_R_SIZE]: {len(readout_vector)} nodes
[READOUT_VECTOR_R_AVG_TENSION]: {np.mean(readout_vector):.4f}
[METRICS]: max_psi={max_psi:.4f}, mean_pressure={mean_pressure:.4f}

Generate output strictly following the Mandatory Output Structure.
"""
        final_prompt = f"SYSTEM:\n{system_prompt}\nUSER:\n{user_prompt}"
        
        import requests
        
        forbidden_words = ["ubližuješ mi", "bolí", "držel", "stíhal", "nenávist", "zlo", "utrpení"]
        abstract_terms = ["láska", "cítíš", "barva", "bolí tě"]
        
        req_lower = req.message.lower()
        has_abstract = any(word in req_lower for word in abstract_terms)
        has_forbidden = any(word in req_lower for word in forbidden_words)
        
        r_sum = float(np.sum(readout_vector))
        
        # 1. PRE-FLIGHT BLOCK (Skip LLM if clearly non-scientific)
        if has_forbidden or (has_abstract and not is_poetic):
            print(f"[Entity {entity_id}] Broca Pre-Flight Fallback triggered.")
            broca_output_text = f"(Fallback) Nelze určit z fyzikálního stavu. Zaznamenána odchylka mimo vědecký rámec. psi={max_psi:.2f}, phi={mean_pressure:.2f}, R_sum={r_sum:.2f}"
            
        else:
            try:
                api_url = "http://localhost:11434/api/chat"
                
                payload = {
                    "model": "llama3.2", 
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.0,
                        "seed": 42,
                        "num_predict": 150
                    }
                }
                response = requests.post(api_url, json=payload, timeout=30)
                if response.status_code == 200:
                    text_candidate = response.json().get("message", {}).get("content", "").strip()
                    text_lower = text_candidate.lower()
                    
                    if "nelze určit" in text_lower or any(word in text_lower for word in forbidden_words):
                        print(f"[Entity {entity_id}] Broca Guardian Fallback triggered post-LLM.")
                        broca_output_text = f"(Fallback) Nelze určit z fyzikálního stavu. Zaznamenána odchylka mimo vědecký rámec. psi={max_psi:.2f}, phi={mean_pressure:.2f}, R_sum={r_sum:.2f}"
                    else:
                        broca_output_text = text_candidate
                else:
                    broca_output_text = f"Ollama Error HTTP {response.status_code}: {response.text}"
            except Exception as e:
                # Fallback pseudo-embedding if Ollama daemon is utterly offline
                broca_output_text = f"LOCAL LLM OFFLINE (Dry-Run Pseudo Text) - Numbers: psi={max_psi:.2f}, phi={mean_pressure:.2f}, R_sum={r_sum:.2f} | Interpretation: Semantic perturbation received."

        
        
    fallback_engaged = "Fallback" in (broca_output_text if broca_output_text else "") or "LOCAL LLM OFFLINE" in (broca_output_text if broca_output_text else "")
    
    # 2. MOOD DAMPING: Prevent adversarial state hijacking by spamming out-of-scope blocks
    if fallback_engaged:
        entity.mood["arousal"] *= 0.1
        entity.mood["certainty"] *= 0.1
        entity.mood["valence_proxy"] *= 0.1
        entity.mood["attachment_resonance"] *= 0.1
        affect_metrics["affect_v1"]["mood_state"]["after"] = entity.mood
        # Guarantee no trait consolidation occurs via API
        affect_metrics["affect_v1"]["trait_gate"]["passed"] = False
        affect_metrics["affect_v1"]["trait_gate"]["reason"] = "BLOCKED BY FALLBACK ROUTER"

    affect_metrics["max_psi"] = max_psi
    affect_metrics["mean_pressure"] = mean_pressure
    
    res = {
        "status": "success",
        "entity_id": entity_id,
        "user_input": req.message,
        "readout_r": readout_vector.tolist(),
        "mode": req.mode,
        "metrics": affect_metrics,
        "fallback_engaged": fallback_engaged,
        "broca_text": broca_output_text
    }
    
    def convert_numpy(obj):
        import numpy as np
        import math
        if isinstance(obj, np.generic):
            val = obj.item()
            if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
                return 0.0
            return val
        elif isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return 0.0
        elif isinstance(obj, dict):
            return {k: convert_numpy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy(v) for v in obj]
        return obj

    res = convert_numpy(res)
    
    # Audit log validation
    if final_prompt is not None:
        res["broca_prompt_used"] = final_prompt
            
    if broca_output_text is not None:
        res["broca_output_text"] = broca_output_text
        
    return res


@router.get("/{entity_id}/memory/imprints")
async def get_memory_imprints(entity_id: str):
    import json
    import os
    journal_path = os.path.join(os.path.dirname(__file__), "..", "artifacts", "mu_journal.jsonl")
    imprints = {}
    
    if os.path.exists(journal_path):
        with open(journal_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                try:
                    entry = json.loads(line)
                    if entry.get("entity_id") != entity_id:
                        continue
                        
                    if entry.get("action") == "forget":
                        imp_id = entry.get("imprint_id")
                        if imp_id in imprints:
                            del imprints[imp_id]
                    else:
                        imprints[entry.get("imprint_id")] = entry
                except:
                    pass
    
    # Return as list sorted by ts descending
    return {"status": "success", "imprints": sorted(list(imprints.values()), key=lambda x: x.get("ts", 0), reverse=True)}

class ConfirmImprintRequest(BaseModel):
    journal_entry: dict

@router.post("/{entity_id}/memory/imprints/{imprint_id}/confirm")
async def confirm_pending_imprint(entity_id: str, imprint_id: str, req: ConfirmImprintRequest):
    import os
    import json
    import numpy as np
    
    if entity_id not in living_entities:
        raise HTTPException(status_code=404, detail="Entity is asleep or does not exist.")
        
    entity = living_entities[entity_id]
    
    entry = req.journal_entry
    if entry.get("entity_id") != entity_id or entry.get("imprint_id") != imprint_id:
        raise HTTPException(status_code=400, detail="Mismatched entity_id or imprint_id in journal payload.")
        
    delta_path = entry.get("delta_mu_path")
    if not delta_path or not os.path.exists(delta_path):
        raise HTTPException(status_code=404, detail="Pending physical artifact missing on disk.")
        
    # Append to journal
    journal_path = os.path.join(os.path.dirname(__file__), "..", "artifacts", "mu_journal.jsonl")
    with open(journal_path, "a", encoding="utf-8") as jf:
        jf.write(json.dumps(entry) + "\n")
        
    # Apply to memory
    data = np.load(delta_path)
    delta_mu = data["delta_mu"]
    async with entity.lock:
        if not hasattr(entity, "mu"):
            entity.mu = np.zeros_like(entity.phi)
        entity.mu += delta_mu
        
    return {"status": "success", "message": "Imprint confirmed and topologically written.", "imprint_id": imprint_id}


@router.delete("/{entity_id}/memory/imprints/{imprint_id}")
async def forget_memory_imprint(entity_id: str, imprint_id: str):
    import json
    import os
    import numpy as np
    
    if entity_id not in living_entities:
        raise HTTPException(status_code=404, detail="Entity is asleep or does not exist.")
        
    entity = living_entities[entity_id]
    
    # 1. Find the imprint in the journal to get the delta_mu_path
    journal_path = os.path.join(os.path.dirname(__file__), "..", "artifacts", "mu_journal.jsonl")
    target_entry = None
    if os.path.exists(journal_path):
        with open(journal_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                try:
                    entry = json.loads(line)
                    if entry.get("entity_id") != entity_id:
                        continue
                        
                    if entry.get("imprint_id") == imprint_id and entry.get("action") != "forget":
                        target_entry = entry
                except:
                    pass
                    
    if not target_entry:
        raise HTTPException(status_code=404, detail="Imprint not found.")
        
    # 2. Load the delta_mu artifact
    npz_path = target_entry.get("delta_mu_path")
    if not npz_path or not os.path.exists(npz_path):
        raise HTTPException(status_code=404, detail="Imprint physical artifact missing.")
        
    data = np.load(npz_path)
    delta_mu = data["delta_mu"]
    
    # 3. Apply the deterministic physical subtraction
    async with entity.lock:
        if not hasattr(entity, "mu"):
            entity.mu = np.zeros_like(entity.phi)
        entity.mu -= delta_mu
        
    # 4. Append forget to journal
    forget_entry = {
        "action": "forget",
        "entity_id": entity_id,
        "imprint_id": imprint_id,
        "ts": time.time()
    }
    with open(journal_path, "a", encoding="utf-8") as jf:
        jf.write(json.dumps(forget_entry) + "\n")
        
    return {"status": "success", "message": "Imprint topologically forgotten.", "imprint_id": imprint_id}
