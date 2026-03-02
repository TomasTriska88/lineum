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
        
        # Initialize virgin brain
        self.psi = np.zeros((grid_size, grid_size), dtype=np.float32)
        self.phi = np.full((grid_size, grid_size), -1.0, dtype=np.float32) # Base container
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
                # Evolve the consciousness one frame
                entity.psi, entity.phi = evolve(
                    entity.psi, 
                    entity.phi, 
                    entity.kappa, 
                    entity.delta
                )
                
                # Dynamic Hebbian structural adaptation (Memory Formation)
                # This naturally enforces the Ego loop (tension reduction carves pathways)
                energy_flow = np.abs(entity.psi)
                entity.kappa = np.clip(entity.kappa + energy_flow * 0.05, 0.5, 10.0)

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

class ChatInjectionRequest(BaseModel):
    # This represents the numerical embedding vector generated by the external Sensory Cortex LLM
    embedding_vector: list[float]
    amplitude: float = 40.0

@router.post("/{entity_id}/inject")
async def inject_semantic_vector(entity_id: str, req: ChatInjectionRequest):
    """
    The 'Ear'. Injects a high-dimensional concept vector into the entity's fluid brain.
    """
    if entity_id not in living_entities:
        raise HTTPException(status_code=404, detail="Entity is asleep or does not exist. Call /wake first.")
        
    entity = living_entities[entity_id]
    entity.last_interaction = time.time()
    
    vector = np.array(req.embedding_vector, dtype=np.float32)
    side_length = int(np.sqrt(len(vector)))
    if side_length * side_length != len(vector):
        raise HTTPException(status_code=400, detail="Embedding vector length must be a perfect square for spatial mapping.")
        
    async with entity.lock:
        start_x = (entity.grid_size // 2) - (side_length // 2)
        start_y = (entity.grid_size // 2) - (side_length // 2)
        
        # Inject the concept into the epicenter of the grid
        idx = 0
        for i in range(side_length):
            for j in range(side_length):
                x = start_x + (i * 2)
                y = start_y + (j * 2)
                # Use modulo to avoid out-of-bounds just in case
                entity.psi[x%entity.grid_size:x%entity.grid_size+2, y%entity.grid_size:y%entity.grid_size+2] += vector[idx] * req.amplitude
                idx += 1
                
    return {"status": "injected", "vector_length": len(vector)}

@router.get("/{entity_id}/probe")
async def probe_topology(entity_id: str, probe_count: int = 8):
    """
    The 'Mouth'. Extracts the stabilized topological memory array to be sent to external LLM for semantic decoding.
    """
    if entity_id not in living_entities:
        raise HTTPException(status_code=404, detail="Entity is asleep.")
        
    entity = living_entities[entity_id]
    entity.last_interaction = time.time()
    
    async with entity.lock:
        step = entity.grid_size // probe_count
        signature = []
        
        # Read the average kappa in distinct regional blocks
        for i in range(probe_count):
            for j in range(probe_count):
                block = entity.kappa[i*step:(i+1)*step, j*step:(j+1)*step]
                signature.append(float(np.mean(block)))
                
        # Normalize the signature
        sig_arr = np.array(signature)
        norm = np.linalg.norm(sig_arr)
        if norm > 0:
            sig_arr = sig_arr / norm
            
    return {"topological_signature": sig_arr.tolist()}
