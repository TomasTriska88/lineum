import requests
import json

def test():
    # Wake
    r = requests.post("http://127.0.0.1:8000/entity/wake", json={"entity_id": "lina", "grid_size": 100})
    print("WAKE:", r.json())
    
    # Chat 'a'
    r = requests.post("http://127.0.0.1:8000/entity/lina/chat", json={"message": "a", "mode": "phys"})
    res = r.json()
    r_vec = res["readout_r"]
    r_sum = sum(r_vec)
    print("CHAT 'a' R_SUM:", r_sum)
    print("Metrics:", res["metrics"])
    print("Min R:", min(r_vec), "Max R:", max(r_vec))

if __name__ == "__main__":
    test()
