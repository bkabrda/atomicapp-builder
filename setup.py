#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='atomicapp-builder',
    version='0.0.1',
    description='Application for building Atomicapps',
    long_description=''.join(open('README.md').readlines()),
    keywords='atomic, atomicapp, docker, nulecule',
    author='Slavek Kabrda',
    author_email='slavek@redhat.com',
    license='BSD',
    packages=['atomicapp_builder'],
    entry_points={
        'console_scripts': ['atomicapp-builder=atomicapp_builder.cli:run'],
    },
    # TODO: parse this from requirements.txt when dock is distributed through PyPI
    install_requires=[
        'anymarkup',
        'dock==1.3.5',
        'requests',
    ],
    dependency_links=[
        'https://github.com/DBuildService/dock/tarball/master#egg=dock-1.3.5',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        ]
)
