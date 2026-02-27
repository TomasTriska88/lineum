from fastapi.testclient import TestClient
import pytest
from starlette.websockets import WebSocketDisconnect
from routing_backend.main import app, active_tasks, ip_request_counts
import time

client = TestClient(app)

def test_rest_task_creation():
    ip_request_counts.clear()
    size = 16
    kappa_flat = [1.0] * (size * size)
    
    payload = {
        "size": size,
        "agents": [
            {"id": "a1", "start": {"x": 2, "y": 2}, "color": "cyan"}
        ],
        "target": {"x": 10, "y": 10},
        "kappa_flat": kappa_flat,
        "max_steps": 5
    }
    
    response = client.post("/api/route/task", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    
    task_id = data["task_id"]
    assert task_id in active_tasks
    
def test_websocket_kill_switch():
    """
    Testuje nejdůležitější cloudovou ochranu Lineum API:
    Že se smyčka a zpracování paměti ABSOLUTNĚ ZASTAVÍ a zahodí,
    jakmile uživatel ukončí WebSocket spojení ("zavře prohlížeč").
    """
    size = 16
    kappa_flat = [1.0] * (size * size)
    
    payload = {
        "size": size,
        "agents": [
            {"id": "a1", "start": {"x": 2, "y": 2}, "color": "cyan"}
        ],
        "target": {"x": 10, "y": 10},
        "kappa_flat": kappa_flat,
        "max_steps": 500  # Obří číslo, které by normálně žralo CPU na cloudu
    }
    
    # 1. Založení tasku (nedělá žádnou CPU zátěž na pozadí)
    response = client.post("/api/route/task", json=payload)
    task_id = response.json()["task_id"]
    
    # 2. Napojení přes websocket a "Utečení" v polovině
    # Prohlížeč odchází ze stránky:
    with client.websocket_connect(f"/api/route/stream/{task_id}") as websocket:
        data1 = websocket.receive_json()
        assert data1["step"] == 0
        
        data2 = websocket.receive_json()
        assert data2["step"] == 5
        
        # PRÁVĚ TEĎ NATVRDO UKONČÍME SPOJENÍ
        # Context manager (with) automaticky zavře websocket
            
    # Ochrana proti uvíznutí tasku na serveru v paměti:
    assert task_id not in active_tasks

def test_max_steps_hard_limit():
    """
    Testuje, že i při plně otevřeném WebSocket spojení existuje 
    maximální strop instrukcí, po kterém se smyčka vypne, aby
    nežrala CPU donekonečna.
    """
    size = 16
    kappa_flat = [1.0] * (size * size)
    
    payload = {
        "size": size,
        "agents": [
            {"id": "a1", "start": {"x": 2, "y": 2}, "color": "cyan"}
        ],
        "target": {"x": 10, "y": 10},
        "kappa_flat": kappa_flat,
        "max_steps": 15 # Přísný hard-limit
    }
    
    response = client.post("/api/route/task", json=payload)
    task_id = response.json()["task_id"]
    
    with client.websocket_connect(f"/api/route/stream/{task_id}") as websocket:
        # krok 0
        assert websocket.receive_json()["step"] == 0
        # krok 5
        assert websocket.receive_json()["step"] == 5
        # krok 10
        assert websocket.receive_json()["step"] == 10
        
        # Očekáváme, že se smyčka bezpečně vypne a websocket timeoutuje, 
        # protože už nenastane krok 15. Smyčka skrze `range(max_steps)` skončí a uzavře rouru.
        with pytest.raises(WebSocketDisconnect):
            websocket.receive_json()

def test_massive_agent_count_scaling():
    """
    Tests that the backend API can handle agent_count = 100_000 without crashing
    by utilizing the new NumPy O(1) vectorized generation.
    """
    size = 64
    kappa_flat = [1.0] * (size * size)
    
    payload = {
        "size": size,
        "agents": [
            {"id": "a1", "start": {"x": 2, "y": 2}, "color": "cyan"}
        ],
        "agent_count": 100000,
        "target": {"x": 10, "y": 10},
        "kappa_flat": kappa_flat,
        "max_steps": 5,
        "preset": "urban_design"
    }
    
    response = client.post("/api/route/task", json=payload)
    assert response.status_code == 200
    task_id = response.json()["task_id"]
    
    with client.websocket_connect(f"/api/route/stream/{task_id}") as websocket:
        msg = websocket.receive_json()
        assert "error" not in msg
        assert msg["step"] == 0
        assert "phi_flat" in msg
        # This confirms that no Math Overflow (NaN) occurred and the O(1) loop started correctly.

def test_agent_injection_intensity():
    """
    Verifies that requesting a massive agent_count actually forces the backend
    to inject extra coordinates into the physics calculation, resulting in
    significantly higher thermal field density (phi).
    """
    size = 64
    kappa_flat = [1.0] * (size * size)
    agents_payload = [{"id": f"a{i}", "start": {"x": 32, "y": 32}, "color": "cyan"} for i in range(50)]
    
    # Run 1: Normal 50 agents
    payload_normal = {
        "size": size,
        "agents": agents_payload,
        "agent_count": 50,
        "target": {"x": 10, "y": 10},
        "kappa_flat": kappa_flat,
        "max_steps": 2,
        "preset": "urban_design"
    }
    
    # Run 2: Massive 20,000 agents
    payload_massive = {
        "size": size,
        "agents": agents_payload,
        "agent_count": 20000,
        "target": {"x": 10, "y": 10},
        "kappa_flat": kappa_flat,
        "max_steps": 2,
        "preset": "urban_design"
    }

    def get_phi_sum(payload):
        resp = client.post("/api/route/task", json=payload)
        task_id = resp.json()["task_id"]
        with client.websocket_connect(f"/api/route/stream/{task_id}") as websocket:
            msg0 = websocket.receive_json() # Step 0 (Physics run once before broadcast)
            return sum(msg0["phi_flat"])

    sum_normal = get_phi_sum(payload_normal)
    sum_massive = get_phi_sum(payload_massive)
    
    assert sum_massive > sum_normal * 10, f"Massive sum {sum_massive} not significantly larger than normal {sum_normal}. Missing appendage array bug detected!"

def test_return_paths_flag_bypass():
    """
    Verifies that when return_paths=False, the O(1) B2B heatmap API omits the O(N) paths extraction.
    """
    ip_request_counts.clear()
    size = 32
    kappa_flat = [1.0] * (size * size)
    agents_payload = [{"id": f"a{i}", "start": {"x": 16, "y": 16}, "color": "white"} for i in range(5)]
    
    payload = {
        "size": size,
        "agents": agents_payload,
        "agent_count": 5,
        "target": {"x": 5, "y": 5},
        "kappa_flat": kappa_flat,
        "max_steps": 2,
        "preset": "urban_design",
        "return_paths": False
    }

    time.sleep(1.5) # Prevent 429 Rate Limiter
    resp = client.post("/api/route/task", json=payload)
    assert resp.status_code == 200
    task_id = resp.json()["task_id"]

    with client.websocket_connect(f"/api/route/stream/{task_id}") as websocket:
        msg = websocket.receive_json()
        assert "paths" not in msg, "Paths dictionary should not be present natively when return_paths is False."
        assert "phi_flat" in msg, "Phi tensor field must be present."
        assert len(msg["phi_flat"]) == size * size, "Phi tensor dimensions must match physics board."

def test_presets_websocket():
    size = 16
    kappa_flat = [1.0] * (size * size)
    
    payload = {
        "size": size,
        "agents": [
            {"id": "a1", "start": {"x": 2, "y": 2}, "color": "cyan", "name": "Test", "eta": "10s"}
        ],
        "target": {"x": 10, "y": 10},
        "kappa_flat": kappa_flat,
        "max_steps": 5,
        "preset": "vascular"
    }
    
    response = client.post("/api/route/task", json=payload)
    assert response.status_code == 200 # Pokud spadne tady, je to Pydanticem
    task_id = response.json()["task_id"]
    
    # Kdyby byla chyba 500 na backendu, websocket.receive_json vyhodi exception
    with client.websocket_connect(f"/api/route/stream/{task_id}") as websocket:
        msg = websocket.receive_json()
        assert msg["step"] == 0

# --- AI LTM ECOSYSTEM TESTS ---

def test_ai_true_rng():
    payload = {"resolution": 32, "pump_cycles": 10}
    response = client.post("/api/v1/ai/true-rng", json=payload)
    assert response.status_code == 200, f"RNG API Error: {response.text}"
    data = response.json()
    assert "entropy_hex" in data

def test_ai_hash():
    payload = {"payload": "LINEUM", "grid_size": 32, "iterations": 10}
    response = client.post("/api/v1/ai/hash", json=payload)
    assert response.status_code == 200, f"Hash API Error: {response.text}"
    data = response.json()
    assert "hash" in data

def test_ai_lpl_compile():
    size = 16
    payload = {
        "mask_flat": [1.0] * (size * size),
        "size": size,
        "inputs": [{"x": 2, "y": 2}],
        "iterations": 10
    }
    response = client.post("/api/v1/ai/lpl-compile", json=payload)
    assert response.status_code == 200, f"LPL API Error: {response.text}"
    data = response.json()
    assert "phi_flat" in data
