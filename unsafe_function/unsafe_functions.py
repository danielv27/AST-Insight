from unsafe_function.scanf import check_scanf

def check_memcpy(node, array_decls):
    if node.name.name == 'memcpy':
        print('memcpy du')

def check_gets(node, array_decls):
    if node.name.name == 'gets':
        print('in gets')


def check_unsafe_write_function_calls(node, declared_arrays):
    if(node.name.name == 'scanf'):
        check_scanf(node, declared_arrays)