from os.path import abspath, dirname
import sys

def add_parent_dir_to_sys_path():
    sys.path.append(dirname(abspath(dirname(__file__))))