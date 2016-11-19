#!/usr/bin/python

DOCUMENTATION = '''
---
module: dcos_marathon_leader
short_description: Manage secrets on DCOS
options:
'''

EXAMPLES = '''
- name: Get the marathon leader
  dcos_marathon_leader:
    register: marathon_leader
'''

from ansible.module_utils.basic import *
from ansible.module_utils import dcos



def dcos_marathon_leader(params):
    client = dcos.DcosClient(service_path='/service/marathon/v2')
    result = client.get('/leader')
    if 'json' in result:
        if 'leader' in result['json']:
            result['leader'] = result['json']['leader']
    module.exit_json(**result)


def main():
    global module
    module = AnsibleModule(argument_spec={})
    dcos_marathon_leader(module.params)


if __name__ == '__main__':
    main()
