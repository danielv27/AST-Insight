import sys
from parse_infer import run_infer, extract_buffer_overflows
from parse_ast import parse_ast, ast_to_c_file
from buffer_overflow_visitor.BufferOverflowVisitor import BufferOverflowVisitor


sys.path.extend(['.', '..'])

if __name__ == "__main__":
    if len(sys.argv) > 1:

        file_path = sys.argv[1]
        infer_output = run_infer(file_path)

        buffer_overflows = extract_buffer_overflows(infer_output)

        ast = parse_ast(file_path)
        BufferOverflowVisitor(buffer_overflows).visit(ast)
        ast_to_c_file(ast, file_path)

    else:
        print("Please provide a filename as argument")

