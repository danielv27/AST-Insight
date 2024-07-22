from pycparser import c_ast

# Extracts Any identifiers specified within a node (used to extract identifiers from buffer subscripts)
class IdentifierExtractor(c_ast.NodeVisitor):
    def __init__(self):
        self.variables = []
    def visit_ID(self, node):
        self.variables.append(node.name)