# -*- coding: utf-8 -*-
import os
import sys
import re
import py
import pytest
import docker
import subprocess as sp
from pytest_ngsfixtures.config import SAMPLES_DIR
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.getLogger("docker").setLevel(logging.INFO)

pytest_plugins = 'pytester'

PYTHON_VERSION = "py{}{}".format(sys.version_info.major,
                                 sys.version_info.minor)
try:
    SNAKEMAKE_VERSION = sp.check_output(
        ["snakemake", "--version"]).decode().strip()
except Exception:
    logger.error("couldn't get snakemake version")
    raise

SNAKEMAKE_REPO = "quay.io/biocontainers/snakemake"
BUSYBOX_IMAGE = "busybox:latest"


def pytest_configure(config):
    config.addinivalue_line("markers",
                            "docker: mark test as dependent on docker")
    config.addinivalue_line("markers",
                            "busybox: mark test as dependent on busybox image")
    config.addinivalue_line("markers",
                            "snakemake: mark test as dependent on snakemake image")
    pytest.uid = os.getuid()
    pytest.gid = os.getgid()
    pytest.testdir = py.path.local(os.path.abspath(os.path.dirname(__file__)))
    snakemake_tag = "{}--0".format(SNAKEMAKE_VERSION)

    regex = re.compile(SNAKEMAKE_VERSION)
    if config.cache.get("pytest_ngsfixtures/tags", None) is None:
        try:
            import requests
            r = requests.get(
                "https://quay.io/api/v1/repository/biocontainers/snakemake/tag")
            tags = sorted([t['name'] for t in r.json()['tags']], reverse=True)
            config.cache.set("pytest_ngsfixtures/tags", tags)
        except Exception:
            logger.error("couldn't complete requests for quay.io")
            raise
    for t in sorted(config.cache.get("pytest_ngsfixtures/tags", []), reverse=True):
        if regex.search(t):
            snakemake_tag = t
            break
    pytest.snakemake_image = "{}:{}".format(SNAKEMAKE_REPO, snakemake_tag)


def pytest_runtest_setup(item):
    dockermark = item.get_closest_marker("docker")
    if dockermark is not None:
        try:
            client = docker.from_env()
            client.images.list()
        except ConnectionError:
            pytest.skip("docker executable not found; docker tests will be skipped")
        except Exception:
            raise
    busyboxmark = item.get_closest_marker("busybox")
    if busyboxmark is not None:
        get_image(BUSYBOX_IMAGE)
    snakemakemark = item.get_closest_marker("snakemake")
    if snakemakemark is not None:
        get_image(pytest.snakemake_image)


def get_image(image):
    try:
        client = docker.from_env()
        image = client.images.get(image)
        logger.info("retrieved local image '{}'".format(image))
    except docker.errors.ImageNotFound:
        logger.info("docker image '{}' not found; pulling to run tests".format(image))
        client.images.pull(image)
        image = client.images.get(image)
    except Exception:
        raise
    return image


def image_factory(name):
    @pytest.mark.docker
    @pytest.fixture(scope="session")
    def image_fixture(request):
        image_name = name
        if name == "snakemake":
            image_name = pytest.snakemake_image
        def rm():
            try:
                client = docker.from_env()
                containers = client.containers.list(filters={'status': 'exited',
                                                             'ancestor': image_name})
                for c in containers:
                    if not c.name.startswith("pytest_ngsfixtures"):
                        continue
                    c.remove(force=True)
                    logger.info("Removed container {} ({})".format(c.name, c.short_id))
            except Exception:
                raise
            finally:
                pass

        request.addfinalizer(rm)
        client = docker.from_env()
        try:
            image = client.images.get(image_name)
        except Exception:
            raise
        return image
    return image_fixture


busybox_image = image_factory(BUSYBOX_IMAGE)
snakemake_image = image_factory("snakemake")


def container_factory(name):
    @pytest.mark.docker
    @pytest.fixture(scope="session")
    def container_fixture(request):
        container_name = name
        if name == "snakemake":
            container_name = pytest.snakemake_image
        def rm():
            try:
                container.remove(force=True)
                logger.info("Removed container {} ({})".format(container.name, container.short_id))
            except Exception:
                raise
            finally:
                pass

        request.addfinalizer(rm)
        client = docker.from_env()
        try:
            image = client.images.get(container_name)
        except Exception:
            raise
        container = client.containers.create(image, tty=True,
                                             user="{}:{}".format(pytest.uid, pytest.gid),
                                             volumes={'/tmp': {'bind': '/tmp', 'mode': 'rw'}},
                                             working_dir="/tmp")
        logger.info("created container {} from image {}".format(container.short_id, image))
        return container
    return container_fixture


busybox_container = container_factory(BUSYBOX_IMAGE)
snakemake_container = container_factory("snakemake")


@pytest.fixture(scope="module")
def image_args():
    d = {
        'user': "{}:{}".format(pytest.uid, pytest.gid),
        'volumes': {'/tmp': {'bind': '/tmp', 'mode': 'rw'}},
        'tty': False,
    }
    return d


@pytest.fixture
def readfile():
    return py.path.local(SAMPLES_DIR / "CHS.HG00512_1.fastq.gz")
