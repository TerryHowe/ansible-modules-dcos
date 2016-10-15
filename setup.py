#!/usr/bin/env python
from distutils.core import setup

files = [
    "ansible/module_utils",
    "ansible/modules/dcos",
]

long_description = """

Ansible modules for Mesospher DC/OS.  Modules exist to create users, groups and acls.

Usage
-----

The following example creates user bob::

    ---
    - hosts: localhost
      tasks:
        - dcos_user: 
            uid: "bobslydell"
            description: 'Bob Slydell'
            password: 'fooBar123ASDF'
            state: present

"""

setup(name='ansible-modules-dcos',
      version='1.0.0',
      description='DCOS Ansible Modules',
      long_description=long_description,
      url='https://github.com/TerryHowe/ansible-modules-dcos',
      author='Kevin Wood',
      author_email='kevin.wood@example.com',
      license='MIT',
      packages=files,
      install_requires = [
        'ansible>2.0.0',
        'dcoscli>0.4.5',
        'toml',
      ],
)
