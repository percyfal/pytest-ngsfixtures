#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import py


def pytest_namespace():
    d = {
        'testdir': py.path.local(os.path.abspath(os.path.dirname(__file__))),
    }
    return d
