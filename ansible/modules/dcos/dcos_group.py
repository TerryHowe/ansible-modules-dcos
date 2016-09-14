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
    ssl_verify:
        description:
            - Verify SSL certificates.
        required: false
        default: true
    dcos_credentials:
        description:
            - Credentials for actions against DCOS, acquired via C(dcos_facts).
        required: true
'''

EXAMPLES = '''
- name: Create a DCOS group
  dcos_group:
     gid: "mygroupname"
     description: "My first group"
     users:
        - myuid1
        - myuid2
     dcos_credentials: "{{ dcos_credentials }}"

- name: Remove a DCOS group
  dcos_group:
     uid: "mygroupname"
     state: absent
     dcos_credentials: "{{ dcos_credentials }}"
'''

from ansible.module_utils.basic import *
from ansible.module_utils.dcos import dcos_api


def dcos_group_absent(params):
    result = dcos_api('DELETE', '/groups/{}'.format(params['gid']), params=params)
    if result['status_code'] == 204: # Deleted
        return True, result
    if result['status_code'] == 400: # Does Not Exist
        return False, result

    module.fail_json(msg="Unrecognized response from server",
                        debug=result)


def dcos_group_present(params):
    changed, meta = _create_or_update_group(params)
    changed, meta = _add_or_modify_membership(params)
    return changed, meta


def _add_or_modify_membership(params):
    result = dcos_api('GET', '/groups/{}/users'.format(params['gid']), params=params)
    current_members = set([ x['user']['uid'] for x in result['json']['array']])
    expected_members = set(params['users'])

    changed = False
    members_to_remove = current_members - expected_members
    members_to_add = expected_members - current_members

    for member in members_to_remove:
        changed = True
        result = dcos_api('DELETE',
            '/groups/{gid}/users/{uid}'.format(gid=params['gid'], uid=member),
            params=params)
        if result['status_code'] != 204:
            module.fail_json(msg="Unable to remove user from group",
                    debug=result)

    for member in members_to_add:
        changed = True
        result = dcos_api('PUT',
            '/groups/{gid}/users/{uid}'.format(gid=params['gid'], uid=member),
            params=params)
        if result['status_code'] != 204:
            module.fail_json(msg="Unable to add user to group",
                    debug=result)

    return changed, result


def _create_or_update_group(params):
    body = {
        'description': params['description']
    }
    result = dcos_api('PUT', '/groups/{}'.format(params['gid']), body=body, params=params)
    if result['status_code'] == 201:
        return True, result

    elif result['status_code'] != 409:
        module.fail_json(msg="Unrecognized response from server",
                            debug=result)

    changed = False
    body = {}
    result = dcos_api('GET', '/groups/{}'.format(params['gid']), params=params)
    description = result['json'].get('description')
    if description != params['description']:
        changed = True
        body['description'] = params['description']

    if not changed:
        return False, result

    result = dcos_api('PATCH', '/groups/{}'.format(params['gid']), body=body, params=params)
    if result['status_code'] == 204:
        return True, result

    module.fail_json(msg='Unrecognized response from server',
                        debug=result)


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
        'ssl_verify': { 'type': 'bool', 'required': False, 'default': True },
        'dcos_credentials': { 'type': 'dict', 'required': True },
    })
    if module.params['state'] == 'present':
        if module.params['users'] and module.params['description']:
            has_changed, meta = dcos_group_present(module.params)
        else:
            module.fail_json(msg="User list and description required for state=present")
    else:
        has_changed, meta = dcos_group_absent(module.params)

    module.exit_json(changed=has_changed, meta=meta)


if __name__ == '__main__':
    main()
