from numbers import Number
from pycparser import c_ast, c_generator
from print_utils.log import log

class IdentifierVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.variables = []
    def visit_ID(self, node):
        self.variables.append(node.name)

class BufferOverflowVisitor(c_ast.NodeVisitor):
    def __init__(self, buffer_overflows):
        self.buffer_overflows = buffer_overflows
        self.suggestions = []
        self.current_function = None
        self.current_loops = {}
        self.modified_code = False

    def visit_FuncDef(self, node): 
        self.track_current_function(node)

    def visit_For(self, node):
        self.track_current_loop(node)

    def visit_Assignment(self, node):
        self.handle_assignment(node)

    def current_function_name(self):
        if self.current_function is None:
            return None
        return self.current_function.decl.name

    def track_current_function(self, node):
        self.current_function = node
        self.generic_visit(node)
        self.current_function = None

    def track_current_loop(self, node):
        var_name = node.init.decls[0].name

        self.current_loops[var_name] = node
        self.generic_visit(node)
        del self.current_loops[var_name]

    def handle_assignment(self, node):
        relevant_overflows = [overflow for overflow in self.buffer_overflows if overflow['procedure'] == self.current_function_name() and overflow['line'] == node.coord.line]
        if relevant_overflows:
            for overflow in relevant_overflows:
                self.correct_array_access(node, overflow)

    def generate_suggestion(self, description):
        generator = c_generator.CGenerator()
        suggestion_code = generator.visit(self.current_function)
        self.suggestions.append({
            'description': description,
            'code': suggestion_code
        })

    def correct_array_access_by_value(self, node, overflow):
        array_size = overflow['size']
        index_value = overflow['index']
        array_name = node.lvalue.name.name
        subscript = node.lvalue.subscript

        if isinstance(subscript, c_ast.Constant):
            log(node.lvalue, f'Access out of bounds {array_name}[{index_value}], suggesting correction to last index ({array_size -1})')
            original_subscript = subscript.value
            node.lvalue.subscript.value = str(array_size - 1)
            self.generate_suggestion(f"At {node.coord}, Correct array access '{array_name}[{index_value}]' to last index access '{array_name}[{array_size - 1}]'")
            node.lvalue.subscript.value = original_subscript
    

    def correct_array_access_by_range(self, node, overflow):
        array_name = node.lvalue.name.name
        subscript = node.lvalue.subscript
        start_offset = overflow['index']['start']
        end_offset = overflow['index']['end']

        log(node.lvalue, f'Access out of bounds `{array_name}` in a loop, Offset [{start_offset}, {end_offset}]\n Suggesting wrapping loop to correct range')

        visitor = IdentifierVisitor()
        visitor.visit(subscript)

        if len(visitor.variables) == 0:
            log(node, 'Unexpected evaluation of subscript', 'warning')
            return
        
        if len(visitor.variables) > 1:
            log(node, 'Current implementation supports at most 1 variable as an index', 'warning')
            return

        var_name = visitor.variables[0]
        size = overflow['size']
        loop_node = self.current_loops[var_name]

        original_cond_value = loop_node.cond.right.value
        original_init_value = loop_node.init.decls[0].init.value

        loop_node.cond.right.value = str(size - start_offset)
        loop_node.init.decls[0].init.value = str(0 - start_offset)

        self.generate_suggestion(f"At {node.coord} Correct wrapping loop to ensure '{var_name}' stays within bounds")
        loop_node.cond.right.value = original_cond_value
        loop_node.init.decls[0].init.value = original_init_value

    def correct_array_access(self, node, overflow):
        if isinstance(node.lvalue, c_ast.ArrayRef):
            if isinstance(overflow['index'], Number): 
                print('by value')
                self.correct_array_access_by_value(node, overflow)
            else: 
                self.correct_array_access_by_range(node, overflow)
