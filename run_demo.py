#!/usr/bin/env python3
"""
Research Nexus — Demo Mode Launcher
Launches the full Research Nexus application in local fallback demo mode using `fallback_demo.dat`.
Fast, non-blocking, clean shutdown, and stays up until closed.
"""

import os
import sys
import time
import subprocess
import webbrowser
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
FALLBACK_DAT = BACKEND_DIR / "fallback_demo.dat"
GENERATE_SCRIPT = BACKEND_DIR / "generate_fallback.py"
MOCK_SERVER_SCRIPT = BACKEND_DIR / "mock_server.py"

def kill_proc_tree(pid: int):
    """Cleanly terminates a process and all its children on Windows/Unix."""
    if not pid:
        return
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
        else:
            import signal
            os.killpg(os.getpgid(pid), signal.SIGTERM)
    except Exception:
        pass

def free_port(port: int):
    """Frees a port on Windows if lingering from a previous run."""
    if os.name == "nt":
        try:
            out = subprocess.check_output(
                f'netstat -ano | findstr :{port}',
                shell=True,
                text=True,
                errors="replace"
            )
            for line in out.strip().splitlines():
                parts = line.split()
                if len(parts) >= 5 and "LISTENING" in parts:
                    pid = parts[-1]
                    try:
                        int_pid = int(pid)
                        if int_pid > 0 and int_pid != os.getpid():
                            subprocess.run(
                                ["taskkill", "/F", "/PID", str(int_pid)],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                check=False
                            )
                    except ValueError:
                        pass
        except Exception:
            pass

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

def wait_for_url(url, timeout=12):
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "DemoHealthCheck"})
            with urllib.request.urlopen(req, timeout=1.5) as response:
                if response.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(0.3)
    return False

def main():
    print("=" * 76)
    print(" 🔬 RESEARCH NEXUS — DEMO LAUNCH MODE (Local .dat Fallback)")
    print("=" * 76)

    # Step 0: Ensure ports 8000 and 5173 are free from previous runs
    free_port(8000)
    free_port(5173)
    
    # Step 1: Ensure dataset exists
    check_or_generate_dat()

    # Step 2: Open dedicated log files to avoid OS pipe deadlocks
    backend_log_path = BACKEND_DIR / "backend.log"
    frontend_log_path = FRONTEND_DIR / "frontend.log"
    backend_log = open(backend_log_path, "w", encoding="utf-8", errors="replace")
    frontend_log = open(frontend_log_path, "w", encoding="utf-8", errors="replace")

    backend_proc = None
    frontend_proc = None

    try:
        # Step 3: Start Mock FastAPI Backend
        print("🚀 Starting Mock API Backend on http://127.0.0.1:8000 ...")
        backend_proc = subprocess.Popen(
            [sys.executable, str(MOCK_SERVER_SCRIPT)],
            cwd=str(BACKEND_DIR),
            stdout=backend_log,
            stderr=subprocess.STDOUT
        )

        # Step 4: Start Vite Frontend
        print("🌐 Starting Vite Frontend on http://127.0.0.1:5173 ...")
        npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
        frontend_proc = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=str(FRONTEND_DIR),
            stdout=frontend_log,
            stderr=subprocess.STDOUT
        )

        # Step 5: Fast health check using direct IPv4 (no localhost DNS delay)
        print("⏳ Initializing services...")
        backend_healthy = wait_for_url("http://127.0.0.1:8000/api/health", timeout=10)
        frontend_healthy = wait_for_url("http://127.0.0.1:5173", timeout=10)

        print("\n" + "=" * 76)
        if backend_healthy:
            print(" ✅ Backend Mock API Server : RUNNING  (http://127.0.0.1:8000)")
        else:
            print(" ⚠️  Backend Mock API Server : Starting (check backend/backend.log)")

        if frontend_healthy:
            print(" ✅ Frontend Application UI : RUNNING  (http://127.0.0.1:5173)")
        else:
            print(" ⚠️  Frontend Application UI : Starting (check frontend/frontend.log)")

        print("=" * 76)
        print(" 💡 Demo ready: Literature Matrix, Comparisons, Gap Analysis,")
        print("    Knowledge Graph, AI Manuscript Authoring, Chat & Discovery!")
        print("=" * 76)

        # Step 6: Open Browser directly
        try:
            webbrowser.open("http://127.0.0.1:5173")
        except Exception:
            pass

        print("\n🟢 App is running! Keep this command prompt open.")
        print("   Press Ctrl+C at any time to shut down.\n")

        # Step 7: Keep alive until user terminates or closes
        while True:
            b_ret = backend_proc.poll()
            f_ret = frontend_proc.poll()
            if b_ret is not None:
                print(f"\n⚠️ Backend process exited with code {b_ret}. See backend/backend.log")
                break
            if f_ret is not None:
                print(f"\n⚠️ Frontend process exited with code {f_ret}. See frontend/frontend.log")
                break
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n🛑 Shutting down demo processes...")
    finally:
        if backend_proc:
            kill_proc_tree(backend_proc.pid)
        if frontend_proc:
            kill_proc_tree(frontend_proc.pid)
        try:
            backend_log.close()
            frontend_log.close()
        except Exception:
            pass
        print("👋 Services stopped cleanly. Goodbye!\n")

if __name__ == "__main__":
    main()
