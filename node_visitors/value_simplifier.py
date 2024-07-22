from pycparser import c_ast
from utils.log import log


# Source: https://os.mbed.com/handbook/C-Data-Types#integer-data-types
sizeof_is_1 = ['char', 'signed char']
sizeof_is_2 = ['short', 'unsigned short']
sizeof_is_4 = ['int', 'unsigned int', 'long', 'unsigned long']
sizeof_is_8 = ['unsigned long long', 'long long']

# NodeVisitor used to simplify binary operations (e.g. If defined as buf[10+1], converted to buf[11])
# Currently only simplifies subscripts or arrays and expression lists (found in functions) but can be applied to all node types
# NOTE: For the changes to modift the AST the parent node needs to be modified (dont modify the expression itself as it will be assigned to a new object,
# not modify the AST)
class ValueSimplifier(c_ast.NodeVisitor):

    def visit_ArrayDecl(self, node):
        if isinstance(node.dim, c_ast.BinaryOp):
            node.dim = self.resolve_constants(node.dim)

    # FuncCall args are of type ExprList
    def visit_ExprList(self, node):
        for i, expr in enumerate(node.exprs):
            node.exprs[i] = self.resolve_constants(expr)

        
    def is_int(self, node):
        return isinstance(node, c_ast.Constant) and node.type == 'int'
    
    # Recursively evaluate expression when containing constants constant expressions
    def resolve_constants(self, node: c_ast.BinaryOp):
        if isinstance(node, c_ast.Constant):
            return node
        if isinstance(node.left, c_ast.BinaryOp):
            node.left = self.resolve_constants(node.left)
        if isinstance(node.right, c_ast.BinaryOp):
            node.right = self.resolve_constants(node.right)
        if self.is_int(node.left) and self.is_int(node.right):
            left_value = int(node.left.value)
            right_value = int(node.right.value)
            if node.op == '+':
                result = left_value + right_value
            elif node.op == '-':
                result = left_value - right_value
            elif node.op == '*':
                result = left_value * right_value
            elif node.op == '/':
                if right_value == 0:
                    log(node, 'Division by zero in constant expression', 'warning')
                    return
                result = left_value // right_value

            return c_ast.Constant(type='int', value=str(result), coord=node.left.coord)
        return node
        

