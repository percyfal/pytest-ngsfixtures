#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import os
import sys
import shlex
import types
import subprocess as sp
import docker
from docker.models.containers import Container, ExecResult
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

STDOUT = sys.stdout


def get_conda_root():
    output = sp.check_output(shlex.split("conda info --json"))
    m = re.search("\"root_prefix\":\s+\"(\S+)\",$", output.decode("utf-8"), re.MULTILINE)
    try:
        return m.group(1)
    except AttributeError:
        logger.error("Failed to set conda root prefix")
        raise


class shell:
    """Class wrapper for shell commands.

    Wrapper for running shell commands. The wrapper accepts arguments
    for seamlessly running in docker/singularity containers.

    Based on snakemake shell implementation by Johannes Köster.

    Args:
      cmd (str): command string
      container (Container): docker/singularity container instance
      conda_env (str): conda environment to activate
      conda_env_list (list): additional conda environment paths to add
                             to PATH. Note: only the conda environment
                             names need be provided as the conda root
                             is inferred from the current conda
                             environment
      conda_root (str): conda root path. Use in case automatically
                        inferring the root fails
      image (Image): docker/singularity image to run in
      iterable (bool): return output as iterable
      read (bool): read and return output
      async (bool): run asynchronously
      path_list (list): prefix command with additional paths
      stdout (_io.TextIOWrapper, int): stdout file object
      stderr (int): stderr special value
      stream (bool): stream containerized run; alias to iterable
      detach (bool): detach containerized run; alias to async
      process_prefix (str): temporarily override class process prefix. In
                            containerized settings, using 'source
                            activate' together with the automatically
                            generated class process prefix 'set -euo
                            pipefail' may fail

    Returns:
      stdout if read is set, an iterable if iterable is set, a process (either :py:mod:`subprocess.Popen` or :py:mod:`docker.models.containers.Container`) if async is set, None otherwise
    """
    _process_args = {}
    _process_prefix = ""

    @classmethod
    def executable(cls, cmd):
        if os.path.split(cmd)[-1] == "bash":
            cls._process_prefix = "set -euo pipefail;"
        cls._process_args["executable"] = cmd

    @classmethod
    def prefix(cls, prefix):
        cls._process_prefix = prefix

    def __new__(cls, cmd,
                container=None,
                conda_env=None,
                conda_env_list=[],
                conda_root=None,
                image=None,
                iterable=False,
                read=False,
                async=False,
                path_list=[],
                **kwargs):

        stdout = sp.PIPE if iterable or async or read else kwargs.pop("stdout", STDOUT)
        stderr = kwargs.pop("stderr", STDOUT)

        close_fds = sys.platform != 'win32'
        plist = path_list
        if kwargs.get("stream", False):
            iterable = kwargs.pop("stream")
        if kwargs.get("detach", False):
            async = kwargs.pop("detach")

        if conda_env_list:
            if not conda_root:
                conda_root = get_conda_root()
            for env in conda_env_list:
                p = os.path.join(conda_root, "envs", env, "bin")
                plist.append(p)
        if plist:
            plist.append("$PATH")
            path = "PATH=\"{}\";".format(":".join(plist))
        else:
            path = ""

        env_prefix = ""

        if conda_env:
            # Run conda environment
            env_prefix = "source activate {};".format(conda_env)
            logger.info("Activating conda environment {}.".format(conda_env))

        cmd = "{} {} {} {}".format(
            kwargs.pop("process_prefix", cls._process_prefix),
            path,
            env_prefix,
            cmd.rstrip())

        if container or image:
            if cls._process_args["executable"]:
                cmd = "{} -c '{}'".format(cls._process_args["executable"], cmd)
        if container:
            try:
                proc = container.exec_run(cmd, stream=iterable,
                                          detach=async,
                                          **kwargs)
                if async:
                    proc = proc.output
            except:
                raise
        elif image:
            try:
                client = docker.from_env()
                proc = client.containers.run(image, command=cmd,
                                             detach=async,
                                             **kwargs)
            except:
                raise
        else:
            proc = sp.Popen(cmd,
                            bufsize=-1,
                            shell=True,
                            stdout=stdout,
                            stderr=stderr,
                            close_fds=close_fds, **cls._process_args)

        if iterable:
            return cls.iter_stdout(proc, cmd)
        if read:
            proc = cls.read_stdout(proc)
            return cls.stdout(proc, cmd, ret=proc)
        elif async:
            return proc

        return cls.stdout(proc, cmd)

    @staticmethod
    def stdout(proc, cmd, ret=None):
        if isinstance(proc, sp.Popen):
            retcode = proc.wait()
            if retcode:
                raise sp.CalledProcessError(retcode, cmd)
            return ret
        elif isinstance(proc, str):
            return ret
        elif isinstance(proc, bytes):
            if ret is None:
                return ret
            else:
                return ret.decode()
        else:
            return ret

    @staticmethod
    def read_stdout(proc):
        if isinstance(proc, sp.Popen):
            return proc.stdout.read()
        elif isinstance(proc, ExecResult):
            return proc.output
        elif isinstance(proc, str):
            return proc
        elif isinstance(proc, bytes):
            return proc.decode()

    @staticmethod
    def iter_stdout(proc, cmd):
        if isinstance(proc, types.GeneratorType):
            for l in proc:
                if isinstance(l, bytes):
                    for k in l.decode().split("\n"):
                        yield k
                else:
                    yield l[:-1]
            raise StopIteration
        elif isinstance(proc, Container):
            for l in proc.logs(stream=True):
                yield l[:-1].decode()
            raise StopIteration
        elif isinstance(proc, ExecResult):
            for l in proc.output:
                if isinstance(l, bytes):
                    for k in l.decode().split("\n"):
                        yield k
                else:
                    yield l[:-1].decode()
            raise StopIteration
        elif isinstance(proc, bytes):
            for l in proc.decode().split("\n"):
                yield l
            raise StopIteration
        elif isinstance(proc, str):
            return proc
        for l in proc.stdout:
            yield l[:-1].decode()
        retcode = proc.wait()
        if retcode:
            raise sp.CalledProcessError(retcode, cmd)


if "SHELL" in os.environ:
    shell.executable(os.environ["SHELL"])
