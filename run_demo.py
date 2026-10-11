#!/usr/bin/env python3
"""
Research Nexus — Demo Mode Launcher
Launches the full Research Nexus application in local fallback demo mode using `fallback_demo.dat`.
Does NOT require a database or external LLM API keys.
"""

import os
import sys
import time
import subprocess
import webbrowser
import urllib.request
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
FALLBACK_DAT = BACKEND_DIR / "fallback_demo.dat"
GENERATE_SCRIPT = BACKEND_DIR / "generate_fallback.py"
MOCK_SERVER_SCRIPT = BACKEND_DIR / "mock_server.py"

def check_or_generate_dat():
    if not FALLBACK_DAT.exists() or FALLBACK_DAT.stat().st_size == 0:
        print("⚡ [Demo Launcher] fallback_demo.dat not found. Generating now...")
        res = subprocess.run([sys.executable, str(GENERATE_SCRIPT)], cwd=str(BACKEND_DIR))
        if res.returncode != 0:
            print("❌ Failed to generate fallback_demo.dat. Exiting.")
            sys.exit(1)
        print("✅ fallback_demo.dat generated successfully!")
    else:
        print(f"✅ Found local dataset fallback: {FALLBACK_DAT.name} ({FALLBACK_DAT.stat().st_size:,} bytes)")

def wait_for_url(url, timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(0.5)
    return False

def main():
    print("=" * 76)
    print(" 🔬 RESEARCH NEXUS — DEMO LAUNCH MODE (Local .dat Fallback)")
    print("=" * 76)
    
    # Step 1: Ensure dataset exists
    check_or_generate_dat()

    # Step 2: Start Mock FastAPI Backend
    print("\n🚀 Starting Mock API Backend server on http://localhost:8000 ...")
    backend_proc = subprocess.Popen(
        [sys.executable, str(MOCK_SERVER_SCRIPT)],
        cwd=str(BACKEND_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Step 3: Start Vite Frontend
    print("🌐 Starting Vite Frontend dev server on http://localhost:5173 ...")
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=str(FRONTEND_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Step 4: Health check
    print("⏳ Waiting for servers to initialize...")
    backend_healthy = wait_for_url("http://localhost:8000/api/health", timeout=12)
    frontend_healthy = wait_for_url("http://localhost:5173", timeout=12)

    print("\n" + "=" * 76)
    if backend_healthy:
        print(" ✅ Backend Mock API Server : RUNNING  (http://localhost:8000)")
    else:
        print(" ⚠️  Backend Mock API Server : Starting (http://localhost:8000)")

    if frontend_healthy:
        print(" ✅ Frontend Application UI : RUNNING  (http://localhost:5173)")
    else:
        print(" ⚠️  Frontend Application UI : Starting (http://localhost:5173)")

    print("=" * 76)
    print(" 💡 Demo features ready: Literature Matrix, Comparisons, Gap Analysis,")
    print("    Paper Intelligence, Visual Knowledge Graph, AI Authoring, Chat & Discovery!")
    print("=" * 76)

    # Step 5: Open Browser
    try:
        webbrowser.open("http://localhost:5173")
    except Exception:
        pass

    print("\nPress Ctrl+C to exit demo mode.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down demo processes...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Goodbye!")

if __name__ == "__main__":
    main()
