import sys
import os
from analyze import analyze_from_code

from node_visitors.buffer_overflow_visitor import BufferOverflowVisitor
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.format import preprocess_code

sys.path.extend(['.', '..'])

app = Flask(__name__)
CORS(app, resources={r"/analyze": {"origins": "*"}})

@app.route('/analyze', methods=["POST"])
def analyze():
    try:
        code = request.json['code']
        juliet = request.json['juliet']
        result, response_code = analyze_from_code(code, juliet)
        return jsonify(result), response_code
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
