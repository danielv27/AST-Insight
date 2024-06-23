# TODO: This part is for visiting heap allocation in code. For later
# def visit_Assignment(self, node):
#     print(node)
#     if isinstance(node.rvalue, c_ast.FuncCall):
#         func_name = node.rvalue.name.name
#         if func_name in ['malloc', 'calloc', 'realloc']:
#             var_name = node.lvalue.name
#             size_expr = node.rvalue.args.exprs[0]
#             # Simplified size calculation (you may need to handle more complex cases)
#             size = int(size_expr.value)
#             self.allocated_sizes[var_name] = size

# TODO: Another case that was there
#     # def visit_Assignment(self, node):
    #     print(node)
    #     if isinstance(node.rvalue, c_ast.FuncCall):
    #         func_name = node.rvalue.name.name
    #         if func_name in ['malloc', 'calloc', 'realloc']:
    #             var_name = node.lvalue.name
    #             size_expr = node.rvalue.args.exprs[0]
    #             # Simplified size calculation (you may need to handle more complex cases)
    #             size = int(size_expr.value)
    #             self.allocated_sizes[var_name] = size



# 
# TODO: Can prbably be removed
# def getFunctionsFromCompound(self, node):
#     result = {}
#     for item in node.block_items:
#         function_name = None
#         function_node = None

#         if(isinstance(item, c_ast.Decl) and item.init):
#             function_name = item.name
#             function_node = item.init
#         elif(isinstance(item, c_ast.Assignment)):
#             function_name = item.lvalue.expr.name
#             function_node = item.rvalue
#         else:
#             continue
#         if(isinstance(function_node, c_ast.FuncCall)):
#             result[function_name] = function_node
#     return result