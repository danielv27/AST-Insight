from pycparser.c_ast import FuncCall, ID

def find_array_decl_of_strlen(node: FuncCall, array_declarations = None):
    arg = node.args.exprs[0]
    if array_declarations and isinstance(arg, ID):
        return array_declarations[arg.name]