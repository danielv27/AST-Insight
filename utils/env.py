import shutil, os, tempfile
from tempfile import mkdtemp

JULIET_DEPENDENCY_PATH = "/Users/danielverner/Programming/MSc_Thesis/python_c_ast/juliet-test-suite-c/testcasesupport"

def setup_juliet_temp_dir():
    temp_dir = tempfile.mkdtemp()
    for file_name in os.listdir(JULIET_DEPENDENCY_PATH):
        file_path = os.path.join(JULIET_DEPENDENCY_PATH, file_name)
        if os.path.isfile(file_path):
            shutil.copy(file_path, temp_dir)
    return temp_dir

def load_existing_file_to_juliet(file_path: str, juliet: bool):
    temp_dir_path = setup_juliet_temp_dir() if juliet else tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir_path, os.path.basename(file_path))
    shutil.copy(file_path, temp_file_path)
    return temp_file_path, temp_dir_path


def load_code_to_juliet(code: str, juliet: bool):
    temp_dir_path = setup_juliet_temp_dir() if juliet else mkdtemp()
    temp_file_path = os.path.join(temp_dir_path, "temp_test_file.c")
    with open(temp_file_path, 'w') as temp_file:
        temp_file.write(code)
    return temp_file_path, temp_dir_path