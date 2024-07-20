import shutil, os, tempfile

JULIET_DEPENDENCY_PATH = "/Users/danielverner/Programming/MSc_Thesis/python_c_ast/juliet-test-suite-c/testcasesupport"

def setup_juliet_temp_dir():
    temp_dir = tempfile.mkdtemp()
    for file_name in os.listdir(JULIET_DEPENDENCY_PATH):
        file_path = os.path.join(JULIET_DEPENDENCY_PATH, file_name)
        if os.path.isfile(file_path):
            shutil.copy(file_path, temp_dir)
    return temp_dir
