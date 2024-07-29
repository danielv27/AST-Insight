import os
import json
import shutil
from pathlib import Path
from analyze import analyze_from_file
from utils.env import load_existing_file_to_juliet

# Paths to the test directories
JULIET_TESTCASES_DIR = os.path.join(Path(__file__).parent.resolve(), 'juliet-test-suite-c/testcases')
CWE_121 = os.path.join(JULIET_TESTCASES_DIR, 'CWE121_Stack_Based_Buffer_Overflow')
CWE_122 = os.path.join(JULIET_TESTCASES_DIR, 'CWE122_Heap_Based_Buffer_Overflow')

RESULTS_DIR = "./tests/results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_test_suite(test_dir, result_file, juliet_required=True):
    results = {}
    subdirs = sorted([d for d in os.listdir(test_dir) if os.path.isdir(os.path.join(test_dir, d))])
    for subdir in subdirs:
        subdir_path = os.path.join(test_dir, subdir)
        for file in os.listdir(subdir_path):
            if file.endswith(".c"):
                test_path = os.path.join(subdir_path, file)
                # print(f"Running test: {test_path}")

                temp_file_path, temp_dir_path = load_existing_file_to_juliet(test_path, juliet_required)
                

                # Run your analyze function on the test file
                try:
                    suggestions, code = analyze_from_file(temp_file_path)
                    if code == 200:
                        results[test_path] = {
                            "suggestions": suggestions,
                            "status": code
                        }
                        print(f"Test {test_path} succeeded. {suggestions}")
                    else:
                        results[test_path] = {
                            "error": str(e),
                            "status": code
                        }
                except Exception as e:
                    results[test_path] = {
                        "error": str(e),
                        "status": 500
                    }
                    print(f"Test {test_path} failed with error: {str(e)}")
                finally:
                    # Cleanup the temporary directory
                    shutil.rmtree(temp_dir_path)

    # Save results to the specified file
    with open(result_file, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Results saved to {result_file}")

def main():
    # Run tests for CWE121
    cwe121_results = os.path.join(RESULTS_DIR, "CWE121_results.json")
    run_test_suite(CWE_121, cwe121_results)

    # Run tests for CWE122
    cwe122_results = os.path.join(RESULTS_DIR, "CWE122_results.json")
    run_test_suite(CWE_122, cwe122_results)
    
    print("Tests completed and results saved.")

if __name__ == "__main__":
    main()
