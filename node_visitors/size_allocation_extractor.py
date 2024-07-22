from pycparser import c_ast

# Arrays might have different strucutures when initialized or assigned . This needs to be handled Via a node visitor.
# e.g. for expression *buffer = (char *)malloc((10)*sizeof(char)); we only care about the malloc node (not the (char *) cast)
class SizeAllocationExtractor(c_ast.NodeVisitor):
    def __init__(self):
        self.complex = False
        self.size_node = None
    def visit_FuncCall(self, node):
        if node.name.name == 'malloc':
            self.size_node = node.args.exprs[0]
            if not isinstance(self.size_node, c_ast.Constant):
                self.complex = True
            
    