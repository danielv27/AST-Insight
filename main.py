import sys
import os
from parse_infer import run_infer, extract_buffer_overflows
from parse_ast import parse_ast
from node_visitors.buffer_overflow_visitor import BufferOverflowVisitor
from flask import Flask, request, jsonify
from flask_cors import CORS
from tempfile import NamedTemporaryFile, mkdtemp
from utils.format import preprocess_code
from utils.env import setup_juliet_temp_dir

sys.path.extend(['.', '..'])

app = Flask(__name__)
CORS(app, resources={r"/analyze": {"origins": "*"}})


def load_request_to_file(code: str, juliet: bool):
    temp_dir_path = setup_juliet_temp_dir() if juliet else mkdtemp()
    temp_file_path = os.path.join(temp_dir_path, "temp_test_file.c")
    with open(temp_file_path, 'w') as temp_file:
        temp_file.write(code)
    return temp_file_path



@app.route('/analyze', methods=["POST"])
def analyze():
    code = preprocess_code(request.json['code'])
    juliet = request.json['juliet']

    try:
        temp_file_path = load_request_to_file(code, juliet)
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
