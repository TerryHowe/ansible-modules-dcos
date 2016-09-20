#!/usr/bin/python

DOCUMENTATION = '''
---
module: dcos_acl
short_description: Manage ACLs on DCOS
options:
    rid:
        description:
            - Identifier of the resource being controlled.
        required: true
    description:
        description:
            - Optional ACL description used during ACL creation.
        required: false
    group_permissions:
        description:
            - Dictionary of groups and their assigned permissions. Valid
            properties include C(gid) to identify the group and C(action)
            with a comma separated list of actions C(full), C(create),
            C(read), C(update), or C(delete). The default C(action) is C(read).
        required: false
    user_permissions:
        description:
            - Dictionary of users and their assigned permissions. Valid
            properties include C(uid) to identify the user and C(action)
            with a comma separated list of actions: C(full), C(create),
            C(read), C(update), or C(delete). The default C(action) is C(read).
        required: false
    state:
        description:
            - If C(present), ensure the ACL exists with all the listed
            group and user permissions set. If C(absent), ensure the ACL
            does not exists. Defaults to C(present).
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
- name: Create the ACL for package management
  dcos_acl:
     rid: "dcos:adminrouter:package"
     description: "Package management ACL"
     group_permissions:
        - gid: "admingroup"
          action: full
     user_permissions:
        - uid: "auseraccount"
          action: read,update
     dcos_credentials: "{{ dcos_credentials }}"

- name: Remove the ACL for package management
  dcos_acl:
     uid: "dcos:adminrouter:package"
     state: absent
     dcos_credentials: "{{ dcos_credentials }}"
'''

from ansible.module_utils.basic import *
from ansible.module_utils.dcos import dcos_api


def dcos_acl_absent(params):
    result = dcos_api('GET', '/acls/{}/permissions'.format(params['rid']), params=params)
    changed, meta = _add_or_modify_membership('users', 'uid', None, result, params)
    changed, meta = _add_or_modify_membership('groups', 'gid', None, result, params)

    result = dcos_api('DELETE', '/acls/{}'.format(params['rid']), params=params)
    if result['status_code'] == 204:
        return True, result

    else:
        module.fail_json(msg='Unrecognized response from server',
                            debug=result)

    return False, params


def dcos_acl_present(params):
    changed, meta = _create_or_update_acl(params)

    result = dcos_api('GET', '/acls/{}/permissions'.format(params['rid']), params=params)
    changed, meta = _add_or_modify_membership('users', 'uid', 'user_permissions', result, params)
    changed, meta = _add_or_modify_membership('groups', 'gid', 'group_permissions', result, params)
    return changed, meta


def _add_or_modify_membership(type_label, id_label, section, result, params):
    current_permissions = set()
    for actor in result['json'][type_label]:
        for action in actor['actions']:
            current_permissions.add( (actor[id_label], action['name']) )
    expected_permissions = set()
    if section: # if no section, all permissions will be removed
        for actor in params[section]:
            for action in actor.get('action', 'read').split(','):
                expected_permissions.add( (actor[id_label], action.strip()) )

    changed = False
    permissions_to_remove = current_permissions - expected_permissions
    permissions_to_add = expected_permissions - current_permissions

    for permission in permissions_to_remove:
        changed = True
        result = dcos_api('DELETE',
            '/acls/{rid}/{type_label}/{actor_id}/{action}'.format(
                    rid=params['rid'],
                    type_label=type_label,
                    actor_id=permission[0],
                    action=permission[1]),
            params=params)
        if result['status_code'] != 204:
            module.fail_json(msg='Unable to remove permission',
                                debug=result)

    for permission in permissions_to_add:
        changed = True
        result = dcos_api('PUT',
            '/acls/{rid}/{type_label}/{actor_id}/{action}'.format(
                    rid=params['rid'],
                    type_label=type_label,
                    actor_id=permission[0],
                    action=permission[1]),
            params=params)
        if result['status_code'] != 204:
            module.fail_json(msg='Unable to add permission',
                                debug=result)

    return changed, result


def _create_or_update_acl(params):
    body = {
        'description': params['description']
    }
    result = dcos_api('PUT', '/acls/{}'.format(params['rid']), body=body, params=params)
    if result['status_code'] == 201:
        return True, result

    elif result['status_code'] != 409:
        module.fail_json(msg='Unrecognized response from server',
                            debug=result)

    changed = False
    body = {}
    result = dcos_api('GET', '/acls/{}'.format(params['rid']), params=params)
    description = result['json'].get('description')
    if description != params['description']:
        changed = True
        body['description'] = params['description']

    if not changed:
        return False, result

    result = dcos_api('PATCH', '/acls/{}'.format(params['rid']), body=body, params=params)
    if result['status_code'] == 204:
        return True, result

    module.fail_json(msg='Unrecognized response from server',
                        debug=result)


def main():
    global module
    module = AnsibleModule(argument_spec={
        'rid': { 'type': 'str', 'required': True },
        'description': { 'type': 'str', 'required': False },
        'group_permissions': { 'type': 'list', 'required': False, 'default': [] },
        'user_permissions': { 'type': 'list', 'required': False, 'default': [] },
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
        if (module.params['description']
                and (module.params['group_permissions']
                or module.params['user_permissions'])):
            has_changed, meta = dcos_acl_present(module.params)
        else:
            module.fail_json(msg="Permissions and description required for state=present")
    else:
        has_changed, meta = dcos_acl_absent(module.params)

    module.exit_json(changed=has_changed, meta=meta)


if __name__ == '__main__':
    main()
