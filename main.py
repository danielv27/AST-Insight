import sys
import os
from parse_infer import run_infer, extract_buffer_overflows, setup_juliet_temp_dir
from parse_ast import parse_ast
from buffer_overflow_visitor.BufferOverflowVisitor import BufferOverflowVisitor
from flask import Flask, request, jsonify
from flask_cors import CORS
from tempfile import NamedTemporaryFile, mkdtemp

sys.path.extend(['.', '..'])

app = Flask(__name__)
CORS(app, resources={r"/analyze": {"origins": "*"}})

def adjust_code_formatting(code):
    lines = code.splitlines()
    adjusted_lines = []
    add_empty_line_next = False

    for i, line in enumerate(lines):
        stripped_line = line.strip()

        if stripped_line == '}':
            adjusted_lines.append(line)
            add_empty_line_next = True
        else:
            if add_empty_line_next:
                adjusted_lines.append('')  # Ensure exactly one empty line
                add_empty_line_next = False
            if stripped_line or (adjusted_lines and adjusted_lines[-1] != ''):
                adjusted_lines.append(line)

    return '\n'.join(adjusted_lines)

def addJulietCode(code):
    print('add juliet')
    return code


@app.route('/analyze', methods=["POST"])
def analyze():
    code = adjust_code_formatting(request.json['code'])
    juliet = request.json['juliet']


    temp_dir = setup_juliet_temp_dir() if juliet else mkdtemp()


    with NamedTemporaryFile(delete=False, suffix='.c') as temp_file:
        temp_file.write(code.encode('utf-8'))
        temp_file_path = temp_file.name

    try:
        temp_file_path = os.path.join(temp_dir, "temp_test_file.c")
        with open(temp_file_path, 'w') as temp_file:
            temp_file.write(code)

        infer_output, error = run_infer(temp_file_path)

        if error:
            return jsonify({'error': error}), 406

        buffer_overflows = extract_buffer_overflows(infer_output)

        ast = parse_ast(temp_file_path)
        visitor = BufferOverflowVisitor(buffer_overflows)
        visitor.visit(ast)

    finally:
        os.remove(temp_file_path)
        
    return jsonify(visitor.suggestions), 200

if __name__ == "__main__":
    app.run(debug=True)
