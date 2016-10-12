#!/usr/bin/python

DOCUMENTATION = '''
---
module: dcos_group_member
short_description: Manage groups members on DCOS
options:
    gid:
        description:
            - The unique name for the group account.
        required: true
    uid:
        description:
            - The uid of a user
        required: true
    state:
        description:
            - If C(present), ensure the group exists. If C(absent),
            ensure the group does not exists. Defaults to C(present).
        required: false
        default: present
        choices: [ present, absent ]
'''

EXAMPLES = '''
- name: Add a DCOS group member
  dcos_group_member:
     gid: "mygroupname"
     uid: "myuid1"

- name: Remove a DCOS group member
  dcos_group_member:
     gid: "mygroupname"
     uid: "myuid1"
     state: absent
'''

from ansible.module_utils.basic import *
from ansible.module_utils import dcos


def dcos_group_member_absent(params):
    client = dcos.DcosClient()
    gid = params['gid']
    uid = params['uid']
    path = '/groups/{gid}/users/{uid}'.format(gid=gid, uid=uid)
    result = client.delete(path)
    module.exit_json(**result)


def dcos_group_member_present(params):
    client = dcos.DcosClient()
    gid = params['gid']
    uid = params['uid']
    path = '/groups/{gid}/users/{uid}'.format(gid=gid, uid=uid)
    result = client.put(path, {})
    if result['changed']:
        module.exit_json(**result)
    elif result['status_code'] != 409:
        module.fail_json(**result)
    result['changed'] = False
    result['failed'] = False
    result['rc'] = 0
    module.exit_json(**result)


def main():
    global module
    module = AnsibleModule(argument_spec={
        'gid': { 'type': 'str', 'required': True },
        'uid': { 'type': 'str', 'required': True },
        'state': {
            'type': 'str',
            'required': False,
            'default': 'present',
            'choices': [ 'present', 'absent' ]
        },
    })
    if module.params['state'] == 'present':
        dcos_group_member_present(module.params)
    else:
        dcos_group_member_absent(module.params)


if __name__ == '__main__':
    main()
