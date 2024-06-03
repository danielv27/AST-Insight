from stack_overflow_visitor.scanf import check_scanf

def check_memcpy(node, array_decls):
    if node.name.name == 'memcpy':
        print('memcpy du')

def check_gets(node, array_decls):
    if node.name.name == 'gets':
        print('in gets')


def check_unsafe_write_function_calls(node, declared_vars, allocated_sizes, current_function):
    if(node.name.name == 'scanf'):
        check_scanf(node, declared_vars, current_function)
    elif node.name.name in ['strcpy', 'memcpy']:
        check_heap_overflow(node, allocated_sizes, current_function)

def check_heap_overflow(node, allocated_sizes, current_function):
    pass