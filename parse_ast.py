import sys
from pkg_resources import resource_filename
sys.path.extend(['.', '..'])

from pycparser import parse_file, c_generator, preprocess_file

fake_libc_path = resource_filename('pycparser', 'utils/fake_libc_include')


def translate_to_c(filename):
    
    ast = parse_file(filename, use_cpp=True,
                 cpp_path='gcc',
                 cpp_args=['-E', r'-I{}'.format(fake_libc_path)])
    
    generator = c_generator.CGenerator()
    print(generator.visit(ast))


if __name__ == "__main__":
    # print(fake_libc_path)
    if len(sys.argv) > 1:
        print('has arg')
        translate_to_c(sys.argv[1])
    else:
        print("Please provide a filename as argument")