from pycparser import c_ast

class DataTypeExtractor(c_ast.NodeVisitor):
    def __init__(self):
        self.data_type = None
    
    def visit_TypeDecl(self, node):
        print('in extractor', node.type.names[0])
        self.data_type = node.type.names[0]

    def get_result(self):
        return self.data_type
