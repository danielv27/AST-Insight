from pycparser import c_ast

from node_visitors.value_simplifier import ConstantEvaluator
from utils.sizeof import node_is_sizeof, resolve_sizeof_node




# Arrays might have different strucutures when initialized or assigned . This needs to be handled Via a node visitor.
# e.g. for expression *buffer = (char *)malloc((10)*sizeof(char)); we only care about the malloc node (not the (char *) cast)
class HeapAllocationSizeExtractor(c_ast.NodeVisitor):
    def __init__(self):
        self.size_node = None
        self.multiplier = 1

    def visit_FuncCall(self, node):
        if node.name.name == 'malloc':
            value_simplifer = ConstantEvaluator()
            value_simplifer.visit(node)
            
            first_expr = node.args.exprs[0]

            if isinstance(first_expr, c_ast.Constant):
                self.size_node = first_expr
                return
            
            if isinstance(first_expr, c_ast.BinaryOp):
                if isinstance(first_expr.left, c_ast.Constant):
                    self.size_node = first_expr.left
                    if first_expr.op == '*' and node_is_sizeof(first_expr.right):
                        self.multiplier *= resolve_sizeof_node(first_expr.right)
                elif isinstance(first_expr.right, c_ast.Constant):
                    self.size_node = first_expr.right
                    if first_expr.op == '*' and node_is_sizeof(first_expr.left):
                        self.multiplier *= resolve_sizeof_node(first_expr.left)


        if node.name.name == 'calloc':
            print('TODO: here I can add the size of each el as a multiplier, abstracting this')

            
            
    