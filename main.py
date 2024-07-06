import sys
from parse_ast import parse_ast, ast_to_c_file
from stack_overflow_visitor.StackOverflowVisitor import StackOverflowVisitor

sys.path.extend(['.', '..'])

if __name__ == "__main__":
    if len(sys.argv) > 1:

        file_path = sys.argv[1]

        # Step 1: pass the program to infra to get data
        # Step 2: pass that data to the visitor
        # Step 3: inise the visitor modify the AST 
        # Step 4: ast_to_file
        

        ast = parse_ast(file_path)
        so_visitor = StackOverflowVisitor()
        so_visitor.visit(ast)

        ast_to_c_file(ast, file_path)

    else:
        print("Please provide a filename as argument")

