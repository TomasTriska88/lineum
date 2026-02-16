import requests
import sys
import time
import os

def verify_deployment(url, expected_text, timeout=300, interval=30, max_retries=3):
    """
    Pings the URL until expected_text is found or timeout/retries reached.
    """
    print(f"[VERIFY] Checking deployment at {url}...")
    start_time = time.time()
    attempt = 0
    
    while time.time() - start_time < timeout:
        attempt += 1
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                if expected_text in response.text:
                    print(f"[VERIFY] Success! Found '{expected_text}' at {url} (Attempt {attempt})")
                    return True
                else:
                    print(f"[VERIFY] Status 200, but '{expected_text}' not found yet. Env might be stale.")
            elif response.status_code == 404:
                print(f"[VERIFY] ERROR 404: Resource missing at {url}. This likely indicates a path resolution bug.")
            else:
                print(f"[VERIFY] Status {response.status_code}, retrying...")
        except Exception as e:
            print(f"[VERIFY] Connection error: {e}. Retrying...")
            
        if attempt >= max_retries and (time.time() - start_time) > 60:
            print(f"[VERIFY] Reached max retries ({max_retries}) and 60s passed without success.")
            break

        time.sleep(interval)
        
    print(f"[VERIFY] FAILED: Could not verify deployment at {url}")
    return False

if __name__ == "__main__":
    url = os.environ.get("TARGET_URL", "https://lineum.io/wiki/lineum-core")
    
    # We verify if the core title is present
    portal_ok = verify_deployment(
        url, 
        "lineum-core", # Slug check in case title is dynamic
        timeout=300,
        max_retries=5
    )
    
    if not portal_ok:
        print("\n[CRITICAL ERROR] Production deployment failed verification.")
        print("AGENT ACTION REQUIRED: Check Railway logs, verify path synchronization, and fix the regression.")
        sys.exit(1)
        
    print("[VERIFY] All systems green. Production is healthy.")
    sys.exit(0)
