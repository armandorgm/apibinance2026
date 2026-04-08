import subprocess
import sys
import os

def run_tests():
    """ Runs all tests using pytest and reports results. """
    print("="*60)
    print("  BINANCE FUTURES TRACKER - UNIFIED TEST RUNNER")
    print("="*60)
    
    # Ensure we are in the backend directory
    # (If run from backend/ or backend/tests/ or project root)
    current_dir = os.getcwd()
    if current_dir.endswith('tests'):
        os.chdir('..')
    elif not os.path.exists('pytest.ini') and os.path.exists('backend/pytest.ini'):
        os.chdir('backend')
    
    print(f"Running tests from: {os.getcwd()}")
    print("-" * 60)
    
    try:
        # Run pytest via the current python interpreter to ensure correct environment
        result = subprocess.run(
            [sys.executable, "-m", "pytest"], 
            capture_output=False, 
            text=True
        )
        
        if result.returncode == 0:
            print("\n" + "="*60)
            print("  ✅ ALL TESTS PASSED SUCCESSFULLY")
            print("="*60)
        else:
            print("\n" + "="*60)
            print(f"  ❌ TEST SUITE FAILED (Exit Code: {result.returncode})")
            print("="*60)
            sys.exit(result.returncode)
            
    except FileNotFoundError:
        print("Error: 'pytest' not found. Please install it with 'pip install pytest'.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
