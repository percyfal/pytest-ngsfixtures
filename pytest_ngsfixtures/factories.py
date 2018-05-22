# -*- coding: utf-8 -*-
import logging
import itertools
import pytest
from pytest_ngsfixtures.os import safe_mktemp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
