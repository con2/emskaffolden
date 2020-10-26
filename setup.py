#!/usr/bin/env python

import os
from setuptools import find_packages, setup


with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='emskaffolden',
    version='0.1.2',
    description='Use Skaffold with Emrichen templates',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    author='Santtu Pajukanta',
    author_email='santtu@pajukanta.fi',
    url='http://github.com/con2/emskaffolden',
    packages = find_packages(exclude=["tests"]),
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'emskaffolden = emskaffolden.__main__:main',
            'emsk = emskaffolden.__main__:main',
        ]
    },
    install_requires=["emrichen", "PyYAML", "pyaml", "jsonpath-rw~=1.4.0"],
    tests_require=["pytest"],
    setup_requires=["pytest-runner"],
)
