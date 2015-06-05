#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup, find_packages

setup(
    name='atomicapp_builder',
    version='0.0.1',
    description='Application for building Atomicapps',
    long_description=''.join(open('README.rst').readlines()),
    keywords='atomic, atomicapp, docker, nulecule',
    author='Slavek Kabrda',
    author_email='slavek@redhat.com',
    license='BSD',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['atomicapp-builder=atomicapp_builder.cli:run'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        ]
)
