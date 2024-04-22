# Correlates to: https://cwe.mitre.org/data/definitions/787.html

from pycparser import c_ast

def check_scanf(node, array_decls):
    if node.name.name != 'scanf':
        return
    print('in scanf')
    if len(node.args.exprs) < 2:
        print("Error: scanf call with insufficient arguments")
        return
    format_string = node.args.exprs[0]
    format_parts = format_string.value.strip('"').split('%')[1:]
    additional_args = node.args.exprs[1:]

    if len(format_parts) > len(additional_args):
        print("Error: insufficient arguments passed to scanf")
        return
    elif len(format_parts) < len(additional_args):
        print("Warning: Unused arguments passed to scanf")

    for index, part in enumerate(format_parts):
        max_chars_str = ''.join(filter(str.isdigit, part))
        if(len(max_chars_str) == 0):
            print(f'Warning: no max length specified on argument %{part} at index: {index}')
        else:
            current_arg = additional_args[index].name
            format_max_size = int(max_chars_str)
            print(array_decls[current_arg]['size'])
            # the size can be at most size -1 of the buffer. This is because there needs to be one byte reserved for the null terminator
            array_size = array_decls[current_arg]['size']
            if(format_max_size == array_size):
                print(f'Warning: Format string size %{part} should account for null terminator byte (max size = buf_size - 1 = {array_size - 1})')
            elif(format_max_size > array_size):
                print(f'Warning: Format string size %{part} is bigger than max allowed size of array {current_arg}(size - 1 = {array_size})')
            print(format_max_size)

        

        print(array_decls[current_arg])
        pass
    

def check_memcpy(node, array_decls):
    if node.name.name == 'memcpy':
        print('in memcpy')

def check_gets(node, array_decls):
    if node.name.name == 'gets':
        print('in gets')


def check_unsafe_write_function_calls(node, array_decls):

    check_scanf(node, array_decls)
    check_memcpy(node, array_decls)
    check_gets(node, array_decls)

class BufferOverflowVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.current_function = None
        self.array_decls = {}

    def visit_FuncDef(self, node):
        self.current_function = node.decl.name
        self.generic_visit(node)
        self.current_function = None
        self.array_decls = {}    

    def visit_If(self, node):
        pass

    def visit_FuncCall(self, node):
        check_unsafe_write_function_calls(node, self.array_decls)
        self.generic_visit(node)

    # Every function or condition has a compound
    def visit_Compound(self, node):
        items = node.block_items
        self.generic_visit(node)

    def visit_ArrayDecl(self, node):
        array_info = {'size': int(node.dim.value), 'type': node.type.type.names[0], 'check_upper_bound': False, 'check_lower_bound': False}
        self.array_decls[node.type.declname] = array_info
        

