#!/usr/bin/python

DOCUMENTATION = '''
---
module: dcos_user
short_description: Manage users on DCOS
options:
    uid:
        description:
            - The unique name for the user account.
        required: true
    password:
        description:
            - Password for the user account. Required for C(state=present).
        required: false
    description:
        description:
            - Optional account description during account creation.
        required: false
    reset_password:
        description:
            - Set the password if the user account exists regardless of
            whether the password has been changed by the user. This will
            always result in C(changed=true).
        required: false
        default: false
    state:
        description:
            - If C(present), ensure the user account exists. If C(absent),
            ensure the user account does not exists. Will not change the
            password for accounts that already exists, unless C(reset_password)
            is true. Defaults to C(present).
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
- name: Create a DCOS user
  dcos_user:
     uid: "myusername"
     password: "s3cr3t"
     description: "My first user account"
     dcos_credentials: "{{ dcos_credentials }}"

- name: Remove a DCOS user
  dcos_user:
     uid: "myusername"
     state: absent
     dcos_credentials: "{{ dcos_credentials }}"
'''

from ansible.module_utils.basic import *
from ansible.module_utils.dcos import dcos_api


def dcos_user_absent(params):
    result = dcos_api('DELETE', '/users/{}'.format(params['uid']), params=params)
    if result['status_code'] == 204: # Deleted
        return True, result
    if result['status_code'] == 400: # Does Not Exist
        return False, result

    module.fail_json(msg="Unrecognized response from server",
                        debug=result)


def dcos_user_present(params):
    body = {
        'description': params['description'],
        'password': params['password'],
    }
    result = dcos_api('PUT', '/users/{}'.format(params['uid']), body=body, params=params)
    if result['status_code'] == 201:
        return True, result

    elif result['status_code'] != 409:
        module.fail_json(msg="Unrecognized response from server",
                            debug=result)

    changed = False
    body = {}
    result = dcos_api('GET', '/users/{}'.format(params['uid']), params=params)
    description = result['json'].get('description')
    if description != params['description']:
        changed = True
        body['description'] = params['description']
    if params['reset_password']:
        changed = True
        body['password'] = params['password']

    if not changed:
        return False, result

    result = dcos_api('PATCH', '/users/{}'.format(params['uid']), body=body, params=params)
    if result['status_code'] == 204:
        return True, result

    module.fail_json(msg="Unrecognized response from server",
                        debug=result)


def main():
    global module
    module = AnsibleModule(argument_spec={
        'uid': { 'type': 'str', 'required': True },
        'password': { 'type': 'str', 'required': False },
        'description': { 'type': 'str', 'required': False },
        'reset_password': { 'type': 'bool', 'required': False, 'default': False },
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
        if module.params['password'] and module.params['description']:
            has_changed, meta = dcos_user_present(module.params)
        else:
            module.fail_json(msg="Password and description required for state=present")
    else:
        has_changed, meta = dcos_user_absent(module.params)
    module.exit_json(changed=has_changed, meta=meta)


if __name__ == '__main__':
    main()
