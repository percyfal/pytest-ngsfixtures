#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
import types
import subprocess as sp
from pytest_ngsfixtures.shell import shell
from docker.models.containers import Container


@pytest.fixture(scope="module")
def foo(tmpdir_factory):
    p = tmpdir_factory.mktemp("foo")
    foo = p.join("foo.txt")
    foo.write("foo")
    bar = p.join("bar.txt")
    bar.write("bar")
    return p


# should return none, but still execute
def test_shell(foo):
    ret = shell("ls " + str(foo))
    touch = foo.join("test_shell.touch")
    shell("touch " + str(touch))
    assert touch.exists()
    assert ret is None


def test_shell_iterable(foo):
    ret = shell("ls " + str(foo), iterable=True)
    assert isinstance(ret, types.GeneratorType)
    assert "bar.txt" in list(ret)


def test_shell_read(foo):
    ret = shell("ls " + str(foo.join("foo.txt")), read=True)
    assert ret.rstrip() == str(foo.join("foo.txt"))


def test_shell_async(foo):
    ret = shell("ls " + str(foo), async=True)
    assert isinstance(ret, sp.Popen)



@pytest.fixture(scope="function")
def shell_config(request):
    def reset():
        shell.executable("/bin/bash")
    request.addfinalizer(reset)
    shell.prefix("set -eo pipefail; ")
    shell.executable("/bin/sh")


@pytest.mark.docker
@pytest.mark.busybox
def test_container_shell(busybox_container, foo, shell_config):
    busybox_container.start()
    ret = shell("ls {}".format(foo.dirname), container=busybox_container)
    touch = foo.join("test_busybox_shell.touch")
    shell("touch {}".format(touch), container=busybox_container)
    assert touch.exists()
    assert ret is None


@pytest.mark.docker
@pytest.mark.busybox
def test_container_shell_iterable(busybox_container, foo, shell_config):
    busybox_container.start()
    ret = shell("ls " + str(foo), iterable=True, container=busybox_container)
    assert isinstance(ret, types.GeneratorType)
    assert "bar.txt" in list(ret)


@pytest.mark.docker
@pytest.mark.busybox
def test_container_shell_iterable_detach(busybox_container, foo, shell_config):
    busybox_container.start()
    touch = foo.join("test_busybox_shell_iterable_detach.touch")
    ret = shell("touch {}".format(touch), container=busybox_container, iterable=True,
                detach=True)
    assert isinstance(ret, types.GeneratorType)
    assert list(ret) == []
    assert touch.exists()


@pytest.mark.docker
@pytest.mark.busybox
def test_container_shell_async(busybox_container, foo, shell_config):
    busybox_container.start()
    touch = foo.join("test_busybox_shell_async.touch")
    ret = shell("touch {}".format(touch), container=busybox_container,
                detach=True)
    assert isinstance(ret, str)
    assert touch.exists()


@pytest.mark.docker
@pytest.mark.busybox
def test_container_shell_read(busybox_container, foo, shell_config):
    busybox_container.start()
    ret = shell("ls " + str(foo.join("foo.txt")), read=True,
                container=busybox_container)
    assert ret.rstrip() == str(foo.join("foo.txt"))


# Image tests
@pytest.mark.docker
def test_busybox_image_shell(busybox_image, foo, image_args, shell_config):
    ret = shell("ls {}".format(foo.dirname), image=busybox_image,
                name="pytest_ngsfixtures_test_busybox_image_shell",
                **image_args)
    touch = foo.join("test_busybox_image_shell.touch")
    shell("touch {}".format(touch), image=busybox_image,
          name="pytest_ngsfixtures_test_busybox_image_shell2",
          **image_args)
    assert touch.exists()
    assert ret is None


@pytest.mark.docker
def test_busybox_image_shell_read(busybox_image, foo, image_args, shell_config):
    ret = shell("ls " + str(foo.join("foo.txt")), read=True,
                name="pytest_ngsfixtures_test_busybox_image_shell_read",
                image=busybox_image, **image_args)
    assert isinstance(ret, str)
    # Something is aloof with the encoding here; there are hidden
    # hexadecimal characters in ret that won't go away in the decoding
    # step
    # assert ret.rstrip() == str(foo.join("foo.txt"))


@pytest.mark.docker
def test_busybox_image_shell_iterable(busybox_image, foo, image_args, shell_config):
    ret = shell("ls " + str(foo), iterable=True, image=busybox_image,
                name="pytest_ngsfixtures_test_busybox_image_shell_iterable",
                **image_args)
    assert isinstance(ret, types.GeneratorType)
    # assert sorted(list(ret)) == ["", "bar.txt", "foo.txt"]


@pytest.mark.docker
def test_busybox_image_shell_iterable_detach(busybox_image, foo, image_args, shell_config):
    touch = foo.join("test_busybox_image_shell_iterable_detach.touch")
    ret = shell("touch {}".format(touch), image=busybox_image, iterable=True,
                detach=True,
                name="pytest_ngsfixtures_test_busybox_image_shell_iterable_detach",
                **image_args)
    assert isinstance(ret, types.GeneratorType)
    assert list(ret) == []
    assert touch.exists()


# Detaching client.containers.run returns a container
@pytest.mark.docker
def test_busybox_image_shell_async(busybox_image, foo, image_args, shell_config):
    touch = foo.join("test_busybox_image_shell_async.touch")
    ret = shell("touch {}".format(touch), image=busybox_image, detach=True,
                name="pytest_ngsfixtures_test_busybox_image_shell_async", **image_args)
    assert isinstance(ret, Container)
    assert touch.exists()


@pytest.mark.docker
@pytest.mark.busybox
def test_container_shell_path(busybox_container, foo, shell_config):
    busybox_container.start()
    touch = foo.join("test_container_shell_path.touch")
    shell("echo $PATH > {}".format(touch),
          path_list=["/foo", "/bar"],
          container=busybox_container)
    assert touch.readlines()[0].startswith("/foo:/bar")
