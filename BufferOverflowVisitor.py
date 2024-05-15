# Correlates to: https://cwe.mitre.org/data/definitions/787.html

from pycparser import c_ast
from unsafe_functions import check_unsafe_write_function_calls

class BufferOverflowVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.current_function = None
        self.declared_vars = {}

    def visit_FuncDef(self, node):
        self.current_function = node.decl.name
        self.generic_visit(node)
        self.current_function = None
        self.declared_vars = {}    

    def visit_FuncCall(self, node):
        check_unsafe_write_function_calls(node, self.declared_vars, self.current_function)
        self.generic_visit(node)

    # Every function or condition has a compound
    def visit_Compound(self, node):
        items = node.block_items
        self.generic_visit(node)

    def visit_ArrayDecl(self, node):

        array_name = node.type.declname
        array_size = int(node.dim.value) if node.dim is not None else None
        array_type = node.type.type.names[0]

        array_info = {
            'size': array_size,
            'type': array_type
        }

        self.declared_vars[array_name] = array_info
        

