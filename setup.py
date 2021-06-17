#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(name='isrun',
        version='0.0.1',
        description='IST server run',
        author='laphon',
        packages=find_packages(),
        scripts=['bin/isrun'],
        install_requires=['sh', 'paramiko'],
        )
