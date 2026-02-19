
import sys
import numpy as np
import hashlib
import os

def hash_array(name, arr):
    arr_c = np.ascontiguousarray(arr)
    data = arr_c.tobytes()
    h = hashlib.sha256(data).hexdigest()
    return h.upper()

def main():
    if len(sys.argv) != 3:
        print("Usage: python compare_checkpoints.py <file1> <file2>")
        sys.exit(1)
        
    f1 = sys.argv[1]
    f2 = sys.argv[2]
    
    print(f"Comparing:")
    print(f"1: {f1}")
    print(f"2: {f2}")
    
    d1 = np.load(f1, allow_pickle=False)
    d2 = np.load(f2, allow_pickle=False)
    
    fields = ["psi", "phi"]
    match = True
    
    print("\nHashes:")
    for f in fields:
        if f not in d1 or f not in d2:
            print(f"Field {f} missing in one file")
            continue
            
        h1 = hash_array(f, d1[f])
        h2 = hash_array(f, d2[f])
        
        m = (h1 == h2)
        if not m: match = False
        
        print(f"{f}:")
        print(f"  1: {h1}")
        print(f"  2: {h2}")
        print(f"  Match: {'✅' if m else '❌'}")
        
    if match:
        print("\n✅ CORE STATE MATCHES!")
    else:
        print("\n❌ STATES DIVERGE")

if __name__ == "__main__":
    main()
