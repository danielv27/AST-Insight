# TODO: function that visits function declerations and counts all functions that contain both good or bad using a node visitor
import json
import os
from analyze import analyze_from_file
from test import get_subdirs, CWE_121, CWE_122, RESULTS_DIR
from utils.env import load_existing_file_to_juliet
from utils.parse_ast import parse_ast
import shutil
from node_visitors.test_case_counter import TestCaseExtractor

os.makedirs(RESULTS_DIR, exist_ok=True)

def update_testcase_count_from_juliet(test_dir, result_file):
    bad_count = 0
    good_count = 0
    
    subdirs = get_subdirs(test_dir)
    for subdir in subdirs:
        subdir_path = os.path.join(test_dir, subdir)
        for file in os.listdir(subdir_path):
            if file.endswith(".c"):
                test_path = os.path.join(subdir_path, file)
                print(test_path)
                temp_file_path, temp_dir_path = load_existing_file_to_juliet(test_path, True)
                try:
                    ast = parse_ast(temp_file_path)
                    extractor = TestCaseExtractor()
                    extractor.visit(ast)
                    bad_count += extractor.bad_count
                    good_count += extractor.good_count
                finally:
                    shutil.rmtree(temp_dir_path)
    with open(result_file, "w") as f:
        json.dump({'bad_count': bad_count, 'good_count': good_count}, f, indent=4)
    print(f"Results saved to {result_file}")


if __name__ == "__main__":
    result_file = os.path.join(RESULTS_DIR, f"CWE121_test_count.json")
    update_testcase_count_from_juliet(CWE_121, result_file)
    result_file = os.path.join(RESULTS_DIR, f"CWE122_test_count.json")
    update_testcase_count_from_juliet(CWE_122, result_file)