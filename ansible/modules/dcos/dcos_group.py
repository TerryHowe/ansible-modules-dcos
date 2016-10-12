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
    users:
        description:
            - List of group members, identified by uid.
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
- name: Create a DCOS group
  dcos_group:
     gid: "mygroupname"
     description: "My first group"
     users:
        - myuid1
        - myuid2

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

    changed = False
    body = {}
    path = '/groups/{}'.format(params['gid'])
    result = client.get(path)
    description = result['json'].get('description')
    if description != params['description']:
        changed = True
        body = {'description': params['description']}
        path = '/groups/{}'.format(params['gid'])
        result = client.patch(path, body)

    result = client.get('/groups/{}/users'.format(params['gid']))
    current_members = set([ x['user']['uid'] for x in result['json']['array']])
    expected_members = set(params['users'])

    changed = False
    remove_them = current_members - expected_members
    add_them = expected_members - current_members
    changed = changed or _remove_members(client, gid, remove_them)
    changed = changed or _add_members(client, gid, add_them)

def _remove_members(client, gid, members_ro_remove):
    changed = False
    for member in members_to_remove:
        changed = True
        path = '/groups/{gid}/users/{uid}'.format(gid=gid, uid=member)
        result = client.delete(path)
        if result['failed']:
            module.fail_json(**result)
    return changed


def _add_members(client, gid, members_ro_remove):
    changed = False
    for member in members_to_add:
        changed = True
        path = '/groups/{gid}/users/{uid}'.format(gid=gid, uid=member)
        result = client.put(path, {})
        if result['failed']:
            module.fail_json(**result)
    return changed


def main():
    global module
    module = AnsibleModule(argument_spec={
        'gid': { 'type': 'str', 'required': True },
        'description': { 'type': 'str', 'required': False },
        'users': { 'type': 'list', 'required': False },
        'state': {
            'type': 'str',
            'required': False,
            'default': 'present',
            'choices': [ 'present', 'absent' ]
        },
    })
    if module.params['state'] == 'present':
        if module.params['users'] and module.params['description']:
            dcos_group_present(module.params)
        else:
            module.fail_json(msg="User list and description required for state=present", rc=1)
    else:
        dcos_group_absent(module.params)


if __name__ == '__main__':
    main()
