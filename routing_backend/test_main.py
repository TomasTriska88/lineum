from fastapi.testclient import TestClient
import pytest
from starlette.websockets import WebSocketDisconnect
from routing_backend.main import app, active_tasks
import time

client = TestClient(app)

def test_rest_task_creation():
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
