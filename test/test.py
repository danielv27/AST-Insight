import os
from analyze import analyze_from_file

# Paths to the test directories
JULIET_TESTCASES_DIR = "./juliet-test-suite-c/testcases/"
CWE_121_DIR = "CWE121_Stack_Based_Buffer_Overflow"
CWE_122_DIR = "CWE122_Stack_Based_Buffer_Overflow"

RESULTS_DIR = "./test/results"

os.makedirs(RESULTS_DIR, exist_ok=True)

def run_test_suite(test_dir):
    results = {}
    for root, _, files in os.walk(test_dir):
        for file in files:
            if file.endswith(".c"):
                test_path = os.path.join(root, file)
                print(f"Running test: {test_path}")
                
                
    return results


