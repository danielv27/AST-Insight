from pycparser.c_ast import FuncCall, ID
from pycparser import c_ast

strlen_like_functions = [
    'strlen',
    'wcslen'
]

def is_strlen_function(node):
    return isinstance(node, c_ast.FuncCall) and node.name.name in strlen_like_functions

def find_size_of_strlen(node: FuncCall, variable_declarations):
    arg = node.args.exprs[0]
    if variable_declarations and isinstance(arg, ID) and variable_declarations[arg.name]:
        value = variable_declarations[arg.name].value.split('"')[1]
        print('value is', value)
        return len(value)