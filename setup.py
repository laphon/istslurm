#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(name='istslurm',
        version='0.0.1',
        description='IST cluster remote job submission',
        author='laphon',
        packages=find_packages(),
        scripts=['bin/istslurm'],
        install_requires=['sh'],
        )
