from scanf import check_scanf

def check_memcpy(node, array_decls):
    if node.name.name == 'memcpy':
        print('in memcpy')

def check_gets(node, array_decls):
    if node.name.name == 'gets':
        print('in gets')


def check_unsafe_write_function_calls(node, declared_vars, current_function):

    check_scanf(node, declared_vars, current_function)
    check_memcpy(node, declared_vars)
    check_gets(node, declared_vars)