#!/usr/bin/env python

from setuptools import setup, find_packages

try:
    with open("requirements.txt", "r") as f:
        install_requires = [x.strip() for x in f.readlines()]
except IOError:
    install_requires = []


setup(name='cg_lims',
        version='1.0',
        description='',
        author='Maya Brandi',
        author_email='maya.brandi@scilifelab.se',
        packages=find_packages(),
        include_package_data=True,
        entry_points={
        'console_scripts': ['lims=cg_lims.commands:cli'],
    },

     )
