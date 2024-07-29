import os
from utils.parse_infer import run_infer, extract_buffer_overflows
from utils.parse_ast import parse_ast
from node_visitors.buffer_overflow_visitor import BufferOverflowVisitor
from flask import jsonify
from utils.format import preprocess_code
from utils.env import load_code_to_juliet
import shutil

def analyze_from_file(file_path):
    ast = parse_ast(file_path)
    visitor = BufferOverflowVisitor()
    visitor.visit(ast)
    return visitor.suggestions, 200


# Generates a response for the analyze endpoint
def analyze_from_code(code, juliet):
    try:
        temp_file_path, temp_dir_path = load_code_to_juliet(code, juliet)
        result, code = analyze_from_file(temp_file_path)
    except Exception as e:
        print('An error occured', e)
        return {'error': str(e)}, 500

    finally:
        shutil.rmtree(temp_dir_path)
    
    return result, code

