import sys
from parse_ast import path_to_ast, ast_to_c_file
from stack_overflow_visitor.StackOverflowVisitor import StackOverflowVisitor

sys.path.extend(['.', '..'])

if __name__ == "__main__":
    if len(sys.argv) > 1:

        file_path = sys.argv[1]

        ast = path_to_ast(file_path)
        so_visitor = StackOverflowVisitor()
        so_visitor.visit(ast)

        ast_to_c_file(ast, file_path)

    else:
        print("Please provide a filename as argument")

