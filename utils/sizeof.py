from pycparser import c_ast

from utils.log import log

# Source: https://os.mbed.com/handbook/C-Data-Types#integer-data-types
# number of bytes sizeof evaluates to
sizeof_mapping = {
    'char': 1,
    'signed char': 1,
    'short': 2,
    'unsigned short': 2,
    'wchar_t': 2,
    'int': 4,
    'unsigned int': 4,
    'long': 4, 
    'unsigned long': 4,
    'unsigned long long': 8,
    'long long': 8,
    'int64_t': 8
}

def node_is_negation(node):
    return isinstance(node, c_ast.UnaryOp) and node.op == '-'


def node_is_sizeof(node):
    return isinstance(node, c_ast.UnaryOp) and node.op == 'sizeof' 

def resolve_sizeof_node(node):
    data_type = node.expr.type.type.names[0]
    try: 
        return sizeof_mapping[data_type]
    except KeyError:
        log(node, f'The type: `{data_type}` has not been implemented')
        print('See sizeof.py')
        return 1