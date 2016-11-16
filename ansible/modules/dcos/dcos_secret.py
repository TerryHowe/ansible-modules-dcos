#!/usr/bin/python

DOCUMENTATION = '''
---
module: dcos_secret
short_description: Manage secrets on DCOS
options:
    path:
        description:
            - Path of secret.
        required: true
    key:
        description:
            - key of secret.
        required: false
    value:
        description:
            - Value of secret.
        required: false
    state:
        description:
            - If C(present), ensure the secret exists with all the given
            value. If C(absent), ensure the secret does not exists.
            Defaults to C(present).
        required: false
        default: present
        choices: [ present, absent ]
'''

EXAMPLES = '''
- name: Create the ACL for package management
  dcos_secret:
     path: "azurediamond/password"
     value: "hunter2"

- name: Remove the ACL for package management
  dcos_secret:
     path: "azurediamond/password"
     state: absent
'''

from ansible.module_utils.basic import *
from ansible.module_utils import dcos



def dcos_secret_absent(params):
    client = dcos.DcosClient(service_path='/secrets/v1')
    result = client.delete('/secret/default/{}'.format(params['path']))
    if result['status_code'] == 404:
        result['failed'] = False
        result['rc'] = 0
    module.exit_json(**result)


def dcos_secret_present(params):
    client = dcos.DcosClient(service_path='/secrets/v1')
    body = {
        params['key']: params['value']
    }
    path = '/secret/default/{}'.format(params['path'])
    result = client.put(path, body)
    if result['changed']:
        module.exit_json(**result)
    elif result['status_code'] != 409:
        module.fail_json(**result)
    result = client.patch(path, body)
    module.exit_json(**result)


def dcos_secret_get(params):
    client = dcos.DcosClient(service_path='/secrets/v1')
    path = '/secret/default/{}'.format(params['path'])
    result = client.get(path)
    data = result['json']
    if params['key'] in data:
        result['value'] = data[params['key']]
    module.exit_json(**result)


def main():
    global module
    module = AnsibleModule(argument_spec={
        'path': { 'type': 'str', 'required': True },
        'key': { 'type': 'str', 'required': False, 'default': 'value' },
        'value': { 'type': 'str', 'required': False },
        'state': {
            'type': 'str',
            'required': False,
            'default': 'present',
            'choices': [ 'present', 'absent' ]
        },
    })
    if module.params['state'] == 'present':
        if (module.params['value']):
            dcos_secret_present(module.params)
        else:
            dcos_secret_get(module.params)
    dcos_secret_absent(module.params)


if __name__ == '__main__':
    main()
