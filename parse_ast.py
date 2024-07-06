import sys
import os
from importlib.resources import files
from pycparser import parse_file, c_generator
sys.path.extend(['.', '..'])

# fake_libc_path = files('pycparser').joinpath('utils/fake_libc_include')
fake_libc_path = 'fake_libc_include'

# https://github.com/eliben/pycparser/blob/main/examples/explore_ast.py
def parse_ast(filename):
    return parse_file(
        filename,
        use_cpp=True,
        cpp_path='gcc',
        cpp_args=['-E', r'-I{}'.format(fake_libc_path)]
    )

def ast_to_c_file(ast, file_path):
    generator = c_generator.CGenerator()

    directory, base_name = os.path.split(file_path)
    name, ext = os.path.splitext(base_name)
    
    new_file_name = f"{name}_modified{ext}"
    new_file_path = os.path.join(directory, new_file_name)

    result = generator.visit(ast)
    with open(new_file_path, 'w') as file:
        file.write(result)
