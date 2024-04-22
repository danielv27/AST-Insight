import sys
from importlib.resources import files
from pycparser import parse_file, c_generator
sys.path.extend(['.', '..'])

fake_libc_path = files('pycparser').joinpath('utils/fake_libc_include')

# https://github.com/eliben/pycparser/blob/main/examples/explore_ast.py
def createAst(filename):
    return parse_file(
        filename,
        use_cpp=True,
        cpp_path='gcc',
        cpp_args=['-E', r'-I{}'.format(fake_libc_path)]
    )
