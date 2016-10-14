#!/usr/bin/python

DOCUMENTATION = '''
---
module: dcos_group
short_description: Manage groups on DCOS
options:
    gid:
        description:
            - The unique name for the group account.
        required: true
    description:
        description:
            - Optional group description during group creation.
        required: false
    state:
        description:
            - If C(present), ensure the group exists. If C(absent),
            ensure the group does not exists. Defaults to C(present).
        required: false
        default: present
        choices: [ present, absent ]
'''

EXAMPLES = '''
- name: Create a DCOS group
  dcos_group:
     gid: "mygroupname"
     description: "My first group"

- name: Remove a DCOS group
  dcos_group:
     uid: "mygroupname"
     state: absent
'''

from ansible.module_utils.basic import *
from ansible.module_utils import dcos


def dcos_group_absent(params):
    client = dcos.DcosClient()
    result = client.delete('/groups/{}'.format(params['gid']))
    module.exit_json(**result)


def dcos_group_present(params):
    client = dcos.DcosClient()
    body = {
        'description': params['description']
    }
    path = '/groups/{}'.format(params['gid'])
    result = client.put(path, body)
    if result['changed']:
        module.exit_json(**result)
    elif result['status_code'] != 409:
        module.fail_json(**result)
    result = client.patch(path, body)
    module.exit_json(**result)


def main():
    global module
    module = AnsibleModule(argument_spec={
        'gid': { 'type': 'str', 'required': True },
        'description': { 'type': 'str', 'required': False },
        'state': {
            'type': 'str',
            'required': False,
            'default': 'present',
            'choices': [ 'present', 'absent' ]
        },
    })
    if module.params['state'] == 'present':
        if module.params['description']:
            dcos_group_present(module.params)
        module.fail_json(msg="User list and description required for state=present", rc=1)
    dcos_group_absent(module.params)


if __name__ == '__main__':
    main()
