import subprocess
import sys
import time
import os
import urllib.request
import urllib.error
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def check_backend_ready(timeout=10):
    url = "http://127.0.0.1:8000/api/v1/system/health"
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False

def main():
    print("=" * 60)
    print(" MULE MATRIX · Unified Financial Investigation Platform")
    print("=" * 60)
    
    backend_dir = BASE_DIR / "backend"
    frontend_dir = BASE_DIR / "frontend"
    
    print("\n[1/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
        cwd=str(backend_dir)
    )
    
    print("[2/3] Verifying Backend Health Telemetry...")
    if check_backend_ready(timeout=12):
        print("  ✓ Backend is ONLINE and responding at http://127.0.0.1:8000")
    else:
        print("  ! Notice: Backend did not report ready within timeout. Proceeding...")

    print("[3/3] Starting Vite Frontend on http://localhost:5173 ...")
    frontend_proc = subprocess.Popen(
        ["npm.cmd" if os.name == "nt" else "npm", "run", "dev"],
        cwd=str(frontend_dir)
    )
    
    print("\n" + "=" * 60)
    print("✓ Platform Services Live:")
    print("  - Frontend UI:      http://localhost:5173")
    print("  - Backend API:      http://127.0.0.1:8000")
    print("  - Interactive Docs: http://127.0.0.1:8000/docs")
    print("=" * 60)
    print("Press Ctrl+C to terminate both servers.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down MULE MATRIX processes...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()
