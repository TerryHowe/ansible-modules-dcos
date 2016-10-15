Ansible Modules for DC/OS
=========================

Ansible modules for DC/OS.

.. image:: https://img.shields.io/pypi/v/ansible-modules-dcos.svg
   :alt: Latest version
   :target: https://pypi.python.org/pypi/ansible-modules-dcos/

Usage
-----

Create a user::

    - hosts: localhost
      tasks:
        - dcos_user: 
            uid: "bobslydell"
            description: 'bobslydell'
            password: 'fooBar123ASDF'
            state: present
            dcos_credentials: "{{ dcos_facts.ansible_facts.dcos_credentials }}"

Create a group::

    - dcos_group: gid="bobs" description='the bobs'

Create a ACL::

    - dcos_acl:
        rid: "dcos:adminrouter:service:marathon-bobs"
        description: "Bob acl"

Add user to ACL::

    - dcos_acl_user:
        rid: "dcos:adminrouter:service:marathon-bobs"
        uid: "bobslydell"
        permission: "read"

Add group to ACL::

    - dcos_acl_group:
        rid: "dcos:adminrouter:service:marathon-bobs"
        gid: "bobs"
        permission: "read"

License
-------

MIT
