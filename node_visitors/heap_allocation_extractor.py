from pycparser import c_ast

from node_visitors.constant_evaluator import ConstantEvaluator
from utils.sizeof import node_is_sizeof, resolve_sizeof_node
from utils.strlen import find_size_of_strlen


# The Idea behind this Node Visitor is to extract the node that defines the size of an operation
# Since in C sizeof() is commonly used to achieve this it is likely to not be a constant
# How this is resolved is by looking for a constant value within the node of interest
# and convert the value that sizeof resolved to as a multiplier of that constant
class HeapAllocationExtractor(c_ast.NodeVisitor):
    def __init__(self, array_declarations):
        self.size_node = None
        self.multiplier = 1
        self.array_declarations = array_declarations

    def visit_FuncCall(self, node):

        func_name = node.name.name

        if func_name in ['malloc', 'calloc', 'alloca']:
            self.size_node = node.args.exprs[0]
            if func_name == 'calloc':
                self.multiplier = node.args.exprs[1]
            
    def get_result(self):
        return self.size_node, self.multiplier
