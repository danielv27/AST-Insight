from pycparser import c_ast

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
        print(f"Error in {current_function}(): Excessive arguments passed to scanf (More args than format strings)")

    for index, part in enumerate(format_parts):
        current_arg = additional_args[index].name
        array_info = declared_vars[current_arg]
        array_size = array_info['size']
        if not current_arg in declared_vars:
            print(f'Error in {current_function}(): {current_arg} is not declared')
            return 
        
        max_chars_str = ''.join(filter(str.isdigit, part))
        format_str = ''.join(filter(str.isalpha, part))
        print('format str:', format_str)
        if(len(max_chars_str) == 0):
            print(f'Problem when using scanf in {current_function}(): no max length specified on argument %{part} at index: {index}')
            print("Modifying to correct max size")
            node.args.exprs[index] = c_ast.Constant(type='string', value=f'"%{array_size - 1}{part}"')
        else:
            
            format_max_size = int(max_chars_str)
            
            if(format_max_size == array_size):
                print(f'Warning in {current_function}(): Format string size %{part} should account for null terminator byte (max size = {array_size - 1})')
            elif(format_max_size > array_size):
                print(f'Warning in {current_function}(): Format string size %{part} is bigger than max allowed size of array {current_arg}(max size = {array_size - 1})')
            else:
                return
            print("Modifying to correct max size")
            node.args.exprs[index] = c_ast.Constant(type='string', value=f'"%{array_size - 1}{format_str}"') 
    
