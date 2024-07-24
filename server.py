import sys
import os
from analyze import analyze_from_code

from node_visitors.buffer_overflow_visitor import BufferOverflowVisitor
from flask import Flask, request
from flask_cors import CORS
from utils.format import preprocess_code

sys.path.extend(['.', '..'])

app = Flask(__name__)
CORS(app, resources={r"/analyze": {"origins": "*"}})

@app.route('/analyze', methods=["POST"])
def analyze():
    code = preprocess_code(request.json['code'])
    juliet = request.json['juliet']
    return analyze_from_code(code, juliet)

if __name__ == "__main__":
    app.run(debug=True)
