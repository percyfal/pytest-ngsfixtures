#!/usr/bin/env python3
import pytest
import itertools
from pytest_ngsfixtures.os import safe_mktemp
from pytest_ngsfixtures.layout import setup_sample_layout, setup_reference_layout
from pytest_ngsfixtures.config import sample_conf, runfmt_alias
from pytest_ngsfixtures import factories


@pytest.fixture(scope="function", autouse=False,
                params=itertools.product(sample_conf.RUNFMT_ALIAS[1:7], sample_conf.SAMPLE_LAYOUTS[1:3]))
def psample(request, tmpdir_factory):
    """Parametrized sample fixture"""
    fmt, layout = request.param
    if fmt not in request.config.option.ngs_runfmt_alias:
        pytest.skip("skipping {} as not in options")
    dirname = "{}_{}".format(fmt, layout)
    if layout == "pool":
        if fmt.endswith("project_run"):
            pytest.skip("pool layout can not be run in project run mode")
    path = safe_mktemp(tmpdir_factory, dirname)
    path = setup_sample_layout(path, layout=layout,
                               copy=request.config.option.ngs_copy)
    return path


@pytest.fixture(scope="function", autouse=False)
def pref(request, tmpdir_factory):
    """Parametrized reference fixture"""
    label = "scaffolds"
    if request.config.option.ngs_ref:
        label = "ref"
    dirname = label
    path = safe_mktemp(tmpdir_factory, dirname)
    path = setup_reference_layout(path, label=label,
                                  copy=request.config.option.ngs_copy,
                                  setup=True, ignore_errors=True)
    return path


sample = factories.sample_layout(
    layout="short",
    dirname="sample",
    runfmt=runfmt_alias("sample")[1],
    numbered=True,
)

sample_run = factories.sample_layout(
    layout="short",
    dirname="sample_run",
    runfmt=runfmt_alias("sample_run")[1],
    numbered=True
)

sample_project_run = factories.sample_layout(
    layout="short",
    dirname="sample_project_run",
    runfmt=runfmt_alias("sample_project_run")[1],
    batches=["p1", "p2", "p1"],
    numbered=True,
)


pop_sample = factories.sample_layout(
    layout="individual",
    dirname="pop_sample",
    runfmt=runfmt_alias("pop_sample")[1],
    numbered=True,
)

pop_sample_run = factories.sample_layout(
    layout="individual",
    dirname="pop_sample_run",
    runfmt=runfmt_alias("pop_sample_run")[1],
    numbered=True,
)

pop_sample_project_run = factories.sample_layout(
    layout="individual",
    dirname="pop_project_sample_run",
    runfmt=runfmt_alias("pop_sample_project_run")[1],
    batches=["p1", "p2", "p1"] + ["p1", "p2"] * 2,
    numbered=True,
)

pool_pop_sample = factories.sample_layout(
    layout="pool",
    dirname="pool_pop_sample",
    runfmt=runfmt_alias("pop_sample")[1],
    numbered=True,
)

pool_pop_sample_run = factories.sample_layout(
    layout="pool",
    dirname="pool_pop_sample_run",
    runfmt=runfmt_alias("pop_sample_run")[1],
    numbered=True,
)
