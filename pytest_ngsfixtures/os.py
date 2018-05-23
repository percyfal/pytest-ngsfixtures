# -*- coding: utf-8 -*-
import os
import py
import pathlib
import logging
from pytest_ngsfixtures import DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def safe_copy(p, src, dst=None, ignore_errors=False):
    """Safely copy fixture file.

    Copy file from src to dst in LocalPath p. If src, dst are strings,
    they will be joined to p, assuming they are relative to p. If src,
    dst are LocalPath instances, they are left alone since LocalPath
    objects are always absolute paths.

    Args:
      p (LocalPath): path in which link is setup
      src (str, LocalPath): source file that link points to. If string, assume relative to pytest_ngsfixtures data directory
      dst (str, LocalPath): link destination name. If string, assume relative to path and concatenate; else leave alone
      ignore_errors (bool): ignore errors should target file exist

    Returns:
      dst (LocalPath): link name
    """
    if isinstance(src, pathlib.PosixPath):
        src = str(src)
    if isinstance(src, str):
        if not os.path.isabs(src):
            src = os.path.join(DATA_DIR, src)
        src = py.path.local(src)
    if dst is None:
        dst = src.basename
    if isinstance(dst, str):
        dst = p.join(dst)
    try:
        dst.dirpath().ensure(dir=True)
        if dst.exists():
            raise py.error.EEXIST("copy('{src}', '{dst}')".format(src=src, dst=dst))
        src.copy(dst)
    except OSError as e:
        if ignore_errors:
            logger.warn(e)
        else:
            logger.error(e)
            raise
    return dst


def safe_symlink(p, src, dst=None, ignore_errors=False):
    """Safely make symlink.

    Make symlink from src to dst in LocalPath p. If src, dst are
    strings, they will be joined to p, assuming they are relative to
    p. If src, dst are LocalPath instances, they are left alone since
    LocalPath objects are always absolute paths.

    Args:
      p (LocalPath): path in which link is setup
      src (str, LocalPath): source file that link points to. If string, assume relative to pytest_ngsfixtures data directory
      dst (str, LocalPath): link destination name. If string, assume relative to path and concatenate; else leave alone
      ignore_errors (bool): ignore errors should target file exist

    Returns:
      dst (LocalPath): link name
    """
    if isinstance(src, pathlib.PosixPath):
        src = str(src)
    if isinstance(src, str):
        if not os.path.isabs(src):
            src = os.path.join(DATA_DIR, src)
        src = py.path.local(src)
    if dst is None:
        dst = src.basename
    if isinstance(dst, str):
        dst = p.join(dst)
    try:
        dst.dirpath().ensure(dir=True)
        dst.mksymlinkto(src)
    except OSError as e:
        if ignore_errors:
            logger.warn(e)
        else:
            logger.error(e)
            raise
    return dst


def safe_mktemp(tmpdir_factory, dirname=None, **kwargs):
    """Safely make directory"""
    if dirname is None:
        return tmpdir_factory.getbasetemp()
    else:
        p = tmpdir_factory.getbasetemp().join(os.path.dirname(dirname)).ensure(dir=True)
        if kwargs.get("numbered", False):
            p = tmpdir_factory.mktemp(dirname)
        else:
            p = tmpdir_factory.getbasetemp().join(dirname)
            if not p.check(dir=1):
                p = tmpdir_factory.mktemp(dirname, numbered=False)
        return p


def localpath(src, path=DATA_DIR):
    """Generate a py.path.local path given a source and a path"""
    assert os.path.isabs(path), "path argument must be an absolute path"
    return py.path.local(os.path.join(path, src))
