#!/usr/bin/python

DOCUMENTATION = '''
---
module: dcos_token
short_description: Get DCOS token
'''

EXAMPLES = '''
- name: Get DCOS token
  dcos_token:
    register: "dcos_token"
'''

from ansible.module_utils.basic import *
from ansible.module_utils import dcos


def main():
    global module
    module = AnsibleModule(argument_spec={})
    client = dcos.DcosClient()
    result = {
        'changed': False,
        'rc': 0,
        'failed': False,
        'value': client.token,
    }
    module.exit_json(**result)


if __name__ == '__main__':
    main()
