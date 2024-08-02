from pycparser import c_ast

from node_visitors.constant_evaluator import ConstantEvaluator
from node_visitors.data_type_extractor import DataTypeExtractor
from utils.sizeof import node_is_sizeof, resolve_sizeof_node
from utils.strlen import find_size_of_strlen
from utils.sizeof import sizeof_mapping


# The Idea behind this Node Visitor is to extract the node that defines the size of an operation
# Since in C sizeof() is commonly used to achieve this it is likely to not be a constant
# How this is resolved is by looking for a constant value within the node of interest
# and convert the value that sizeof resolved to as a multiplier of that constant


class ArrayAllocationExtractor(c_ast.NodeVisitor):
    def __init__(self, evaluate, array_declarations):
        self.name = None
        self.size_node = None
        self.multiplier = 1
        self.array_declarations = array_declarations
        self.evaluate = evaluate
        self.array_declared = False

    def set_array_state(self, name, size_node, data_type):
        self.name = name
        self.size_node = size_node
        self.multiplier = sizeof_mapping[data_type] if data_type in sizeof_mapping else 1
        self.array_declared = True

    def visit_ArrayDecl(self, node):
        print('array allocation extractor in array_decl', node)

    def visit_Decl(self, node):
        print('array allocation axtractor decl', node)
        data_type_extractor = DataTypeExtractor()
        data_type_extractor.visit(node)
        data_type = data_type_extractor.get_result()
        self.multiplier = sizeof_mapping[data_type] if data_type in sizeof_mapping else self.multiplier
        if isinstance(node.type, c_ast.PtrDecl):
            print('array allocation axtractor ptr decl', node)
            self.set_array_state(node.name, node.init, data_type)
            
        elif isinstance(node.type, c_ast.ArrayDecl):
            print('array allocation axtractor array decl', node)
            print('data_type', data_type)
            data_type_size = sizeof_mapping[data_type] if data_type in sizeof_mapping else 1
            self.set_array_state(node.name, self.evaluate(node.type.dim) * data_type_size, data_type)
            pass
    
    def visit_ID(self, node):
        if self.name is None:
            self.name = node.name
            

    def visit_Assignment(self, node):
        if isinstance(node.lvalue, c_ast.UnaryOp) and node.lvalue.op == '*':
            print('array allocation extractor in assignment', node, self.array_declarations)
            print(self.array_declarations)
        self.generic_visit(node)

    def visit_FuncCall(self, node):
        func_name = node.name.name
        if func_name in ['malloc', 'calloc', 'alloca']:
            multiplier = self.array_declarations[self.name]['multiplier'] if self.name in self.array_declarations else 1
            self.set_array_state(self.name, node.args.exprs[0], multiplier)
            
    def get_result(self):
        return self.name, self.size_node, self.multiplier
