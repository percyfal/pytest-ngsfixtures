#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os


# Helper function to make output executable
def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)


def save_command(cmd, path=os.environ["PATH"], outfile="command.sh"):
    with open(outfile, "w") as fh:
        fh.write("#!/bin/bash\n")
        fh.write("PATH={}\n".format(os.environ["PATH"]))
        fh.write("args=$*\n")
        fh.write(cmd + " ${args}\n")
    make_executable(outfile)
