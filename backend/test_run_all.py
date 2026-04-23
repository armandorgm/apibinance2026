import subprocess
import os
import sys

def run_tests():
    """
    Runs all pytest tests in the backend, prints to console and logs to .temp/test_results.log.
    """
    # Current file is in backend/
    # Project root is ../
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    temp_dir = os.path.join(project_root, ".temp")
    
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    log_file = os.path.join(temp_dir, "test_results.log")
    
    # Use -s to see print statements if any (but user wanted console + log)
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"]
    
    print(f"RUNNER: Iniciando Suite de Pruebas (TDD Mode)...")
    print(f"LOG: {log_file}")
    print("-" * 50)
    
    try:
        with open(log_file, "w", encoding="utf-8") as f:
            # Write header to log
            f.write(f"TEST RUN: {datetime.now().isoformat()}\n")
            f.write("-" * 50 + "\n")
            
            # Start process
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True,
                cwd=backend_dir
            )
            
            for line in process.stdout:
                sys.stdout.write(line)
                f.write(line)
                
            process.wait()
            
            if process.returncode == 0:
                print("\n[SUCCESS] Todos los tests pasaron exitosamente.")
            else:
                print(f"\n[FAILURE] Se encontraron fallos (Exit code: {process.returncode}).")
                
    except Exception as e:
        print(f"!!! Error critico ejecutando el runner: {e}")

if __name__ == "__main__":
    from datetime import datetime
    run_tests()
