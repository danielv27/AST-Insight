from pycparser import c_ast

class NameExtractor(c_ast.NodeVisitor):
    def __init__(self):
        self.name = None
    def visit_ID(self, node):
        self.name = node.name
    def get_result(self):
        return self.name