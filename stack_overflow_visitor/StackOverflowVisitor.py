# Correlates to: https://cwe.mitre.org/data/definitions/787.html

from pycparser import c_ast
from stack_overflow_visitor.unsafe_functions import check_unsafe_write_function_calls
from print_utils.log import log

# Keep track of current context (scope). space allocated on the stack is (in most cases) only relevant on the current function's level
def track_current_scope(self, node):
    self.current_function = node.decl.name
    self.generic_visit(node)
    self.current_function = None
    self.declared_arrays = {} 


def track_array_allocations(self, node):
    array_name = node.type.declname
    array_size = int(node.dim.value) if node.dim is not None else None
    array_type = node.type.type.names[0]

    array_info = {
        'size': array_size,
        'type': array_type,
        'node': node
    }
    self.declared_arrays[array_name] = array_info
    self.generic_visit(node)



def handle_array_assignment(self, node):
    if isinstance(node.lvalue, c_ast.ArrayRef):
        array_name = node.lvalue.name.name
        if array_name in self.declared_arrays:
            array_info = self.declared_arrays[array_name]
            array_size = array_info['size']
            index = node.lvalue.subscript

            if isinstance(index, c_ast.Constant):
                index_value = int(index.value)
                is_error = False
                if index_value < 0:
                    log(node.lvalue, "Array access with negative value", "warning")
                    is_error = True
                elif index_value >= array_size:
                    log(node.lvalue, f"Array access '{array_name}[{index_value}]' out of bounds. Array size is {array_size}", "error", True, False)
                    is_error = True
                
                if is_error:
                    log(array_info['node'], f"{array_name}[{array_size}] decleration location", "info", False, True)


    self.generic_visit(node)

def handle_unsafe_functions(self, node):
    check_unsafe_write_function_calls(node, self.declared_arrays)
    self.generic_visit(node)

class StackOverflowVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.current_function = None
        self.declared_arrays = {}
        self.modified_code = False
        

    # def visit_Compound(self, node): print(node)
    

    def visit_FuncDef(self, node): track_current_scope(self, node)
    def visit_ArrayDecl(self, node): track_array_allocations(self, node)
    def visit_Assignment(self, node): handle_array_assignment(self, node)
    def visit_FuncCall(self, node): handle_unsafe_functions(self, node)
