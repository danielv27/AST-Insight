import argparse
import os
import json
import re
import shutil
from pathlib import Path
from analyze import analyze_from_file
from utils.env import load_existing_file_to_juliet
from utils.parse_infer import get_metrics_from_infer_output, run_infer
import subprocess
from pycparser import c_ast

# Paths to the test directories
JULIET_TESTCASES_DIR = os.path.join(Path(__file__).parent.resolve(), 'juliet-test-suite-c/testcases')
CWE_121 = os.path.join(JULIET_TESTCASES_DIR, 'CWE121_Stack_Based_Buffer_Overflow')
CWE_122 = os.path.join(JULIET_TESTCASES_DIR, 'CWE122_Heap_Based_Buffer_Overflow')

RESULTS_DIR = "./tests/results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def extract_function_name_from_line_number(file_path, line_number):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    function_name = None
    # Look for function definition above the line_number
    for i, line in enumerate(lines):
        current_line_number = i + 1
        match = re.match(r'^\s*(\w+)\s+(\w+)\s*\([^;]*\)\s*$', line)
        if line_number > current_line_number and match:
            function_name = match.group(2)
    return function_name

class TestCaseExtractor(c_ast.NodeVisitor):
    pass

# TODO: function that extracts all functions that end with _good or _bad using a node visitor
def get_testcases_from_juliet():
    pass

def get_metrics_from_ast_insight_suggestions(file, suggestions):
    functions_checked = []
    for suggestion in suggestions:
        function_name = suggestion['function_name']
        print('function_name in ast insight:', function_name, function_name.endswith('_bad'))
        if 'bad' in function_name:
            status = "true_positive"
        elif 'good' in function_name:
            status = "false_positive"
        else:
            continue  # Skip utility functions
        
        result = {
            "file": file,
            "function": function_name,
            "status": status
        }
        if result not in functions_checked:
            functions_checked.append({
                "file": file,
                "function": function_name,
                "status": status
            })
    return functions_checked

def run_test_ast_insight(test_dir, result_file, juliet_required=True):
    results = []
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
                        metrics = get_metrics_from_ast_insight_suggestions(file, suggestions)
                        print('metrics generated are:', metrics)
                        for metric in metrics:
                            results.append(metric)
                        print('current results:', results)
                        if suggestions:
                            print(f"Test {test_path} detected vunerabilties: {suggestions}")
                        else:
                            print(f'Test {test_path}: No vulerabilities detected')
                        
                    # else:
                    #     results[test_path] = {
                    #         "error": f'Failed with status code {code}',
                    #         "status": code
                    #     }
                        print(f"Test {test_path} failed without raising an exception with status code {code}")
                except Exception as e:
                    pass
                    # results[test_path] = {
                    #     "error": str(e),
                    #     "status": 500
                    # }
                    print(f"Test {test_path} failed with status code 500, error: {str(e)}")
                finally:
                    # Cleanup the temporary directory
                    shutil.rmtree(temp_dir_path)

    # Save results to the specified file
    with open(result_file, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Results saved to {result_file}")

def run_test_infer(test_dir, result_file, juliet_required = True):
    results = []
    subdirs = sorted([d for d in os.listdir(test_dir) if os.path.isdir(os.path.join(test_dir, d))])
    for subdir in subdirs:
        subdir_path = os.path.join(test_dir, subdir)
        for file in os.listdir(subdir_path):
            if file.endswith(".c"):
                test_path = os.path.join(subdir_path, file)
                print(f"Running test: {test_path}")

                temp_file_path, temp_dir_path = load_existing_file_to_juliet(test_path, juliet_required)
                
                # Run your analyze function on the test file
                try:
                    output, error = run_infer(temp_file_path)

                    if error == None:
                        metrics = get_metrics_from_infer_output(file, output)
                        for metric in metrics:
                            results.append(metric)
                        print('current results:', results)
                    # else:
                        # results = {
                        #     "error": str(error),
                        #     "status": 500
                        # }
                # except Exception as e:
                #     results[test_path] = {
                #         "error": str(e),
                #         'status': 500
                #     }
                finally:
                    # Cleanup the temporary directory
                    shutil.rmtree(temp_dir_path)
        # Save results to the specified file
    with open(result_file, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Results saved to {result_file}")


# def run_test_clang(test_dir, result_file, juliet_required = True):
#     results = []
#     subdirs = sorted([d for d in os.listdir(test_dir) if os.path.isdir(os.path.join(test_dir, d))])
#     for subdir in subdirs:
#         subdir_path = os.path.join(test_dir, subdir)
#         for file in os.listdir(subdir_path):
#             if file.endswith(".c"):
#                 test_path = os.path.join(subdir_path, file)
#                 print(f"Running test: {test_path}")

#                 temp_file_path, temp_dir_path = load_existing_file_to_juliet(test_path, juliet_required)
                
#                 # Run your analyze function on the test file
#                 try:
#                     run_clang_sa(temp_file_path)

    
#                 finally:
#                     # Cleanup the temporary directory
#                     shutil.rmtree(temp_dir_path)
#     #     # Save results to the specified file
#     # with open(result_file, "w") as f:
#     #     json.dump(results, f, indent=4)
#     # print(f"Results saved to {result_file}")

def run_test_clang(test_dir, result_file, juliet_required=True):
    results = []
    subdirs = sorted([d for d in os.listdir(test_dir) if os.path.isdir(os.path.join(test_dir, d))])
    for subdir in subdirs:
        subdir_path = os.path.join(test_dir, subdir)
        for file in os.listdir(subdir_path):
            if file.endswith(".c"):
                test_path = os.path.join(subdir_path, file)
                print(f"Running test: {test_path}")

                temp_file_path, temp_dir_path = load_existing_file_to_juliet(test_path, juliet_required)
                
                try:
                    output_dir = os.path.join(temp_dir_path, 'scan-build-output')
                    os.makedirs(output_dir, exist_ok=True)

                    
                    # Run Clang Static Analyzer with specific checkers enabled
                    result = subprocess.run([
                        'clang-sa/bin/scan-build',
                        'gcc', 
                        '-c', temp_file_path,
                        # '--load-plugin', 'alpha.security.MallocOverflow',
                        # '--load-plugin', 'alpha.security.ArrayBound',
                        # '--load-plugin', 'alpha.security.ArrayBoundV2',
                        # '--load-plugin', 'alpha.security.MallocOverflow'
                        '-Weverything'

                    ], capture_output=True, text=True)

                    # print('return code:', result.returncode)
                    print('output:', result.stdout, 'No bugs found', 'No bugs found' in result.stdout)
                    # print('error:', result.stderr)

                    
                    # Capture the analysis results
                    # for root, _, files in os.walk(output_dir):
                    #     for report_file in files:
                    #         if report_file.endswith('.plist'):
                    #             report_file_path = os.path.join(root, report_file)
                    #             with open(report_file_path, 'rb') as f:
                    #                 report_data = plistlib.load(f)
                    #                 results.append({
                    #                     "file": file,
                    #                     "report": report_data
                    #                 })
                finally:
                    shutil.rmtree(temp_dir_path)


def extract_metrics_from_cppcheck(file_path, err):
    functions_checked = []
    error_lower_case = err.lower()
    lines = error_lower_case.split('\n')
    status = None
    print('lines are', lines)
    for line in lines:
        if 'index' in line or 'bounds' in line:
            parts = line.split(':')
            line_number = int(parts[1])
            function_name = extract_function_name_from_line_number(file_path, line_number)
            if function_name:
                if 'bad' in function_name:
                    status = 'true_positive'
                elif 'good' in function_name:
                    status = 'false_positive'
                else:
                    continue
                result = {
                    "file": file_path,
                    "function": function_name,
                    "status": status,
                    "info": line
                }

                if result not in functions_checked:
                    functions_checked.append(result)
    return functions_checked

        

def run_test_cpp(test_dir, result_file, juliet_required=True):
    results = []
    subdirs = sorted([d for d in os.listdir(test_dir) if os.path.isdir(os.path.join(test_dir, d))])
    for subdir in subdirs:
        subdir_path = os.path.join(test_dir, subdir)
        for file in os.listdir(subdir_path):
            if file.endswith(".c"):
                test_path = os.path.join(subdir_path, file)
                print(f"Running test: {test_path}")

                temp_file_path, temp_dir_path = load_existing_file_to_juliet(test_path, juliet_required)
                
                try:
                    output_dir = os.path.join(temp_dir_path, 'scan-build-output')
                    os.makedirs(output_dir, exist_ok=True)
                    
                    
                    # Run Clang Static Analyzer with specific checkers enabled
                    result = subprocess.run([
                        'cppcheck', 
                        '--template=gcc',
                        '--check-level=exhaustive',
                        temp_file_path

                    ], capture_output=True, text=True)

                    # print('return code:', result.returncode)
                    # print('output:', result.stdout)

                    metrics = extract_metrics_from_cppcheck(temp_file_path, result.stderr)
                    for metric in metrics:
                        results.append(metric)
                    
                finally:
                    shutil.rmtree(temp_dir_path)

    with open(result_file, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Results saved to {result_file}")

def main():
    parser = argparse.ArgumentParser(description="Run Juliet Test Suite benchmarks.")
    parser.add_argument(
        '--tool',
        type=str,
        required=True,
        choices=['ast', 'infer', 'cppcheck', 'clang'],
        help="Specify the analysis tool to use (ast, infer, cppcheck, clang)."
    )
    args = parser.parse_args()

    tool_map = {
        'ast': run_test_ast_insight,
        'infer': run_test_infer,
        'clang': run_test_clang,
        'cppcheck': run_test_cpp,
    }

    if args.tool in tool_map:

        print(f'Running test {args.tool}')
        result_file = os.path.join(RESULTS_DIR, f"CWE121_{args.tool}_results.json")
        tool_map[args.tool](CWE_121, result_file)

        result_file = os.path.join(RESULTS_DIR, f"CWE122_{args.tool}_results.json")
        tool_map[args.tool](CWE_122, result_file)

    else:
        print(f"Unknown tool: {args.tool}")

if __name__ == "__main__":
    main()
