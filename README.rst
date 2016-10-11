Ansible Modules for DC/OS
=========================

Ansible modules for Hashicorp Vault.

.. image:: https://img.shields.io/pypi/v/ansible-modules-dcos.svg
   :alt: Latest version
   :target: https://pypi.python.org/pypi/ansible-modules-dcos/

Usage
-----

Create a user::

    ---
    - hosts: localhost
      tasks:
        - dcos_user: 
            uid: "bob"
            description: 'bob'
            password: 'fooBar123ASDF'
            state: present
            dcos_credentials: "{{ dcos_facts.ansible_facts.dcos_credentials }}"

License
-------

MIT
