import sys


def execute_file(file):
    """
    Executes the passed in file in the current python interpreter.
    :param file: The string filename.
    """
    exec(open(file).read())


if __name__ == '__main__':
    execute_file(sys.argv[1])
