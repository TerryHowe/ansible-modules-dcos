#!/usr/bin/python

DOCUMENTATION = '''
---
module: dcos_facts
short_description: Load DCOS-related facts
'''

EXAMPLES = '''
- name: Load DCOS-related facts
  dcos_facts:

 - name: Print out the DCOS credentials
   debug: msg="{{ dcos_credentials }}"
'''
import requests
import subprocess
from ansible.module_utils.basic import *


def main():
    module = AnsibleModule(argument_spec={})
    token = subprocess.check_output(["dcos", "config", "show", "core.dcos_acs_token"]).rstrip()
    url = subprocess.check_output(["dcos", "config", "show", "core.dcos_url"]).rstrip()
    if not url.endswith('/'):
        url = url + '/'
    facts = {
        'dcos_credentials': { 'token': token, 'url': url }
    }
    module.exit_json(changed=False, ansible_facts=facts)


if __name__ == '__main__':
    main()
