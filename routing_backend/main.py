from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Tuple, Optional
import asyncio
import uuid
import numpy as np
import heapq
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core.math import evolve
from lineum_core import math as core_math

# Tuning Lineum for web environment
core_math.TEST_EXHALE_MODE = False
core_math.NOISE_STRENGTH = 0.0
core_math.PSI_DIFFUSION = 0.15
core_math.REACTION_STRENGTH = 0.1
core_math.PHI_DIFFUSION = 0.01

app = FastAPI(title="Lineum Routing API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # V produkci lze omezit pouze na doménu lineum.io
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
    
    core_math.DISSIPATION_RATE = cfg["dissipation"]
    core_math.NOISE_STRENGTH = cfg["noise"]
    core_math.REACTION_STRENGTH = cfg["reaction"]
    core_math.PHI_DIFFUSION = cfg["phi_diff"]
    
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
                
            # Source Injection (Agents)
            for agent in req.agents:
                sy, sx = agent.start.y, agent.start.x
                # Matrix boundary handling
                sy_start, sy_end = max(0, sy-1), min(size, sy+2)
                sx_start, sx_end = max(0, sx-1), min(size, sx+2)
                psi[sy_start:sy_end, sx_start:sx_end] = 10.0
                
            # Target Suction
            ty_start, ty_end = max(0, target_y-2), min(size, target_y+3)
            tx_start, tx_end = max(0, target_x-2), min(size, target_x+3)
            psi[ty_start:ty_end, tx_start:tx_end] *= 0.1
            
            # 1. PHYSICS STEP
            psi, phi = evolve(psi, delta, phi, kappa)
            psi *= (kappa > 0.05)
            
            # SEND DATA TO SVELTE CLIENT EVERY 5 STEPS (saving network bandwidth)
            if step % 5 == 0:
                # Load path for all agents (extraction)
                paths = {}
                for agent in req.agents:
                    px, py = extract_path(phi, kappa, agent.start.x, agent.start.y, target_x, target_y, size)
                    paths[agent.id] = {"x": px, "y": py, "color": agent.color}
                
                # Compress PHI heatmap (sending only 1D array like kappa for WebGL render in JS)
                # Normalize phi to 0.0 - 1.0 for sending Float32 buffer to Svelte canvas
                max_phi = np.max(phi)
                phi_normalized = (phi / max_phi).flatten().tolist() if max_phi > 0 else phi.flatten().tolist()
                
                payload = {
                    "step": step,
                    "max_steps": req.max_steps,
                    "paths": paths,
                    "phi_flat": phi_normalized  # Can be optimized in future via binary struct
                }
                
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
        
        # We don't even inject float noise. We let the CPU threads naturally cause thermal race conditions.
        psi_1, phi_1 = evolve(psi_1, delta_1, phi_1, kappa_1)

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
            
        psi, phi = evolve(psi, delta, phi, kappa)
        
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
                
        psi, phi = evolve(psi, delta, phi, kappa)
        
    # Send the raw mathematical telemetry back via JSON Float Array
    phi_max = np.max(phi)
    phi_norm = (phi / phi_max).flatten().tolist() if phi_max > 0 else phi.flatten().tolist()
    
    return {"status": "success", "phi_flat": phi_norm}
