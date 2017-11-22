#!/usr/bin/env python3
from pytest_ngsfixtures.config import runfmt_alias
from pytest_ngsfixtures import factories

sample = factories.sample_layout(
    layout="short",
    dirname="sample",
    runfmt=runfmt_alias["sample"],
    numbered=True,
)

sample_run = factories.sample_layout(
    layout="short",
    dirname="sample_run",
    runfmt=runfmt_alias["sample_run"],
    numbered=True
)

sample_project_run = factories.sample_layout(
    layout="short",
    dirname="sample_project_run",
    runfmt=runfmt_alias["sample_project_run"],
    batches=["p1", "p2", "p1"],
    numbered=True,
)


pop_sample = factories.sample_layout(
    layout="individual",
    dirname="pop_sample",
    runfmt=runfmt_alias["pop_sample"],
    numbered=True,
)

pop_sample_run = factories.sample_layout(
    layout="individual",
    dirname="pop_sample_run",
    runfmt=runfmt_alias["pop_sample_run"],
    numbered=True,
)

pop_sample_project_run = factories.sample_layout(
    layout="individual",
    dirname="pop_project_sample_run",
    runfmt=runfmt_alias["pop_sample_project_run"],
    batches=["p1", "p2", "p1"] + ["p1", "p2"] * 2,
    numbered=True,
)

pool_pop_sample = factories.sample_layout(
    layout="pool",
    dirname="pool_pop_sample",
    runfmt=runfmt_alias["pop_sample"],
    numbered=True,
)

pool_pop_sample_run = factories.sample_layout(
    layout="pool",
    dirname="pool_pop_sample_run",
    runfmt=runfmt_alias["pop_sample_run"],
    numbered=True,
)
