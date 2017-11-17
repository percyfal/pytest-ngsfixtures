# -*- coding: utf-8 -*-
import os
import sys
import contextlib


# context manager for cd
@contextlib.contextmanager
def cd(path):
    CWD = os.getcwd()
    print("Changing directory from {} to {}".format(CWD, path), file=sys.stderr)

    os.chdir(path)
    try:
        yield
    except:
        print('Exception caught: ', sys.exc_info()[0],
              file=sys.stderr)
    finally:
        print("Changing directory back to {}".format(CWD), file=sys.stderr)
        os.chdir(CWD)
