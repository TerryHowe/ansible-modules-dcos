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
'''

EXAMPLES = '''
- name: Create a DCOS user
  dcos_user:
     uid: "myusername"
     password: "s3cr3t"
     description: "My first user account"

- name: Remove a DCOS user
  dcos_user:
     uid: "myusername"
     state: absent
'''

from ansible.module_utils.basic import *
from ansible.module_utils import dcos


def dcos_user_absent(params):
    client = dcos.DcosClient()
    result = client.delete('/users/{}'.format(params['uid']))
    module.exit_json(**result)


def dcos_user_present(params):
    body = {
        'description': params['description'],
        'password': params['password'],
    }
    client = dcos.DcosClient()
    result = client.put('/users/{}'.format(params['uid']), body=body)
    if result['changed']:
        module.exit_json(**result)
    elif result['status_code'] != 409:
        module.fail_json(**result)

    changed = False
    body = {}
    result = client.get('/users/{}'.format(params['uid']))
    description = result['json'].get('description')
    if description != params['description']:
        changed = True
        body['description'] = params['description']
    if params['reset_password']:
        changed = True
        body['password'] = params['password']

    if not changed:
        module.exit_json(**result)

    result = client.patch('/users/{}'.format(params['uid']), body=body)
    if result['status_code'] == 204:
        module.exit_json(**result)

    module.fail_json(**result)


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
    })
    if module.params['state'] == 'present':
        if module.params['password'] and module.params['description']:
            dcos_user_present(module.params)
        else:
            module.fail_json(msg="Password and description required for state=present", rc=1)
    else:
        dcos_user_absent(module.params)


if __name__ == '__main__':
    main()
