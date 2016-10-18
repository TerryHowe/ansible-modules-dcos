#!/usr/bin/env python
from setuptools import setup

files = [
    "ansible/module_utils",
    "ansible/modules/dcos",
]

long_description = open('README.rst', 'r').read()

setup(
    name='ansible-modules-dcos',
    version='1.0.8',
    description='DCOS Ansible Modules',
    long_description=long_description,
    url='https://github.com/TerryHowe/ansible-modules-dcos',
    author='Kevin Wood,Terry Howe',
    author_email='kevin.wood@example.com',
    license='MIT',
    packages=files,
    install_requires = [
        'ansible>=2.0.0',
        'dcoscli>=0.4.5',
        'toml',
    ],
)
