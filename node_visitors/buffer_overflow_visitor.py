from numbers import Number
from pycparser import c_ast, c_generator
from node_visitors.identifier_extractor import IdentifierExtractor
from node_visitors.size_node_and_multiplier_extractor import SizeNodeAndMultiplierExtractor
from node_visitors.constant_evaluator import ConstantEvaluator
from utils.log import log
from math import ceil

from utils.strlen import find_array_decl_of_strlen
        
class BufferOverflowVisitor(c_ast.NodeVisitor):
    def __init__(self, buffer_overflows):
        self.buffer_overflows = buffer_overflows
        self.suggestions = []
        self.current_function = None
        self.current_loops = {}
        self.variable_declarations = {}
        self.array_declarations = {}

    def visit_FuncDef(self, node):
        self.track_current_function(node)

    def visit_For(self, node):
        self.track_current_loop(node)

    def visit_While(self, node):
        self.track_current_loop(node)

    # TODO: should be pretty easy to remove overflows from here
    def visit_FuncCall(self, node):
        self.handle_memory_function(node)
        self.generic_visit(node)

    def visit_Decl(self, node):
        if isinstance(node.type, c_ast.PtrDecl) and node.init:
            size_extractor = SizeNodeAndMultiplierExtractor(self.array_declarations)
            size_extractor.visit(node.init)

            size_node, multiplier = size_extractor.get_result()

            self.set_array_state(node.name, size_node, multiplier)

        if isinstance(node.type, c_ast.ArrayDecl):
            # Simplifies consant expressions
            const_evaluator = ConstantEvaluator()
            const_evaluator.visit(node)
            self.set_array_state(node.name, node.type.dim, 1)

        if isinstance(node.type, c_ast.TypeDecl):
            var_name = node.name
            if isinstance(node.init, c_ast.FuncCall):
                if node.init.name.name == 'strlen':
                    self.variable_declarations[var_name] = find_array_decl_of_strlen(node.init, self.array_declarations)
            else:
                self.variable_declarations[var_name] = node.init
        

    def visit_Assignment(self, node):
        if isinstance(node.lvalue, c_ast.ID) and isinstance(node.rvalue, c_ast.ID) and self.array_declarations[node.rvalue.name]:
            self.array_declarations[node.lvalue.name] = self.array_declarations[node.rvalue.name]
            return
        
        if isinstance(node.lvalue, c_ast.ID):
            if isinstance(node.rvalue, c_ast.FuncCall):
                self.variable_declarations[node.lvalue.name] = find_array_decl_of_strlen(node.rvalue, self.array_declarations)
        
        size_extractor = SizeNodeAndMultiplierExtractor(self.array_declarations)
        size_extractor.visit(node.rvalue)

        size_node, multiplier = size_extractor.get_result()

        # Heap allocation extractor will only set a size node when there is a heap allocation inside the node
        if size_node is not None:
            self.set_array_state(node.lvalue.name, size_node, multiplier)

        relevant_overflows = self.getRelevantOverflows(node)
        if relevant_overflows:
            for overflow in relevant_overflows:
                self.correct_array_access(node, overflow)


    def current_function_name(self):
        if self.current_function is None:
            return None
        return self.current_function.decl.name

    def getRelevantOverflows(self, node):
       return [overflow for overflow in self.buffer_overflows if overflow['procedure'] == self.current_function_name() and overflow['line'] == node.coord.line]


    def track_current_function(self, node):
        self.current_function = node
        self.generic_visit(node)
        self.current_function = None


    def get_loop_state(self, var_name):
        return self.current_loops['node'], self.current_loops['start'], self.current_loops['end']
        

    def set_loop_state(self, var_name, node, start, end):
        self.current_loops[var_name] = {
            'node': node,
            'start': start,
            'end': end
        }

    def track_current_loop(self, node):
        var_name = None
        if isinstance(node, c_ast.For):
            if isinstance(node.init, c_ast.Assignment):
                var_name = node.init.lvalue.name
                start = int(node.init.rvalue.value)
            else:
                var_name = node.init.decls[0].name
                start = int(node.init.decls[0].init.value)


            print(node)
            print('start is:', start)
            
            self.current_loops[var_name] = node
            
        elif isinstance(node, c_ast.While):
            if isinstance(node.cond.left, c_ast.ID):
                var_name = node.cond.left.name
                self.current_loops[var_name] = node
        
        self.generic_visit(node)
        # Once the loop is done being visited, the tracking should be removed (no longer in the loop)
        if var_name is not None:
            del self.current_loops[var_name]

    def set_array_state(self, name, size_node, multiplier):
        self.array_declarations[name] = {'size_node': size_node, 'multiplier': multiplier}

    
    def get_array_state(self, name):
        array_state = self.array_declarations[name]
        return array_state['size_node'], array_state['multiplier']


    def generate_suggestion(self, node, description):
        generator = c_generator.CGenerator()
        suggestion_code = generator.visit(self.current_function)
        self.suggestions.append({
            'description': description,
            'code': suggestion_code,
            'line': node.coord.line - self.current_function.coord.line + 1
        })

    def suggest_constant_adjustment(self, node, overflow):
        array_name = node.lvalue.name.name
        index_value = overflow['index']
        array_size = overflow['size']
        subscript = node.lvalue.subscript
        log(node.lvalue, f'Access out of bounds {array_name}[{index_value}], suggesting correction to last index ({array_size -1})')
        original_subscript = subscript.value
        node.lvalue.subscript.value = str(array_size - 1)
        self.generate_suggestion(node, f"Correct array access '{array_name}[{index_value}]' to valid index access (0 to {array_size - 1}). e.g.:{array_name}[{array_size - 1}]")
        node.lvalue.subscript.value = original_subscript  

    def suggest_variable_adjustment(self, node, overflow):
        subscript = node.lvalue.subscript
        visitor = IdentifierExtractor()
        visitor.visit(subscript)

        var_name = visitor.variables[0]
        var_node = self.variable_declarations[var_name]

        original_value = var_node.value

        var_node.value = str(overflow['size'] - 1)
        self.generate_suggestion(var_node, f'Change variable `{var_name}` to a valid index (between 0 and {overflow["size"] - 1}) e.g. {overflow["size"] - 1}')
        var_node.value = original_value   

    def suggest_buffer_allocation_adjustment(self, node, overflow):

        array_name = node.lvalue.name.name
        array_size_node, multiplier = self.get_array_state(array_name)
        array_size = int(array_size_node.value) * multiplier

        if isinstance(overflow['index'], Number):
            minimal_size = overflow['index'] + 1
        else:
            minimal_size = overflow['index']['end'] + 1
        
        if array_size >= minimal_size:
            return
            
        original_size = array_size_node.value

        result = ceil(minimal_size / multiplier)

        array_size_node.value = str(ceil(minimal_size / multiplier))
        self.generate_suggestion(array_size_node, f"Increase size of `{array_name}` to account for index access (atleast {result} units of {multiplier} bytes)") 
        array_size_node.value = original_size

    def suggest_for_loop_adjustment(self, node, loop_node, overflow, var_name):

        size = overflow['size']
        start_offset = overflow['index']['start']

        if isinstance(loop_node.cond.right, c_ast.ID):
            print("if for loop is with ID")
            pass

        if isinstance(loop_node.cond.right, c_ast.Constant):
            original_cond_value = loop_node.cond.right.value
            loop_node.cond.right.value = str(size - start_offset)

            if isinstance(loop_node.init, c_ast.Assignment):
                original_init_value = loop_node.init.rvalue.value
                loop_node.init.rvalue.value = str(0 - start_offset)
            else:
                original_init_value = loop_node.init.decls[0].init.value
                loop_node.init.decls[0].init.value = str(0 - start_offset)


            self.generate_suggestion(loop_node, f"Adjust wrapping for loop to ensure '{var_name}' stays within bounds")
            loop_node.cond.right.value = original_cond_value

            if isinstance(loop_node.init, c_ast.Assignment):
                loop_node.init.rvalue.value = original_init_value
            else:
                loop_node.init.decls[0].init.value = original_init_value
        

    def suggest_while_loop_adjustment(self, node, loop_node, overflow, var_name):
            var_decleration = self.variable_declarations[var_name]
            size = overflow['size']
            start_offset = overflow['index']['start']

            original_var_value = var_decleration.value

            var_decleration.value = str(0 - start_offset)

            original_cond_value = loop_node.cond.right.value
            loop_node.cond.right = c_ast.Constant('int', str(size - start_offset))

            self.generate_suggestion(loop_node, f"Correct variable decleations and wrapping while loop and to ensure '{var_name}' stays within bounds")
            var_decleration.value = original_var_value
            loop_node.cond.right = original_cond_value


    # When the index of a buffer is a value it means that is is accessed with a single value (variable or constant)
    def correct_array_access_by_value(self, node, overflow):
        if isinstance(node.lvalue.subscript, c_ast.Constant):
            self.suggest_constant_adjustment(node, overflow)
        else:
            self.suggest_variable_adjustment(node, overflow)


    # When the index of a buffer is a range it means it is accessed in a loop 
    def correct_array_access_by_range(self, node, overflow):
        subscript = node.lvalue.subscript

        visitor = IdentifierExtractor()
        visitor.visit(subscript)

        if len(visitor.variables) == 0:
            log(node, 'Unexpected evaluation of subscript', 'warning')
            return
        
        if len(visitor.variables) > 1:
            log(node, 'Current implementation supports at most 1 variable as an index', 'warning')
            return

        var_name = visitor.variables[0]
        loop_node = self.current_loops[var_name]

        if isinstance(loop_node, c_ast.For):
            self.suggest_for_loop_adjustment(node, loop_node, overflow, var_name)
            
        elif isinstance(loop_node, c_ast.While):
            self.suggest_while_loop_adjustment(node, loop_node, overflow, var_name)



    def correct_array_access(self, node, overflow):
        self.suggest_buffer_allocation_adjustment(node, overflow)
        if isinstance(node.lvalue, c_ast.ArrayRef):
            if isinstance(overflow['index'], Number): 
                print('by value')
                self.correct_array_access_by_value(node, overflow)
            else: 
                print('by range')
                self.correct_array_access_by_range(node, overflow)


    def handle_memory_function(self, node):

        func_name = node.name.name
        if func_name in ['memset', 'memmove', 'memcpy', 'strcpy']:
            dest_node = node.args.exprs[0]
            source_node = node.args.exprs[1] if len(node.args.exprs) > 1 else None
            size_node = node.args.exprs[2] if len(node.args.exprs) > 2 else None

            if isinstance(dest_node, c_ast.ID) and dest_node.name in self.array_declarations:
                dest_size_node, dest_multiplier = self.get_array_state(dest_node.name)
                dest_size = int(dest_size_node.value) * dest_multiplier


                if source_node and isinstance(source_node, c_ast.ID) and source_node.name in self.array_declarations:
                    source_size_node, source_multiplier = self.get_array_state(source_node.name)
                    source_size = int(source_size_node.value) * source_multiplier

                    if source_size > dest_size:
                        self.generate_suggestion(dest_size_node, f"Adjust the size of the destination buffer '{dest_node.name}' to be at least {source_size}")

                if size_node:
                    size_extractor = SizeNodeAndMultiplierExtractor(self.array_declarations)
                    size_extractor.visit(node)

                    size_node, multiplier = size_extractor.get_result()


                    copy_size = int(size_node.value) * multiplier if size_node else None

                    result = ceil(dest_size / dest_multiplier)

                    if copy_size > dest_size:
                        self.generate_suggestion(size_node, f"Reduce the number of bytes coppied in {func_name} ({size_node.value} units of {multiplier} bytes) to not be larger than the destination buffer '{dest_node.name}' ({dest_size_node.value} units of {dest_multiplier} bytes)")
                        self.generate_suggestion(dest_size_node, f"Increase the size of the destination buffer in {func_name} ({dest_size_node.value} units of {dest_multiplier} bytes) to be able to hold coppied size '{dest_node.name}' ({size_node.value} units of {multiplier} bytes)")

                    if not size_node and source_size > dest_size:
                        self.generate_suggestion(dest_size_node, f"Increase size of the destination buffer `{dest_node.name}` ({dest_size_node.value} units of {dest_multiplier} bytes) to account for copy size (atleast {result} units of {multiplier} bytes)")
                        self.generate_suggestion(source_size_node, f"Decrease the size of the source buffer `{source_node.name}` ({source_size_node.value} units of {source_multiplier} bytes) to account for copy size (atleast {result} units of {multiplier} bytes)")