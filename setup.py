#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import versioneer
from os.path import realpath, dirname, relpath, join
from setuptools import setup

ROOT = dirname(realpath(__file__))

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'pytest>=3.0.0',
    'pyyaml',
    'snakemake',
]

test_requirements = [
    'pytest>=3.0.0',
]

package_data = []

scripts = [
    'scripts/pytest_ngsfixtures_download_data.py',
    'scripts/pytest_ngsfixtures_add_application.py',
]


def package_path(path, filters=()):
    if not os.path.exists(path):
        raise RuntimeError("packaging non-existent path: %s" % path)
    elif os.path.isfile(path):
        package_data.append(relpath(path, 'bioodo'))
    else:
        for path, dirs, files in os.walk(path):
            path = relpath(path, 'bioodo')
            for f in files:
                if not filters or f.endswith(filters):
                    package_data.append(join(path, f))

package_path(join(ROOT, "pytest_ngsfixtures", "data"))

setup(
    name='pytest_ngsfixtures',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="pytest ngs fixtures",
    long_description=readme + '\n\n' + history,
    author="Per Unneberg",
    author_email='per.unneberg@scilifelab.se',
    url='https://github.com/percyfal/pytest-ngsfixtures',
    packages=[
        'pytest_ngsfixtures',
    ],
    package_data={'pytest_ngsfixtures/data': package_data},
    include_package_data=True,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='pytest_ngsfixtures',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    install_requires=requirements,
    setup_requires=['pytest-runner'],
    tests_require=test_requirements,
    entry_points = {'pytest11':['pytest_ngsfixtures = pytest_ngsfixtures.plugin']},
    scripts = scripts,
)
