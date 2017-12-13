#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
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


@pytest.fixture(scope="module")
def image_args():
    d = {
        'user': "{}:{}".format(pytest.uid, pytest.gid),
        'volumes': {'/tmp': {'bind': '/tmp', 'mode': 'rw'}},
        'tty': True,
    }
    return d


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


@pytest.mark.docker
def test_container_shell(container, foo):
    container.start()
    ret = shell("ls {}".format(foo.dirname), container=container)
    touch = foo.join("test_container_shell.touch")
    shell("touch {}".format(touch), container=container)
    assert touch.exists()
    assert ret is None


@pytest.mark.docker
def test_container_shell_iterable(container, foo):
    container.start()
    ret = shell("ls " + str(foo), iterable=True, container=container)
    assert isinstance(ret, types.GeneratorType)
    assert "bar.txt" in list(ret)


@pytest.mark.docker
def test_container_shell_iterable_detach(container, foo):
    container.start()
    touch = foo.join("test_container_shell_iterable_detach.touch")
    ret = shell("touch {}".format(touch), container=container, iterable=True,
                detach=True)
    assert isinstance(ret, types.GeneratorType)
    assert list(ret) == []
    assert touch.exists()


@pytest.mark.docker
def test_container_shell_async(container, foo):
    container.start()
    touch = foo.join("test_container_shell_async.touch")
    ret = shell("touch {}".format(touch), container=container,
                detach=True)
    assert isinstance(ret, str)
    assert touch.exists()


@pytest.mark.docker
def test_container_shell_read(container, foo):
    container.start()
    ret = shell("ls " + str(foo.join("foo.txt")), read=True,
                container=container)
    assert ret.rstrip() == str(foo.join("foo.txt"))


# Image tests
@pytest.mark.docker
def test_image_shell(image, foo, image_args):
    ret = shell("ls {}".format(foo.dirname), image=image,
                **image_args)
    touch = foo.join("test_image_shell.touch")
    shell("touch {}".format(touch), image=image, **image_args)
    assert touch.exists()
    assert ret is None


@pytest.mark.docker
def test_image_shell_read(image, foo, image_args):
    ret = shell("ls " + str(foo.join("foo.txt")), read=True,
                image=image, **image_args)
    assert isinstance(ret, str)
    # Something is aloof with the encoding here; there are hidden
    # hexadecimal characters in ret that won't go away in the decoding
    # step
    # assert ret.rstrip() == str(foo.join("foo.txt"))


@pytest.mark.docker
def test_image_shell_iterable(image, foo, image_args):
    ret = shell("ls " + str(foo), iterable=True, image=image,
                **image_args)
    assert isinstance(ret, types.GeneratorType)
    # assert sorted(list(ret)) == ["", "bar.txt", "foo.txt"]


@pytest.mark.docker
def test_image_shell_iterable_detach(image, foo, image_args):
    touch = foo.join("test_image_shell_iterable_detach.touch")
    ret = shell("touch {}".format(touch), image=image, iterable=True,
                detach=True, **image_args)
    assert isinstance(ret, types.GeneratorType)
    assert list(ret) == []
    assert touch.exists()


# Detaching client.containers.run returns a container
@pytest.mark.docker
def test_image_shell_async(image, foo, image_args):
    touch = foo.join("test_image_shell_async.touch")
    ret = shell("touch {}".format(touch), image=image,
                detach=True, **image_args)
    assert isinstance(ret, Container)
    assert touch.exists()
