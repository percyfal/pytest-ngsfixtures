# -*- coding: utf-8 -*-
import os
import docker
import pytest
from pytest_ngsfixtures.wm.snakemake import run as snakemake_run, snakefile


@pytest.fixture(scope="session")
def container(request):
    def rm():
        try:
            print("Removing container ", container.name)
            container.remove(force=True)
        except Exception:
            raise
        finally:
            pass
    request.addfinalizer(rm)
    client = docker.from_env()
    try:
        image = client.images.get(pytest.snakemake_repo)
    except docker.errors.ImageNotFound:
        print("docker image '{}' not found; pulling".format(pytest.snakemake_repo))
        client.images.pull(pytest.snakemake_repo)
        image = client.images.get(pytest.snakemake_repo)
    except Exception:
        raise
    container = client.containers.create(image, tty=True,
                                         user="{}:{}".format(os.getuid(), os.getgid()),
                                         volumes={'/tmp': {'bind': '/tmp', 'mode': 'rw'}},
                                         working_dir="/tmp")
    return container


@pytest.mark.samples(numbered=True)
@pytest.mark.snakefile(dirname="snakefile", numbered=True)
def test_workflow(snakefile, samples, container):
    container.start()
    for r in snakemake_run(snakefile,
                           options=["-d", str(samples), "-s",
                                    str(snakefile)], container=container,
                           read=True, iterable=True):
        print(r)
    assert samples.join("results.txt").exists()
