# Correlates to: https://cwe.mitre.org/data/definitions/787.html

from pycparser import c_ast
from print_utils.log import log

# Keep track of current context (scope). space allocated on the stack is (in most cases) only relevant on the current function's level
def track_current_scope(self, node):
    self.current_function = node.decl.name
    self.generic_visit(node)
    self.current_function = None


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

class BufferOverflowVisitor(c_ast.NodeVisitor):
    def __init__(self, buffer_overflows):
        self.buffer_overflows = buffer_overflows
        self.current_function = None
        self.modified_code = False

    def visit_FuncDef(self, node):
        track_current_scope(self, node)


    def visit_Assignment(self, node): 
        handle_array_assignment(self, node)


    def visit_Assignment(self, node):
        relevant_overflows = [overflow for overflow in self.buffer_overflows if overflow['procedure'] == self.current_function and overflow['line'] == node.coord.line]
        if relevant_overflows:
            for overflow in relevant_overflows:
                self.correct_array_access(node, overflow)

        
        
    def correct_array_access(self, node, overflow):
        if isinstance(node.lvalue, c_ast.ArrayRef):
        
            array_name = node.lvalue.name.name
            index = node.lvalue.subscript

            if isinstance(index, c_ast.Constant):
                index_value = int(index.value)
                array_size = overflow['size']
                print(overflow)
                
                response = ''
                while response.lower() != 'y' and response.lower() != 'n':
                    log(node.lvalue, f'Access out of bounds {array_name}[{index_value}], \nwould you like to auto correct to last index({array_size -1})? y/n', 'warning')
                    response = input()
                    print(response)

                if response == 'y':
                    node.lvalue.subscript.value = str(array_size - 1)
                    log(node.lvalue, f"Correction applied to array '{array_name}' access at index {index_value}", "info", True, True)
                    self.modified_code = True
            else:
                log(node.lvalue, f'index value range {overflow["index"]["start"]} and {overflow["index"]["end"]}', 'warning')
                # TODO: correct wrapping for loop

                

                