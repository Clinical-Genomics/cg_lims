#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='cg_lims',
        version='1.0',
        description='',
        author='Maya Brandi',
        author_email='maya.brandi@scilifelab.se',
        packages=find_packages(),
        include_package_data=True,
        entry_points={
        'console_scripts': ['epps=cg_lims.commands:cli'],
    },

     )
