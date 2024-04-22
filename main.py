import sys
from parse_ast import createAst
from BufferOverflowVisitor import BufferOverflowVisitor

sys.path.extend(['.', '..'])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ast = createAst(sys.argv[1])
        bo_visitor = BufferOverflowVisitor()
        bo_visitor.visit(ast)

    else:
        print("Please provide a filename as argument")

