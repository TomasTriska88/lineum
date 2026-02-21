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

# Tuning Lineum na webové prostředí
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

# Modely pro REST upload z prohlížeče
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
    kappa_flat: List[float] # Zploštělé (flatten) pole propustností z canvasu Svelte
    max_steps: int = 1000
    preset: Optional[str] = "urban_design" # ['urban_design', 'evacuation', 'vascular', 'dielectric']

# Úložiště nastavení tasků
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
            # Návrat už v rozloženém JSON-ready formátu
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

@app.post("/api/route/task")
async def create_routing_task(req: RouteRequest):
    """
    Krok 1: Klient odešle rozsáhlou mapu a souřadnice. Server nezahajuje smyčku výpočtu.
    Pouze to uloží do RAM paměti a vrátí vstupenku (ID), kterou klient zadá do WebSocketu.
    """
    if len(req.kappa_flat) != req.size * req.size:
        raise HTTPException(status_code=400, detail="Délka kappa_flat neodpovídá size*size")
        
    task_id = str(uuid.uuid4())
    active_tasks[task_id] = req
    return {"status": "created", "task_id": task_id}


@app.websocket("/api/route/stream/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    Krok 2: Živé spuštění on-demand výpočtu pouze po dobu trvání spojení.
    """
    await websocket.accept()
    
    if task_id not in active_tasks:
        await websocket.send_json({"error": "Task not found."})
        await websocket.close()
        return
        
    req = active_tasks.pop(task_id) # Vyjmout ze stacku
    size = req.size
    
    # Rekonstrukce mřížky z odeslaného 1D pole do 2D Numpy Float matice
    kappa = np.array(req.kappa_flat, dtype=np.float64).reshape((size, size))
    psi = np.zeros((size, size), dtype=np.complex128)
    delta = np.zeros((size, size), dtype=np.float64)
    phi = np.zeros((size, size), dtype=np.float64)
    
    target_y = req.target.y
    target_x = req.target.x
    
    # APLIKACE "PRESET" (Demosféra fyziky Linea k ukázkovým Use-cases)
    preset = req.preset if hasattr(req, 'preset') and req.preset else "urban_design"
    preset_settings = {
        "urban_design": {"dissipation": 0.005, "noise": 0.0, "reaction": 0.1, "phi_diff": 0.05},
        "evacuation": {"dissipation": 0.08, "noise": 0.0, "reaction": 0.3, "phi_diff": 0.15},    # Rychlý rozpad zácpy, chaotičtější
        "vascular": {"dissipation": 0.002, "noise": 0.08, "reaction": 0.02, "phi_diff": 0.02},  # Křehké dlouhotrvající větvičky s šumem
        "dielectric": {"dissipation": 0.001, "noise": 0.0, "reaction": 0.5, "phi_diff": 0.005}, # Masivní bleskový rovný push s propálením
    }
    
    cfg = preset_settings.get(preset, preset_settings["urban_design"])
    
    core_math.DISSIPATION_RATE = cfg["dissipation"]
    core_math.NOISE_STRENGTH = cfg["noise"]
    core_math.REACTION_STRENGTH = cfg["reaction"]
    core_math.PHI_DIFFUSION = cfg["phi_diff"]
    
    start_time = time.time()
    MAX_COMPUTE_TIME = 15.0 # Max 15 sekund výpočtu per connection
    
    try:
        # Plynulý On-Demand Render Loop
        for step in range(req.max_steps):
            if time.time() - start_time > MAX_COMPUTE_TIME:
                print(f"Task {task_id} exceeded {MAX_COMPUTE_TIME}s limit.")
                try:
                    await websocket.send_json({"error": "Compute timeout exceeded"})
                except: pass
                break
                
            # Injekce Zdrojů (Agentů)
            for agent in req.agents:
                sy, sx = agent.start.y, agent.start.x
                # Ošetření okrajů matice
                sy_start, sy_end = max(0, sy-1), min(size, sy+2)
                sx_start, sx_end = max(0, sx-1), min(size, sx+2)
                psi[sy_start:sy_end, sx_start:sx_end] = 10.0
                
            # Odsávání Cíle
            ty_start, ty_end = max(0, target_y-2), min(size, target_y+3)
            tx_start, tx_end = max(0, target_x-2), min(size, target_x+3)
            psi[ty_start:ty_end, tx_start:tx_end] *= 0.1
            
            # 1. KROK FYZIKY
            psi, phi = evolve(psi, delta, phi, kappa)
            psi *= (kappa > 0.05)
            
            # ODESLÁNÍ DAT DO SVELTE KLIENTA KAŽDÝCH 5 KROKŮ (šetření bandwidth sítě)
            if step % 5 == 0:
                # Načteme trasu pro všechny agenty (Extrakcne)
                paths = {}
                for agent in req.agents:
                    px, py = extract_path(phi, kappa, agent.start.x, agent.start.y, target_x, target_y, size)
                    paths[agent.id] = {"x": px, "y": py, "color": agent.color}
                
                # Zkomprimování PHI heatmapy (posíláme pouze 1D array jako u kappa pro WebGL render v JS)
                # Normujeme phi na 0.0 - 1.0 pro odesílání Float32 bufferu Svelte canvasu
                max_phi = np.max(phi)
                phi_normalized = (phi / max_phi).flatten().tolist() if max_phi > 0 else phi.flatten().tolist()
                
                payload = {
                    "step": step,
                    "max_steps": req.max_steps,
                    "paths": paths,
                    "phi_flat": phi_normalized  # Lze pak v budoucnu pro úsporu přes binární struct
                }
                
                # Umožnění asyncio smyčky přijmout mutace počasí ("Dynamic Weather")
                # Zkoušíme "neblokovaně" přijmout dotaz ze svelte, např změnu KAPPA
                # Doplňující implementace v dalších krocích...
                
                await websocket.send_json(payload)
                await asyncio.sleep(0.01) # Yield vlákna pro Pytorch/Threading stabilitu
                
        # Korektní a bezpečné uzavření trubky po uběhnutí celého cyklu
        await websocket.close()
                
    except WebSocketDisconnect:
        # Jakmile Svelte komponenta umře, výpočetní "while" smyčka skončí a CPU zátěž končí (0%)
        print(f"Client disconnected task {task_id}. Cleaning up compute.")
    except Exception as e:
        print(f"Server Error in simulation loop: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass

@app.get("/api/snippet")
async def get_api_snippet(language: str = "python", preset: str = "urban_design", fleet_size: int = 500):
    """
    Returns dynamic API code snippets based on the current UI state.
    """
    if language.lower() == "python":
        snippet = f"""# 1. Initialize Lineum Continuous Solver
import lineum as ln

# 2. Upload environmental tensor
solver = ln.SwarmEnvironment("{preset}.npz", precision=16)

# 3. Stream {fleet_size} parallel fleet agents
routes = solver.compute_flow(
    origins=fleet_positions,
    targets=delivery_nodes,
    temperature=0.02
)"""
    elif language.lower() == "curl":
        snippet = f"""curl -X POST https://api.lineum.io/v1/compute/swarm \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "environment": "{preset}.npz",
    "fleet_size": {fleet_size},
    "temperature": 0.02
  }}'"""
    else:
        snippet = "// Language not supported."

    return {"language": language, "code": snippet}
