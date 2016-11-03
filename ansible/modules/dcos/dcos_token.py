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


def get_token():
    client = dcos.DcosClient()
    return {
        'changed': False,
        'rc': 0,
        'failed': False,
        'value': client.token,
    }


def main():
    global module
    module = AnsibleModule(argument_spec={})
    module.exit_json(**get_token())


if __name__ == '__main__':
    main()
