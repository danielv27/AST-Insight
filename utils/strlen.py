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
    if variable_declarations and isinstance(arg, ID) and arg.name in variable_declarations:
        variable = variable_declarations[arg.name]
        if isinstance(variable_declarations, c_ast.Constant):
            value = variable_declarations[arg.name].value.split('"')[1]
            return len(value)
        return 0
        