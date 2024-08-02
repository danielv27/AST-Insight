from numbers import Number
from pycparser import c_ast, c_generator
from node_visitors.data_type_extractor import DataTypeExtractor
from node_visitors.identifier_extractor import IdentifierExtractor
from node_visitors.heap_allocation_extractor import ArrayAllocationExtractor
from node_visitors.constant_evaluator import ConstantEvaluator
from node_visitors.name_extractor import NameExtractor
from utils.log import log
from math import ceil
from utils.sizeof import sizeof_mapping, node_is_sizeof, node_is_negation

from utils.strlen import find_size_of_strlen, is_strlen_function

UNKNOWN = 'unknown'


class BufferOverflowVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.suggestions = []
        self.current_function = None
        self.current_loops = {}
        self.variable_declarations = {}
        self.array_declarations = {}
        self.variable_constrainsts = {}

    def evaluate(self, node):
        if isinstance(node, Number):
            return node
        if isinstance(node, c_ast.Constant) and node.type == 'int':
            return int(node.value)
        if isinstance(node, c_ast.ID):
            return self.evaluate(self.variable_declarations[node.name])
        if node_is_negation(node):
            return -1 * self.evaluate(node.expr)
        if node_is_sizeof(node):
            type_name = node.expr.type.type.names[0]
            if type_name in sizeof_mapping:
                return sizeof_mapping[type_name]
            print(f'NOTE: sizeof({type_name}) not implemented, defaulting to 1')
            return 1
        if isinstance(node, c_ast.UnaryOp) and node.op == '&':
            return self.evaluate(node.expr)
        if is_strlen_function(node):
            return find_size_of_strlen(node, self.variable_declarations)
        if isinstance(node, c_ast.BinaryOp):
            match node.op:
                case '+': return self.evaluate(node.left) + self.evaluate(node.right)
                case '-': return self.evaluate(node.left) - self.evaluate(node.right)
                case '*': return self.evaluate(node.left) * self.evaluate(node.right)
                case '/': return self.evaluate(node.left) / self.evaluate(node.right)
        log(node, f'Didnt match any node in evaluate on {node}')

    def visit_FuncDef(self, node):
        self.track_current_function(node)

    def visit_For(self, node):
        self.track_current_loop(node)

    def visit_While(self, node):
        self.track_current_loop(node)

    # TODO later
    def visit_If(self, node):
       state_before_cond = dict(self.variable_constrainsts)
       self.track_current_condition(node.cond)
       self.generic_visit(node)
       self.variable_constrainsts = state_before_cond

    def visit_FuncCall(self, node):
        self.handle_memory_function(node)
        self.generic_visit(node)

    def visit_Decl(self, node):
        if node.init:
            self.variable_declarations[node.name] = node.init
        self.handle_array_allocation(node)

 
    def visit_Assignment(self, node):
        # If variable is assigned to another variable make them refer to the same size node
        if isinstance(node.lvalue, c_ast.ID) and isinstance(node.rvalue, c_ast.ID) and self.array_declarations[node.rvalue.name]:
            self.array_declarations[node.lvalue.name]['size_node'] = self.array_declarations[node.rvalue.name]['size_node']
            return

        if isinstance(node.lvalue, c_ast.ID):
            var_name = node.lvalue.name
            self.variable_declarations[var_name] = node.rvalue

        self.handle_array_allocation(node)

        if isinstance(node.lvalue, c_ast.ArrayRef):
            self.check_array_access(node, True)
        if isinstance(node.rvalue, c_ast.ArrayRef):
            self.check_array_access(node, False)

    def current_function_name(self):
        if self.current_function is None:
            return None
        return self.current_function.decl.name

    def track_current_function(self, node):
        self.current_function = node
        self.generic_visit(node)
        self.current_function = None


    def get_loop_state(self, var_name):
        return self.current_loops[var_name]['start_node'], self.current_loops[var_name]['end_node'] if var_name in self.current_loops else [None, None]


    def set_loop_state(self, var_name, start_node, end_node):
        self.current_loops[var_name] = {
            'start_node': start_node,
            'end_node': end_node
        }

    def track_current_loop(self, node):
        var_name = None
        end_node = None
        print('in track_current_loop')
        if isinstance(node, c_ast.For):
            if isinstance(node.init, c_ast.Assignment):
                var_name = node.init.lvalue.name
                start_node = node.init.rvalue
            else:
                var_name = node.init.decls[0].name
                start_node = node.init.decls[0].init

            end_node = node.cond.right

        elif isinstance(node, c_ast.While) and isinstance(node.cond, c_ast.BinaryOp):
            if isinstance(node.cond.left, c_ast.ID) and isinstance(node.cond.right, c_ast.Constant):
                var_name = node.cond.left.name
                if node.cond.op == '<':
                    start_node = self.variable_declarations[var_name]
                    end_node = node.cond.right
                elif node.cond.op == '>':
                    start_node = node.cond.right
                    end_node = self.variable_declarations[var_name]

            elif isinstance(node.cond.right, c_ast.ID) and isinstance(node.cond.left, c_ast.Constant):
                var_name = node.cond.right.name
                if node.cond.op == '<':
                    start_node = self.cond.left
                    end_node = self.variable_declarations[var_name]
                elif node.cond.op == '>':
                    start_node = self.variable_declarations[var_name]
                    end_node = node.cond.left

        if isinstance(end_node, c_ast.ID):
            end_node = self.variable_declarations[end_node.name]

        if var_name and start_node and end_node:
            self.set_loop_state(var_name, start_node, end_node)

        

        self.generic_visit(node)
        # Once the loop is done being visited, the tracking should be removed (no longer in the loop)
        if var_name in self.current_loops:
            del self.current_loops[var_name]



    def handle_array_allocation(self, node):
        array_extractor = ArrayAllocationExtractor(self.evaluate, self.array_declarations)
        array_extractor.visit(node)
        if array_extractor.array_declared:
            name, size, multiplier = array_extractor.get_result()
            self.set_array_state(name, size, multiplier)    


    # if is_upper_bound is set to false the constraint is the lower bound
    # Mapped to an array [lower_bound, upper_bound]
    def set_variable_constraint(self, name, value, is_upper_bound):
        if not name in self.variable_constrainsts:
            self.variable_constrainsts[name] = [None, None]
        index = 1 if is_upper_bound else 0
        self.variable_constrainsts[name][index] = value

    def get_variable_constraints(self, name):
        if name in self.variable_constrainsts:
            return self.variable_constrainsts[name]
        return None

    def track_current_condition(self, cond):
        constraint = None
        print('cond is', cond)
        if isinstance(cond, c_ast.ID):
            # If the condition is an ID that means that value it truthy
            self.set_variable_constraint(cond.name, 0, False)
        if isinstance(cond, c_ast.BinaryOp):
            if isinstance(cond.left, c_ast.ID):
                constraint = self.evaluate(cond.right)
                match cond.op:
                    case '<':
                        self.set_variable_constraint(cond.left.name, constraint, True)
                    case '<=':
                        self.set_variable_constraint(cond.left.name, constraint + 1, True)
                    case '>':
                        self.set_variable_constraint(cond.left.name, constraint, False)
                    case '>=':
                        self.set_variable_constraint(cond.left.name, constraint - 1, False)
                    case '==':
                        self.set_variable_constraint(cond.left.name, constraint, True)
                        self.set_variable_constraint(cond.left.name, constraint, False)
                
            if isinstance(cond.right, c_ast.ID):
                constraint = self.evaluate(cond.left)
                match cond.op:
                    case '<':
                        self.set_variable_constraint(cond.left.name, constraint, False)
                    case '<=':
                        self.set_variable_constraint(cond.left.name, constraint - 1, False)
                    case '>':
                        self.set_variable_constraint(cond.left.name, constraint, True)
                    case '>=':
                        self.set_variable_constraint(cond.left.name, constraint + 1, True)
                    case '==':
                        self.set_variable_constraint(cond.left.name, constraint, True)
                        self.set_variable_constraint(cond.left.name, constraint, False)

            if isinstance(cond.left, c_ast.BinaryOp) and cond.op == '&&':
                self.track_current_condition(cond.left)
            if isinstance(cond.right, c_ast.BinaryOp) and cond.op == '&&':
                self.track_current_condition(cond.right)

            # Maybe TODO: if there is an or condition flip it to an and so it can be handled more easily

        if constraint:
            print("TODO: remove constraint")
        # TODO: remove condition

    def set_array_state(self, name, size_node, multiplier):
        self.array_declarations[name] = {'size_node': size_node, 'multiplier': multiplier}


    def get_array_state(self, name):
        print('arrays', self.array_declarations)
        if name in self.array_declarations:
            array_state = self.array_declarations[name]
            return array_state['size_node'], array_state['multiplier']
        print('get_array_state found no result')
        return None, None



    def generate_suggestion(self, node, description):
        generator = c_generator.CGenerator()
        suggestion_code = generator.visit(self.current_function)
        line = node.coord.line - self.current_function.coord.line + 1 if isinstance(node, c_ast.Node) else None
        self.suggestions.append({
            'function_name': self.current_function_name(),
            'description': description,
            'code': suggestion_code,
            'line': line
        })

    def check_array_access(self, node, left = True):
        array_acces_node = node.lvalue if left else node.rvalue
        array_name = array_acces_node.name.name
        print('check array access array name:',array_name)
        array_size_node, multiplier = self.get_array_state(array_name)
        print('array_size_node', array_size_node)

        # TODO later
        if array_size_node == UNKNOWN:
            access_value = self.evaluate(array_acces_node.subscript)
            print('array_size_node is unknown')
            return
        print('in check_array_access')
        print('evaluate(array_size_node)', self.evaluate(array_size_node))
        print('evaluate(multiplier)', self.evaluate(multiplier))

        array_size = self.evaluate(array_size_node)
        array_multiplier = self.evaluate(multiplier)
        subscript_node = array_acces_node.subscript
        if isinstance(subscript_node, c_ast.ID) and subscript_node.name in self.current_loops:

            variable_name = subscript_node.name

            _, end_node = self.get_loop_state(variable_name)

            end_node_value = self.evaluate(end_node)

            print('end_node', end_node)
            print(self.variable_declarations)

            print(end_node_value)
            print(array_size)
            print(array_multiplier)
            if array_size // array_multiplier < end_node_value:
                self.generate_suggestion(array_size_node, f'Increase size of array `{array_name}`({array_size // array_multiplier}) to account for loop access (atleast {end_node_value})')
                self.generate_suggestion(end_node, f'Decrease loop upper bound ({end_node_value}) to stay within the bounds of the array `{array_name}` (at most {array_size // array_multiplier})')

        elif isinstance(subscript_node, c_ast.ID) and subscript_node.name in self.variable_declarations:
           
            variable_size_node = self.variable_declarations[variable_name]

            index_value = self.evaluate(variable_size_node)
            if index_value > array_size:
                self.generate_suggestion(variable_size_node, f'Change variable `{variable_name}` to a valid index (between 0 and {array_size - 1}) e.g. {array_size - 1}')
                self.generate_suggestion(array_size_node, f'Increase size of `{array_name}` to account for index access (atleast {access_value + 1} units of 1 bytes)')
        print('exit check_array_access')

    def handle_memory_function(self, node):
        func_name = node.name.name
        if func_name in ['memset', 'memmove', 'memcpy', 'strcpy', 'wmemset']:
            dest_node = node.args.exprs[0] if len(node.args.exprs) > 0 else None
            source_node = node.args.exprs[1] if len(node.args.exprs) > 1 else None
            size_node = node.args.exprs[2] if len(node.args.exprs) > 2 else None

            if isinstance(dest_node, c_ast.ID):
                dest_size_node, dest_multiplier = self.get_array_state(dest_node.name)

                if not dest_size_node:
                    return
                print('in handle_memory_function')
                print('dest_size_node',dest_size_node)

                print('dest_size_node', dest_size_node)
                print('dest_multipler', dest_multiplier)


                if(dest_size_node == UNKNOWN):
                    # TODO: if variable is read from user input or passed as an argument it is an unknown. This is to target the exposed attack surface of the program
                    return

                dest_size = self.evaluate(dest_size_node) * self.evaluate(dest_multiplier)

                print('dest_size', dest_size)

                if size_node:
                    size_node_size = self.evaluate(size_node)

                    print(size_node_size, dest_size)

                    if size_node_size > dest_size:
                        self.generate_suggestion(node, f"Reduce the number of bytes coppied in {func_name} ({size_node_size} bytes to not be larger than the destination buffer '{dest_node.name}' ({dest_size} bytes)")
                        self.generate_suggestion(node, f"Increase the size of the destination buffer in {func_name} ({dest_size // dest_multiplier} units of {self.evaluate(dest_multiplier)} bytes) to be able to hold coppied size '{dest_node.name}' ({size_node_size} bytes")

                elif source_node and isinstance(source_node, c_ast.ID) and source_node.name in self.array_declarations:
                    source_size_node, source_multiplier = self.get_array_state(source_node.name)

                    print(source_size_node)

                    source_size = self.evaluate(source_size_node) * self.evaluate(source_multiplier)

                    print('source_size', source_size)

                    if source_size > dest_size:
                        self.generate_suggestion(node, f"Increase the size of the destination buffer '{dest_node.name}' from {dest_size} bytes to be at least {source_size} bytes")



        print('exit mem function')