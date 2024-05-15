def check_scanf(node, declared_vars, current_function):
    if node.name.name != 'scanf':
        return
    if len(node.args.exprs) < 2:
        print(f"Error in {current_function}(): scanf call with insufficient arguments")
        return
    format_string = node.args.exprs[0]
    format_parts = format_string.value.strip('"').split('%')[1:]
    additional_args = node.args.exprs[1:]

    if len(format_parts) > len(additional_args):
        print(f"Error in {current_function}(): insufficient arguments passed to scanf (More format strings than args)")
        return
    elif len(format_parts) < len(additional_args):
        print(f"Warning in {current_function}(): Excessive arguments passed to scanf (More args than format strings)")

    for index, part in enumerate(format_parts):
        current_arg = additional_args[index].name
        if not current_arg in declared_vars:
            print(f'Error in {current_function}(): {current_arg} is not declared')
            return 
        
        max_chars_str = ''.join(filter(str.isdigit, part))
        if(len(max_chars_str) == 0):
            print(f'Warning in {current_function}: no max length specified on argument %{part} at index: {index}')
        else:
            
            format_max_size = int(max_chars_str)
            # the size can be at most size -1 of the buffer. This is because there needs to be one byte reserved for the null terminator
            array_size = declared_vars[current_arg]['size']
            if(format_max_size == array_size):
                print(f'Warning in {current_function}(): Format string size %{part} should account for null terminator byte (max size = buf_size - 1 = {array_size - 1})')
            elif(format_max_size > array_size):
                print(f'Warning in {current_function}(): Format string size %{part} is bigger than max allowed size of array {current_arg}(size - 1 = {array_size})')
    

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