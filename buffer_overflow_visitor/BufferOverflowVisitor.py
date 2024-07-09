# Correlates to: https://cwe.mitre.org/data/definitions/787.html
from numbers import Number
from pycparser import c_ast
from print_utils.log import log



class BufferOverflowVisitor(c_ast.NodeVisitor):
    def __init__(self, buffer_overflows):
        self.buffer_overflows = buffer_overflows
        self.current_function = None
        self.modified_code = False

    def visit_FuncDef(self, node): self.track_current_function(node)

    # Keep track of current context (scope). space allocated on the stack is (in most cases) only relevant on the current function's level
    def track_current_function(self, node):
        self.current_function = node
        self.generic_visit(node)
        self.current_function = None

    def current_function_name(self):
        if self.current_function is None:
            return None
        return self.current_function.decl.name


    def visit_For(self, node):
        self.generic_visit()

    def visit_Assignment(self, node):
        relevant_overflows = [overflow for overflow in self.buffer_overflows if overflow['procedure'] == self.current_function_name() and overflow['line'] == node.coord.line]
        if relevant_overflows:
            for overflow in relevant_overflows:
                self.correct_array_access(node, overflow)

    def correct_array_access_by_value(self, node, overflow):
        
        array_size = overflow['size']
        index_value = overflow['index']
        array_name = node.lvalue.name.name
        subscript = node.lvalue.subscript

        def is_constant():
            return isinstance(subscript, c_ast.Constant)
        def is_variable():
            return isinstance(subscript, c_ast.ID)
            pass
        
        response = ''
        while response.lower() != 'y' and response.lower() != 'n':
            if is_constant():
                log(node.lvalue, f'Access out of bounds {array_name}[{index_value}], \nwould you like to auto correct to last index({array_size -1})? y/n')
                response = input()
            elif is_variable():
                log(node.lvalue, f'Access out of bounds {array_name}[{subscript.name}], not implemented press y/n to continue')
                response = input()


        if response == 'y':

            if is_constant():
                node.lvalue.subscript.value = str(array_size - 1)
                log(node.lvalue, f"Corrected '{array_name}[{index_value}]' to last index access '{array_name}[{array_size - 1}]'", "fixed", True, True)
                self.modified_code = True

            elif is_variable():
                print("TODO")
            

    def correct_array_access_by_range(self, node, overflow):
        print('correct_array_access_by_range')
        pass
        
    def correct_array_access(self, node, overflow):
        if isinstance(node.lvalue, c_ast.ArrayRef):
        
            index = node.lvalue.subscript

            if isinstance(overflow['index'], Number): self.correct_array_access_by_value(node, overflow)

            else: self.correct_array_access_by_range(node, overflow)

                

                