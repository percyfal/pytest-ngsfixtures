# -*- coding: utf-8 -*-
"""
test_pytest_repo
----------------------------------

Tests for `pytest_ngsfixtures.repo` module.
"""
import os
import pytest
from pytest_ngsfixtures import repo


def test_download_url_fail(tmpdir_factory):
    import urllib.request
    bn = tmpdir_factory.mktemp("foo").join("foo.bar")
    with pytest.raises(urllib.error.HTTPError):
        repo.download_sample_file(str(bn), "yuge")


def test_download_url_wrong_size(tmpdir_factory):
    bn = tmpdir_factory.mktemp("foo").join("foo.bar")
    repo.download_sample_file(str(bn), "tiny")
    assert not bn.exists()


def test_download_url(tmpdir_factory, monkeypatch):
    bn = tmpdir_factory.mktemp("foo").join("foo.bar.gz")

    def mockreturn(*args):
        return "https://raw.githubusercontent.com/percyfal/pytest-ngsfixtures/master/pytest_ngsfixtures/data/tiny/CHS.HG00512_1.fastq.gz"
    monkeypatch.setattr(os.path, 'join', mockreturn)
    repo.download_sample_file(str(bn), "yuge")
    import gzip
    with gzip.open(str(bn), 'rb') as fh:
        assert fh.readlines()[0].strip() == b'@ERR016116.1225854/1'


def test_download_url_exists(tmpdir_factory):
    bn = tmpdir_factory.mktemp("foo").join("foo.bar.gz")
    bn.write("foo.bar")
    repo.download_sample_file(str(bn), "yuge")
    assert "foo.bar" == "".join(bn.readlines())


def test_download_sample_file(tiny_fastq_files):
    url = repo.download_sample_file(tiny_fastq_files[0], "yuge", dry_run=True, force=True)
    assert url.startswith("https://raw.githubusercontent.com/percyfal/pytest-ngsfixtures/master/pytest_ngsfixtures")
