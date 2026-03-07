import uvicorn
import multiprocessing
import time
import requests
from routing_backend.main import app

def run_server():
    uvicorn.run("routing_backend.main:app", host="127.0.0.1", port=8001, log_level="debug")

if __name__ == "__main__":
    p = multiprocessing.Process(target=run_server)
    p.start()
    time.sleep(3)
    
    try:
        print("Waking entity on isolated port 8001...")
        requests.post('http://127.0.0.1:8001/entity/wake', json={'entity_id':'debug-test', 'grid_size':64})
        time.sleep(1)
        
        print("Pinging hybrid chat...")
        res = requests.post('http://127.0.0.1:8001/entity/debug-test/chat', json={'message':'Tlak stoupa', 'mode':'hybrid'})
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text}")
    finally:
        p.terminate()
        p.join()
