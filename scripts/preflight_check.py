import urllib.request
import json
import sys

def check_url(url, name):
    try:
        response = urllib.request.urlopen(url, timeout=5)
        if response.getcode() == 200:
            print(f"[OK] {name} is running at {url}")
            return True
        else:
            print(f"[ERROR] {name} returned status code {response.getcode()} at {url}")
            return False
    except Exception as e:
        print(f"[ERROR] {name} is NOT reachable at {url}. Error: {e}")
        return False

def main():
    print("--- Starting Preflight Service Check ---")
    backend_ok = check_url("http://127.0.0.1:8000/health", "Backend API")
    frontend_ok = check_url("http://127.0.0.1:3000", "Frontend UI")
    
    if backend_ok and frontend_ok:
        print("--- All systems are GO ---")
        sys.exit(0)
    else:
        print("--- Check FAILED. Please ensure both services are running. ---")
        sys.exit(1)

if __name__ == "__main__":
    main()
