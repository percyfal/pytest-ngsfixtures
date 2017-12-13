# -*- coding: utf-8 -*-
import os
import pytest
import docker
from docker.types import Mount
from pytest_ngsfixtures import DATA_DIR, factories
from pytest_ngsfixtures.os import localpath
from pytest_ngsfixtures.fixtures import *
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

pytest_plugins = 'pytester'


def pytest_namespace():
    d = {
        'uid': os.getuid(),
        'gid': os.getgid(),
    }
    return d


def pytest_configure(config):
    config.addinivalue_line("markers",
                            "docker: mark test as dependent on docker")
    return config


def pytest_runtest_setup(item):
    dockermark = item.get_marker("docker")
    if dockermark is not None:
        try:
            client = docker.from_env()
            client.images.get("busybox")
        except ConnectionError:
            pytest.skip("docker executable not found; docker tests will be skipped")
        except docker.errors.ImageNotFound:
            logger.info("docker image 'busybox' not found; pulling to run tests")
            client.images.pull("busybox")
        except:
            raise


@pytest.mark.docker
@pytest.fixture(scope="session")
def image(request):
    def rm():
        # try:
        #     logger.info("Removing containers  {}".format(container.name))
        #     container.remove(force=True)
        # except:
        #     raise
        # finally:
        #     pass
        pass

    request.addfinalizer(rm)
    client = docker.from_env()
    try:
        busybox = client.images.get("busybox")
    except:
        raise
    return busybox


@pytest.mark.docker
@pytest.fixture(scope="session")
def container(request):
    def rm():
        try:
            logger.info("Removing container {}".format(container.name))
            container.remove(force=True)
        except:
            raise
        finally:
            pass

    request.addfinalizer(rm)
    client = docker.from_env()
    try:
        busybox = client.images.get("busybox")
    except:
        raise
    container = client.containers.create(busybox, tty=True,
                                         user="{}:{}".format(pytest.uid, pytest.gid),
                                         volumes={'/tmp': {'bind': '/tmp', 'mode': 'rw'}})
    return container


@pytest.fixture(scope="module", autouse=False)
def tiny_fastq_files():
    """Fixture that returns list of all tiny fastq files"""
    for path, dirs, files in os.walk(os.path.join(DATA_DIR, "tiny")):
        filelist = sorted([os.path.join(DATA_DIR, "tiny", x) for x in files])
    return filelist


# Local files
PURHG00731 = localpath(os.path.join("applications", "pe",
                                    "PUR.HG00731.tiny.bam"))
PURHG00733 = localpath(os.path.join("applications", "pe",
                                    "PUR.HG00733.tiny.bam"))


# File fixtures
@pytest.fixture(scope="function", autouse=False)
def bamfile():
    """Bamfile fixture"""
    return PURHG00731


bam = factories.filetype(PURHG00731.basename,
                         fdir="bamfoo", scope="function",
                         numbered=True)
bam_copy = factories.filetype(PURHG00731.basename, fdir="bamfoo",
                              scope="function", numbered=True,
                              copy=True)
renamebam = factories.filetype(PURHG00731.basename,
                               fdir="renamebamfoo", scope="function",
                               numbered=True, alias="s.tiny.bam")
renamebam_copy = factories.filetype(PURHG00731.basename, fdir="renamebamfoo",
                                    scope="function", numbered=True,
                                    alias="s.tiny.bam", copy=True)


# Multifile fixtures
_PURFILES = [PURHG00731.relto(DATA_DIR), PURHG00733.relto(DATA_DIR)]


@pytest.fixture(scope="function", autouse=False)
def PURFILES():
    """List of bam files"""
    return [PURHG00731, PURHG00733]


bamset = factories.fileset(src=_PURFILES, fdir="bamset",
                           scope="function")

_dstfiles = ["foo.fastq.gz", "bar.fastq.gz"]


@pytest.fixture(scope="function", autouse=False)
def dstfiles():
    """Destination file names"""
    return _dstfiles


bamset2 = factories.fileset(src=_PURFILES, dst=_dstfiles,
                            fdir="bamset2", scope="function")
