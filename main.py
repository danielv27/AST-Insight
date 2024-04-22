import sys
from parse_ast import filename_to_ast, ast_to_c
from BufferOverflowVisitor import BufferOverflowVisitor

sys.path.extend(['.', '..'])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ast = filename_to_ast(sys.argv[1])
        bo_visitor = BufferOverflowVisitor()
        bo_visitor.visit(ast)
        
        # ast_to_c(ast)

    else:
        print("Please provide a filename as argument")

