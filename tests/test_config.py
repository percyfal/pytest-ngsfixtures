#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from pytest_ngsfixtures.config import ref, layout, SAMPLES_DIR


@pytest.mark.samples(layout=[2,1])
@pytest.mark.xfail(strict=True)
def test_samples_list(samples):
    pass


@pytest.mark.samples(numbered=True)
@pytest.mark.parametrize("layout,dirname", [(layout['flat'], "flat"),
                                            (layout['sample'], "sample")])
def test_samples(samples, ref, layout, dirname):
    pass

@pytest.mark.ref(dirname="Foo",
                 copy=True,
                 data=ref,
                 numbered=True)
def test_ref(ref):
    pass
