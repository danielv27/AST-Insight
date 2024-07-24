import sys, os, subprocess, json, re
sys.path.extend(['.', '..'])
import json


def run_infer(file_path):
    try:
        analysis_process = subprocess.Popen(f'sudo infer-arm64/bin/infer run --bufferoverrun -- clang -c {file_path}', shell=True,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
        analysis_out, analysis_err = analysis_process.communicate()
        analysis_errcode = analysis_process.returncode

        if analysis_errcode != 0:
            error_message = f"Infer analysis encountered an error: {analysis_err.decode('UTF-8')}"
            return None, error_message

        analysis_process.wait()

        report_process = subprocess.Popen('sudo infer-arm64/bin/infer report --format json', shell=True,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
        report_out, report_err = report_process.communicate()
        report_errcode = report_process.returncode

        report_process.wait()

        if report_errcode != 0:
            error_message = f"Infer report encountered an error: {report_err.decode('UTF-8')}"
            return None, error_message

        # Check if report.json exists and read it
        report_file = 'infer-out/report.json'
        if not os.path.exists(report_file):
            error_message = f"Infer report encountered an error: Failed to generate report file."
            return None, error_message

        # Parse JSON output
        with open(report_file, 'r') as f:
            infer_output = json.load(f)
        return infer_output, None
    except Exception as e:
        return None, str(e)


def extract_buffer_overflows(json_output):
    buffer_overflows = []
    for issue in json_output:
        implemented = False
        bug_type = issue['bug_type']
        offset = None
        size = None

        if bug_type == 'BUFFER_OVERRUN_L1':
            implemented = True
            match = re.search(r'Offset(\s*added)?:\s*(-?\d+)\s*Size:\s*(\d+)', issue['qualifier'])
            if match:
                offset = int(match.group(2))
                size = int(match.group(3))

        if bug_type in ['BUFFER_OVERRUN_L2', 'BUFFER_OVERRUN_L3']:
            implemented = True
            match = re.search(r'Offset(\s*added)?:\s*\[\s*(-?\d+)\s*,\s*(-?\d+)\s*\]\s*Size:\s*(\d+)', issue['qualifier'])
            if match:
                offset = {'start': int(match.group(2)), 'end': int(match.group(3))}
                size = int(match.group(3))


        if implemented:
            details = {
                'file': issue['file'],
                'line': issue['line'],
                'column': issue.get('column', None),  # Using get to handle cases where column might not be present
                'index': offset,
                'size': size,
                'procedure': issue['procedure'],
                'procedure_start_line': issue['procedure_start_line'],
                'handled': False,
            }
            buffer_overflows.append(details)
    return buffer_overflows