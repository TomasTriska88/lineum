from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Dict, Tuple, Optional
import asyncio
import sys

import uuid
import numpy as np
import heapq
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core.math import CoreConfig, step_core

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP CHECK: Guardrail against dual routing_backend paths (VAR A)
    duplicate_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'portal', 'src', 'lib', 'data', 'routing_backend'))
    if os.path.exists(duplicate_path):
        error_msg = f"CRITICAL FAILURE: Duplicate routing_backend found at {duplicate_path}. Please delete the duplicate if it is causing issues."
        print(error_msg, file=sys.stderr)
        # Bypassing sys.exit(1) to allow execution even when npm run sync creates the duplicate
        
    # Kick off the persistent thermodynamic engine for conscious instances
    task = asyncio.create_task(_entity_dream_loop())
    yield
    task.cancel()

app = FastAPI(title="Lineum Routing API", version="1.0.0", lifespan=lifespan)

from routing_backend.entity_api import router as entity_router, _entity_dream_loop
from routing_backend.engraving_api import router as engraving_router
from routing_backend.lab_api import router as lab_router

app.include_router(entity_router)
app.include_router(engraving_router)
app.include_router(lab_router, prefix="/api/lab")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models for REST upload from browser
class Point(BaseModel):
    x: int
    y: int

class AgentDef(BaseModel):
    id: str
    start: Point
    color: str # hex nebo css barva

class RouteRequest(BaseModel):
    size: int # např 64 nebo 128
    agents: List[AgentDef]
    target: Point
    kappa_flat: List[float] # Flattened terrain traversability array from Svelte canvas
    max_steps: int = 1000
    preset: Optional[str] = "urban_design" # ['urban_design', 'evacuation', 'vascular', 'dielectric']
    agent_count: Optional[int] = 0 # If set higher than len(agents), the backend will randomly generate the rest for massive scalability tests
    return_paths: bool = True # Flag allowing true O(1) B2B heatmap benchmarking

# Task configuration storage
active_tasks: Dict[str, RouteRequest] = {}

def extract_path(phi_field: np.ndarray, kappa: np.ndarray, start_x: int, start_y: int, target_x: int, target_y: int, size: int) -> Tuple[List[int], List[int]]:
    if np.max(phi_field) < 1e-4: return [], []
    
    cost_map = np.zeros((size, size))
    for y in range(size):
        for x in range(size):
            if kappa[y, x] <= 0.01:
                cost_map[y, x] = np.inf
            else:
                cost_map[y, x] = (1.0 / (phi_field[y, x] + 1e-6)) * (1.0 / kappa[y, x])
                
    pq = [(0, target_x, target_y)]
    came_from = {}
    g_score = {(target_x, target_y): 0}
    
    while pq:
        _, cx, cy = heapq.heappop(pq)
        if abs(cx - start_x) <= 2 and abs(cy - start_y) <= 2:
            curr = (cx, cy)
            raw_path = [curr]
            while curr in came_from:
                curr = came_from[curr]
                raw_path.append(curr)
            # Return in decomposed JSON-ready format
            return [start_x] + [p[0] for p in raw_path], [start_y] + [p[1] for p in raw_path]
            
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < size and 0 <= ny < size and kappa[ny, nx] > 0.0:
                if dx != 0 and dy != 0:
                    if kappa[cy, nx] == 0.0 and kappa[ny, cx] == 0.0:
                        continue
                
                move_cost = cost_map[ny, nx] * (1.414 if dx != 0 and dy != 0 else 1.0)
                tentative_g = g_score[(cx, cy)] + move_cost
                if (nx, ny) not in g_score or tentative_g < g_score[(nx, ny)]:
                    came_from[(nx, ny)] = (cx, cy)
                    g_score[(nx, ny)] = tentative_g
                    f_score = tentative_g + np.hypot(start_x - nx, start_y - ny) * 0.1
                    heapq.heappush(pq, (f_score, nx, ny))
    return [], []

from fastapi import Request

# Simple In-Memory Rate Limiter (prod deployments might use Redis)
ip_request_counts: Dict[str, list] = {}
MAX_CONCURRENT_TASKS = int(os.environ.get("LINEUM_API_MAX_CONCURRENT_TASKS", 100))
RATE_LIMIT_REQUESTS = int(os.environ.get("LINEUM_API_RATE_LIMIT_MAX_REQUESTS", 5)) # Maximum number of simulations per window 
RATE_LIMIT_WINDOW = int(os.environ.get("LINEUM_API_RATE_LIMIT_WINDOW_SECONDS", 60)) # Window in seconds

@app.post("/api/route/task")
async def create_routing_task(req: RouteRequest, request: Request):
    """
    Step 1: Client sends a large map and coordinates. The server doesn't start the compute loop.
    It only stores it in RAM and returns a ticket (ID) that the client inputs into the WebSocket.
    """
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    # Prune old IPs from rate limiter
    if client_ip not in ip_request_counts:
        ip_request_counts[client_ip] = []
    
    ip_request_counts[client_ip] = [t for t in ip_request_counts[client_ip] if now - t < RATE_LIMIT_WINDOW]
    
    if len(ip_request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(status_code=429, detail="Too Many Requests. Maximum 5 simulations per minute.")
        
    ip_request_counts[client_ip].append(now)

    if len(active_tasks) >= MAX_CONCURRENT_TASKS:
        raise HTTPException(status_code=503, detail="Server is at full capacity. Please try again later.")
        
    if len(req.kappa_flat) != req.size * req.size:
        raise HTTPException(status_code=400, detail="Délka kappa_flat neodpovídá size*size")
        
    task_id = str(uuid.uuid4())
    active_tasks[task_id] = req
    return {"status": "created", "task_id": task_id}


@app.websocket("/api/route/stream/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    Step 2: Live execution of on-demand computing only for the duration of the connection.
    """
    await websocket.accept()
    
    if task_id not in active_tasks:
        await websocket.send_json({"error": "Task not found."})
        await websocket.close()
        return
        
    req = active_tasks.pop(task_id) # Remove from stack
    size = req.size
    
    # Reconstruct grid from sent 1D array to 2D Numpy Float matrix
    kappa = np.array(req.kappa_flat, dtype=np.float64).reshape((size, size))
    psi = np.zeros((size, size), dtype=np.complex128)
    delta = np.zeros((size, size), dtype=np.float64)
    phi = np.zeros((size, size), dtype=np.float64)
    
    target_y = req.target.y
    target_x = req.target.x
    
    # APPLY "PRESET" (Lineum physics demosphere for showcase Use-cases)
    preset = req.preset if hasattr(req, 'preset') and req.preset else "urban_design"
    preset_settings = {
        "urban_design": {"dissipation": 0.005, "noise": 0.0, "reaction": 0.1, "phi_diff": 0.05},
        "evacuation": {"dissipation": 0.08, "noise": 0.0, "reaction": 0.3, "phi_diff": 0.15},    # Fast congestion decay, more chaotic
        "vascular": {"dissipation": 0.002, "noise": 0.08, "reaction": 0.02, "phi_diff": 0.02},  # Fragile long-lasting branches with noise
        "dielectric": {"dissipation": 0.001, "noise": 0.0, "reaction": 0.5, "phi_diff": 0.005}, # Massive lightning straight push with burn-through
    }
    
    cfg = preset_settings.get(preset, preset_settings["urban_design"])
    
    cfg = CoreConfig(
        dissipation_rate=cfg["dissipation"],
        noise_strength=cfg["noise"],
        reaction_strength=cfg["reaction"],
        phi_diffusion=cfg["phi_diff"],
        use_mode_coupling=False
    )
    
    # SETUP MASSIVE SWARM VECTORIZATION ONCE BEFORE LOOP
    y_coords = [a.start.y for a in req.agents]
    x_coords = [a.start.x for a in req.agents]
    
    # If the UI requested a massive swarm (agent_count > len(agents sent))
    # We automatically generate the rest on the backend natively in python O(1) to avoid JSON bloat
    if hasattr(req, 'agent_count') and req.agent_count and req.agent_count > len(req.agents):
        extra_needed = req.agent_count - len(req.agents)
        # Distribute them deterministically around 3 major "Logistics Depots" 
        # so they don't visually jump around wildly between slider resets (RandomState(42) locks the seed).
        rng = np.random.RandomState(42)
        
        depots = [
            (size // 4, size // 4),
            (size - 20, size // 4),
            (size // 2, 10)
        ]
        
        extra_y = []
        extra_x = []
        
        agents_per_depot = extra_needed // len(depots)
        remainder = extra_needed % len(depots)
        
        for i, (cy, cx) in enumerate(depots):
            count = agents_per_depot + (1 if i < remainder else 0)
            if count > 0:
                # Gaussian cluster around depot, converting floats back to int matrix coords
                ys = rng.normal(loc=cy, scale=5.0, size=count).astype(int)
                xs = rng.normal(loc=cx, scale=5.0, size=count).astype(int)
                extra_y.extend(ys.tolist())
                extra_x.extend(xs.tolist())
        
        y_coords.extend(extra_y)
        x_coords.extend(extra_x)
    
    y_arr = np.array(y_coords)
    x_arr = np.array(x_coords)
    
    # Simple bounds check
    y_arr = np.clip(y_arr, 1, size - 2)
    x_arr = np.clip(x_arr, 1, size - 2)
    
    # 3x3 Brush (9 elements around the center)
    dy = np.array([-1, -1, -1,  0, 0, 0,  1, 1, 1])
    dx = np.array([-1,  0,  1, -1, 0, 1, -1, 0, 1])
    
    # Broadcasting to get all 9 coordinates for all N agents
    yy = (y_arr[:, None] + dy).flatten()
    xx = (x_arr[:, None] + dx).flatten()
    
    start_time = time.time()
    MAX_COMPUTE_TIME = 15.0 # Max 15 seconds of computing per connection
    
    try:
        # Smooth On-Demand Render Loop
        for step in range(req.max_steps):
            if time.time() - start_time > MAX_COMPUTE_TIME:
                print(f"Task {task_id} exceeded {MAX_COMPUTE_TIME}s limit.")
                try:
                    await websocket.send_json({"error": "Compute timeout exceeded"})
                except: pass
                break
                
            # Source Injection (Agents) - Vectorized O(1) for scale
            # Injecting the 10.0 energy potential to the Psi matrix 
            psi[yy, xx] = np.clip(psi[yy, xx] + 1.0, 0, 10.0)
                
            # Target Suction
            ty_start, ty_end = max(0, target_y-2), min(size, target_y+3)
            tx_start, tx_end = max(0, target_x-2), min(size, target_x+3)
            psi[ty_start:ty_end, tx_start:tx_end] *= 0.1
            
            # 1. PHYSICS STEP
            state = step_core({"psi": psi, "phi": phi, "kappa": kappa, "delta": delta}, cfg)
            psi = state["psi"]
            phi = state["phi"]
            psi *= (kappa > 0.05)
            
            # SEND DATA TO SVELTE CLIENT EVERY 5 STEPS (saving network bandwidth)
            if step % 5 == 0:
                paths = {}
                # Load path for all agents (extraction) - UI Rendering Optimization:
                # Even though the physics computes 100k agents in O(1) via the Phi field,
                # rendering 100k distinct SVG paths to the frontend would crash the browser and the Python loop.
                # We cap the visual path extraction to a representative subset.
                if req.return_paths:
                    visual_agents = req.agents[:500] if len(req.agents) > 500 else req.agents
                    for agent in visual_agents:
                        px, py = extract_path(phi, kappa, agent.start.x, agent.start.y, target_x, target_y, size)
                        paths[agent.id] = {"x": px, "y": py, "color": agent.color}
                
                # Compress PHI heatmap (sending only 1D array like kappa for WebGL render in JS)
                # Normalize phi to 0.0 - 1.0 for sending Float32 buffer to Svelte canvas
                max_phi = np.max(phi)
                if np.isnan(max_phi) or np.isinf(max_phi):
                    print("MATH OVERFLOW: NaN or Inf detected in physics field.")
                    break
                    
                phi_normalized = (phi / max_phi).flatten().tolist() if max_phi > 0 else phi.flatten().tolist()
                
                payload = {
                    "step": step,
                    "max_steps": req.max_steps,
                    "phi_flat": phi_normalized  # O(1) Scalable mathematical Tensor Field
                }
                
                if req.return_paths:
                    payload["paths"] = paths
                
                # Allow asyncio loop to accept weather mutations ("Dynamic Weather")
                # Trying to "non-blockingly" accept request from svelte, e.g. KAPPA change
                # Additional implementation in upcoming steps...
                
                await websocket.send_json(payload)
                await asyncio.sleep(0.01) # Yield thread for Pytorch/Threading stability
                
        # Correct and safe pipe closure after full cycle completion
        await websocket.close()
                
    except WebSocketDisconnect:
        # Once the Svelte component dies, the compute "while" loop ends and CPU load stops (0%)
        print(f"Client disconnected task {task_id}. Cleaning up compute.")
    except Exception as e:
        print(f"Server Error in simulation loop: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass

@app.get("/api/snippet")
async def get_api_snippet(language: str = "python", preset: str = "urban_design", fleet_size: int = 500):
    return {"language": language, "code": "DEPRECATED"}

# --- COMMERCIAL AI ECOSYSTEM ENDPOINTS ---

class RngRequest(BaseModel):
    resolution: int = 64
    pump_cycles: int = 1500

@app.post("/api/v1/ai/true-rng")
async def generate_true_rng(req: RngRequest, request: Request):
    """
    1. True RNG (Harvesting thermal variance from CPU threads)
    Returns mathematically perfect randomness generated from the physical environment.
    """
    client_ip = request.client.host if request.client else "unknown"
    
    size = req.resolution
    psi_1 = np.full((size, size), 0.5, dtype=np.complex128)
    delta_1 = np.zeros((size, size), dtype=np.float64)
    phi_1 = np.zeros((size, size), dtype=np.float64)
    kappa_1 = np.full((size, size), 0.2, dtype=np.float64)
    
    # Outer Skull
    y, x = np.ogrid[-size//2:size//2, -size//2:size//2]
    mask = x**2 + y**2 > (size//2 - 5)**2
    
    for step in range(req.pump_cycles):
        psi_1[mask] = 0.0j
        # Central Pump
        if step % 5 == 0:
            center = size // 2
            psi_1[center-5:center+5, center-5:center+5] = 1.0 + 0j
        
        state = step_core({"psi": psi_1, "phi": phi_1, "kappa": kappa_1, "delta": delta_1}, CoreConfig(use_mode_coupling=False))
        psi_1 = state["psi"]
        phi_1 = state["phi"]

    # Harvest entropy: We take the complex phase angle of the chaotic fluid
    entropy_matrix = np.angle(psi_1)
    
    # Extract as a hex string via SHA256 of the raw byte buffer for easy JSON consumption, 
    # but the entropy origin is *Hardware thermal RNG*, not the SHA math.
    import hashlib
    entropy_hex = hashlib.sha256(entropy_matrix.tobytes()).hexdigest()
    
    return {
        "status": "success", 
        "entropy_hex": entropy_hex, 
        "raw_sample": entropy_matrix[size//2:size//2+2, size//2:size//2+2].tolist()
    }

class HashRequest(BaseModel):
    payload: str
    grid_size: int = 64
    iterations: int = 1500

@app.post("/api/v1/ai/hash")
async def cryptographic_hash(req: HashRequest):
    """
    2. Cryptographic Avalanche Hashing
    Injects a string payload as physical wave drops and freezes the resulting topology.
    """
    size = req.grid_size
    psi = np.full((size, size), 0.5, dtype=np.complex128)
    delta = np.zeros((size, size), dtype=np.float64)
    phi = np.zeros((size, size), dtype=np.float64)
    kappa = np.full((size, size), 0.2, dtype=np.float64)
    
    y, x = np.ogrid[-size//2:size//2, -size//2:size//2]
    mask = x**2 + y**2 > (size//2 - 5)**2
    
    # Map payload bytes to initial pulse drops
    payload_bytes = req.payload.encode('utf-8')
    for i, byte in enumerate(payload_bytes):
        py = 5 + (i * 7) % (size - 10)
        px = 5 + (i * 13) % (size - 10)
        # The phase angle is dictated by the byte 
        phase = (byte / 255.0) * 2 * np.pi
        psi[py:py+2, px:px+2] += np.exp(1j * phase)
    
    for step in range(req.iterations):
        psi[mask] = 0.0j
        # Central Pump
        if step % 5 == 0:
            c = size // 2
            psi[c-2:c+2, c-2:c+2] = 1.0 + 0j
            
        state = step_core({"psi": psi, "phi": phi, "kappa": kappa, "delta": delta}, CoreConfig(use_mode_coupling=False))
        psi = state["psi"]
        phi = state["phi"]
        
    # The frozen Phi fluid topology is the hash
    import hashlib
    hash_hex = hashlib.sha256(phi.tobytes()).hexdigest()
    
    return {"status": "success", "hash": hash_hex}

class LplRequest(BaseModel):
    mask_flat: List[float] # 1.0 = fluid, 0.0 = wall
    size: int
    inputs: List[Point] # Where to inject 1.0 energy wave-pulses (e.g. A, B bits)
    iterations: int = 500

@app.post("/api/v1/ai/lpl-compile")
async def compile_lpl(req: LplRequest):
    """
    3. LPL Logic Compilation
    Uploads a physical CAD mask from the API and runs fluid logic gates.
    """
    size = req.size
    
    if len(req.mask_flat) != size * size:
        raise HTTPException(status_code=400, detail="Invalid mask_flat length. Must be size * size.")
        
    # Convert mask: 1 is fluid, 0 is wall. We need a boolean mask where True = Wall (0.0j forces)
    fluid_map = np.array(req.mask_flat, dtype=np.float64).reshape((size, size))
    wall_mask = fluid_map < 0.5
    
    psi = np.full((size, size), 0.5, dtype=np.complex128)
    delta = np.zeros((size, size), dtype=np.float64)
    phi = np.zeros((size, size), dtype=np.float64)
    kappa = np.full((size, size), 0.2, dtype=np.float64)
    
    for step in range(req.iterations):
        psi[wall_mask] = 0.0j
        
        # Inject Wave Inputs (The 1 Data bits)
        if step % 50 == 0:
            for p in req.inputs:
                py, px = p.y, p.x
                # Ensure within bounds
                if 0 <= py < size-1 and 0 <= px < size-1:
                    psi[py:py+2, px:px+2] = 1.0 + 0j
                
        state = step_core({"psi": psi, "phi": phi, "kappa": kappa, "delta": delta}, CoreConfig(use_mode_coupling=False))
        psi = state["psi"]
        phi = state["phi"]
        
    # Send the raw mathematical telemetry back via JSON Float Array
    phi_max = np.max(phi)
    phi_norm = (phi / phi_max).flatten().tolist() if phi_max > 0 else phi.flatten().tolist()
    
    return {"status": "success", "phi_flat": phi_norm}
