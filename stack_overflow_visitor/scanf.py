from pycparser import c_ast
from print_utils.log import log

def validate_arg_amount(node, format_parts, additional_args):
    if len(node.args.exprs) < 2:
        log(node, f"Scanf requires atleast 2 arguments")
        return
    placeholder_count = len(format_parts)
    argument_count = len(additional_args)
    if len(format_parts) > len(additional_args):
        log(node, f"Insufficient arguments passed to scanf: Only {argument_count} arguments while having {placeholder_count} placeholders)")
        return False
    elif len(format_parts) < len(additional_args):
        log(node, f"Excessive arguments passed to scanf: Only {placeholder_count} placeholders while having {argument_count} arguments)")
        return False
    return True


# Returns true if the AST was modifed, returns false otherwise
# TODO: Not inportant at the moment but only generate new file if a modification was made to the AST
def check_scanf(node, declared_arrays):

    log(node, "Checking usage of scanf", "info", True, False)
    modified = False
    
    format_string = node.args.exprs[0]
    format_parts = format_string.value.strip('"').split('%')[1:]
    additional_args = node.args.exprs[1:]

    if not validate_arg_amount(node, format_parts, additional_args):
        return False   

    for index, part in enumerate(format_parts):

        current_arg = additional_args[index].name
        if not current_arg in declared_arrays:
            log(node.args, f"Variable '{current_arg}' is not an array", "warning")
            return False

        
        array_info = declared_arrays[current_arg]
        array_size = array_info['size']

        
        max_chars_str = ''.join(filter(str.isdigit, part))
        format_str = ''.join(filter(str.isalpha, part))
        if(len(max_chars_str) == 0):
            log(node, f'No max length specified in scanf() for argument `{current_arg}` at index: {index}', 'error', True, False)
            log(node, "Modifying to correct max size", 'fixed', False)
            node.args.exprs[index] = c_ast.Constant(type='string', value=f'"%{array_size - 1}{part}"')
        else:
            
            format_max_size = int(max_chars_str)
            
            # TODO: change these prints to use log instead
            if(format_max_size == array_size):
                print(f'Warning in BLA(): Format string size %{part} should account for null terminator byte (max size = {array_size - 1})')
            elif(format_max_size > array_size):
                print(f'Warning in BLA(): Format string size %{part} is bigger than max allowed size of array {current_arg}(max size = {array_size - 1})')
            else:
                return
            print("Modifying to correct max size")
            node.args.exprs[index] = c_ast.Constant(type='string', value=f'"%{array_size - 1}{format_str}"') 
    
