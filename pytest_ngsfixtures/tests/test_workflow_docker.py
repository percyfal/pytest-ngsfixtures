# -*- coding: utf-8 -*-
import os
import docker
import pytest
from pytest_ngsfixtures.wm import snakemake
from pytest_ngsfixtures import factories


flat_copy = factories.sample_layout(sample=["CHS.HG00512"],
                                    dirname="flat_copy",
                                    numbered=True, copy=True)


@pytest.fixture(scope="session")
def container(request):
    def rm():
        try:
            print("Removing container ", container.name)
            container.remove(force=True)
        except:
            raise
        finally:
            pass
    request.addfinalizer(rm)
    client = docker.from_env()
    try:
        image = client.images.get(pytest.snakemake_image)
    except docker.error.ImageNotFound:
        print("docker image {} not found; pulling".format(pytest.snakemake_image))
        client.images.pull(pytest.snakemake_image)
        image = client.images.get(pytest.snakemake_image)
    except:
        raise
    container = client.containers.create(image, tty=True,
                                         user="{}:{}".format(os.getuid(), os.getgid()),
                                         volumes={'/tmp': {'bind': '/tmp', 'mode': 'rw'}},
                                         working_dir="/tmp")
    return container


Snakefile = snakemake.snakefile_factory(
    copy=True, numbered=True)


def test_workflow(Snakefile, flat_copy, container):
    container.start()
    for r in snakemake.run(Snakefile,
                           options=["-d", str(flat_copy), "-s",
                                    str(Snakefile)], container=container,
                           read=True, iterable=True):
        print(r)
    assert flat_copy.join("results.txt").exists()
