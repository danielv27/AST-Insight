# NodeVisitor used to count all good and bad test cases in juliet test suite
from pycparser import c_ast
class TestCaseExtractor(c_ast.NodeVisitor):
    def __init__(self):
       self.bad_count = 0
       self.good_count = 0
    def visit_FuncDef(self, node):
        name = node.decl.name
        if 'bad' in name.lower():
            self.bad_count += 1
        elif 'good' in name.lower():
            self.good_count += 1