#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

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
    install_requires=open('requirements.txt').read().splitlines(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        ]
)
