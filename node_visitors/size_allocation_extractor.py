from pycparser import c_ast

from node_visitors.constant_evaluator import ConstantEvaluator
from utils.sizeof import node_is_sizeof, resolve_sizeof_node
from utils.strlen import find_array_decl_of_strlen

class HeapAllocationSizeExtractor(c_ast.NodeVisitor):
    def __init__(self, array_declarations):
        self.size_node = None
        self.multiplier = 1
        self.array_declarations = array_declarations

    def visit_FuncCall(self, node):

        func_name = node.name.name

        if func_name == 'strlen':
            array_decl = find_array_decl_of_strlen(node, self.array_declarations)
            print('in strlen array_decl', array_decl)
            if array_decl:
                # This implementation assuems that strlen() is not used in the size argument which is not conventioal anyways
                self.size_node = array_decl['size_node']
                self.multiplier *= array_decl['multiplier']

        self.generic_visit(node)

    def visit_BinaryOp(self, node):
        if isinstance(node.left, c_ast.Constant):
            self.size_node = node.left
            if node.op == '*' and node_is_sizeof(node.right):
                self.multiplier *= resolve_sizeof_node(node.right)
        elif isinstance(node.right, c_ast.Constant):
            self.size_node = node.right
            if node.op == '*' and node_is_sizeof(node.left):
                self.multiplier *= resolve_sizeof_node(node.left)
        self.generic_visit(node)
            
    def get_result(self):
        return self.size_node, self.multiplier
