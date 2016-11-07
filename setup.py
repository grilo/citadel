#!/usr/bin/env python
# -*- coding: utf-8 -*-

import distutils.core

#from setuptools import setup, find_packages

long_description = ('Information and documentation at https://github.com/grilo/citadel')

distutils.core.setup(
    name='citadel',
    version='1.0',
    author='João Grilo',
    author_email='joao.grilo@gmail.com',
    url='https://github.com/grilo/citadel',
    license='GPLv2',
    description='Generate a build script from a yml file.',
    long_description=long_description,
    packages=['citadel', 'citadel/nodes', 'citadel/yaml'],
    include_package_data=True,
    platforms=['any'],
    scripts=['citadel-generate'],
    classifiers=[
        'Topic :: Software Development :: Libraries',
        'Natural Language :: English',
        'License :: Freely Distributable',
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
