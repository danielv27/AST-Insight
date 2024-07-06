import sys
from parse_ast import parse_ast, ast_to_c_file
from stack_overflow_visitor.StackOverflowVisitor import StackOverflowVisitor
import subprocess
import json, os

sys.path.extend(['.', '..'])

def run_infer(file_path):
    # process = subprocess.Popen(f'sudo infer-arm64/bin/infer report --bufferoverrun  -- clang -c {file_path}', shell=True,
    #                         stdout=subprocess.PIPE, 
    #                         stderr=subprocess.PIPE)

    # # wait for the process to terminate
    # out, err = process.communicate()
    # errcode = process.returncode

    # print(out.decode('UTF-8'))
    # Run infer analysis
    analysis_process = subprocess.Popen(f'sudo infer-arm64/bin/infer run --bufferoverrun -- clang -c {file_path}', shell=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
    analysis_out, analysis_err = analysis_process.communicate()
    analysis_errcode = analysis_process.returncode

    if analysis_errcode != 0:
        print(f"Infer analysis encountered an error: {analysis_err.decode('UTF-8')}")
        sys.exit(analysis_errcode)

    report_process = subprocess.Popen('sudo infer-arm64/bin/infer report --format json', shell=True,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
    report_out, report_err = report_process.communicate()
    report_errcode = report_process.returncode

    if report_errcode != 0:
        print(f"Infer report encountered an error: {report_err.decode('UTF-8')}")
        sys.exit(report_errcode)

    # Check if report.json exists and read it
    report_file = 'infer-out/report.json'
    if not os.path.exists(report_file):
        print(f"Report file {report_file} does not exist.")
        sys.exit(1)

    # Parse JSON output
    with open(report_file, 'r') as f:
        infer_output = json.load(f)
    print(infer_output)
    return infer_output

    pass


if __name__ == "__main__":
    if len(sys.argv) > 1:

        file_path = sys.argv[1]

        # Step 1: pass the program to infra to get data

        # Command: sudo infer-arm64/bin/infer run --bufferoverrun  -- clang -c test_files/scanf/stack_overflow_basic.c

        # Step 2: pass that data to the visitor
        # Step 3: inise the visitor modify the AST 
        # Step 4: ast_to_file

        run_infer(file_path)
        

        ast = parse_ast(file_path)
        so_visitor = StackOverflowVisitor()
        so_visitor.visit(ast)

        ast_to_c_file(ast, file_path)

    else:
        print("Please provide a filename as argument")

