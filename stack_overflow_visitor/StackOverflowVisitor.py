# Correlates to: https://cwe.mitre.org/data/definitions/787.html

from pycparser import c_ast
from stack_overflow_visitor.unsafe_functions import check_unsafe_write_function_calls

def getFunctionsFromCompound(self, node):
    result = {}
    for item in node.block_items:
        function_name = None
        function_node = None

        if(isinstance(item, c_ast.Decl) and item.init):
            function_name = item.name
            function_node = item.init
        elif(isinstance(item, c_ast.Assignment)):
            function_name = item.lvalue.expr.name
            function_node = item.rvalue
        else:
            continue
        if(isinstance(function_node, c_ast.FuncCall)):
            result[function_name] = function_node
    return result


class StackOverflowVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.current_function = None
        self.declared_vars = {}
        self.allocated_sizes = {}

    def visit_FuncDef(self, node):
        self.current_function = node.decl.name
        self.generic_visit(node)
        self.current_function = None
        self.declared_vars = {}    

    def visit_Compound(self, node):

        print(getFunctionsFromCompound(self, node))
        self.generic_visit(node)
        # print(isinstance(node.block_items.type, c_ast.PtrDecl))

    def visit_FuncCall(self, node):
        check_unsafe_write_function_calls(node, self.declared_vars, self.allocated_sizes, self.current_function)
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
    
    # def visit_Assignment(self, node):
    #     print(node)
    #     if isinstance(node.rvalue, c_ast.FuncCall):
    #         func_name = node.rvalue.name.name
    #         if func_name in ['malloc', 'calloc', 'realloc']:
    #             var_name = node.lvalue.name
    #             size_expr = node.rvalue.args.exprs[0]
    #             # Simplified size calculation (you may need to handle more complex cases)
    #             size = int(size_expr.value)
    #             self.allocated_sizes[var_name] = size
        
        

