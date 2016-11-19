#!/usr/bin/env python
from setuptools import setup

py_files=[
    "ansible/module_utils/dcos",
    "ansible/plugins/lookup/dcos_token",
    "ansible/plugins/lookup/dcos_token_header",
]
files = [
    "ansible/modules/dcos",
]

long_description = open('README.rst', 'r').read()

setup(
    name='ansible-modules-dcos',
    version='1.4.0',
    description='DCOS Ansible Modules',
    long_description=long_description,
    url='https://github.com/TerryHowe/ansible-modules-dcos',
    author='Kevin Wood,Terry Howe',
    author_email='kevin.wood@example.com',
    license='MIT',
    py_modules=py_files,
    packages=files,
    install_requires = [
        'ansible>=2.0.0',
        'dcoscli>=0.4.5',
        'toml',
    ],
)
