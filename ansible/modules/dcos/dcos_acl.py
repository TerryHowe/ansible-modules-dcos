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
    state:
        description:
            - If C(present), ensure the ACL exists with all the listed
            group and user permissions set. If C(absent), ensure the ACL
            does not exists. Defaults to C(present).
        required: false
        default: present
        choices: [ present, absent ]
'''

EXAMPLES = '''
- name: Create the ACL for package management
  dcos_acl:
     rid: "dcos:adminrouter:package"
     description: "Package management ACL"

- name: Remove the ACL for package management
  dcos_acl:
     uid: "dcos:adminrouter:package"
     state: absent
'''

from ansible.module_utils.basic import *
from ansible.module_utils import dcos


def dcos_acl_absent(params):
    client = dcos.DcosClient()
    result = client.delete('/acls/{}'.format(params['rid']))
    module.exit_json(**result)


def dcos_acl_present(params):
    client = dcos.DcosClient()
    body = {
        'description': params['description']
    }
    path = '/acls/{}'.format(params['rid'])
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
        'rid': { 'type': 'str', 'required': True },
        'description': { 'type': 'str', 'required': False },
        'state': {
            'type': 'str',
            'required': False,
            'default': 'present',
            'choices': [ 'present', 'absent' ]
        },
    })
    if module.params['state'] == 'present':
        if (module.params['description']):
            dcos_acl_present(module.params)
        module.fail_json(msg="Description required for state=present", rc=1)
    dcos_acl_absent(module.params)


if __name__ == '__main__':
    main()
