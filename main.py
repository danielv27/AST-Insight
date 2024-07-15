import sys
import os
from parse_infer import run_infer, extract_buffer_overflows
from parse_ast import parse_ast, ast_to_c_file
from buffer_overflow_visitor.BufferOverflowVisitor import BufferOverflowVisitor
from flask import Flask, request, jsonify
from flask_cors import CORS
from tempfile import NamedTemporaryFile

sys.path.extend(['.', '..'])

app = Flask(__name__)
CORS(app, resources={r"/analyze": {"origins": "*"}})

@app.route('/analyze', methods=["POST"])
def analyze():
    code = request.json['code']

    with NamedTemporaryFile(delete=False, suffix='.c') as temp_file:
        temp_file.write(code.encode('utf-8'))
        temp_file_path = temp_file.name

    try:
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
