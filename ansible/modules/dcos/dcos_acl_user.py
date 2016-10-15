#!/usr/bin/python

DOCUMENTATION = '''
---
module: dcos_acl_user
short_description: Manage acl users
options:
    rid:
        description:
            - Identifier of the resource being controlled.
        required: true
    uid:
        description:
            - User id to modify.
        required: false
    permission:
        description:
            - Permission on the resource e.g. read, full, ...
        required: false
    state:
        description:
            - If C(present), add the permission to the resource.
            If C(absent), remove the permission from the resource.
            Defaults to C(present).
        required: false
        default: present
        choices: [ present, absent ]
'''

EXAMPLES = '''
- name: Create the ACL for resource
  dcos_acl_user:
     rid: "dcos:adminrouter:ops:metadata"
     uid: "bobone"
     permission: "read"

- name: Remove the ACL for resource
  dcos_acl_user:
     rid: "dcos:adminrouter:ops:metadata"
     uid: "bobone"
     state: absent
'''

from ansible.module_utils.basic import *
from ansible.module_utils import dcos


def dcos_acl_user_absent(params):
    client = dcos.DcosClient()
    path = '/acls/{rid}/users/{uid}/{permission}'.format(**params)
    result = client.delete(path)
    module.exit_json(**result)


def dcos_acl_user_present(params):
    client = dcos.DcosClient()
    body = {
        'description': params['rid']
    }
    path = '/acls/{rid}/users/{uid}/{permission}'.format(**params)
    result = client.put(path)
    module.exit_json(**result)


def main():
    global module
    module = AnsibleModule(argument_spec={
        'rid': { 'type': 'str', 'required': True },
        'uid': { 'type': 'str', 'required': True },
        'permission': { 'type': 'str', 'required': True },
        'state': {
            'type': 'str',
            'required': False,
            'default': 'present',
            'choices': [ 'present', 'absent' ]
        },
    })
    if module.params['state'] == 'present':
        dcos_acl_user_present(module.params)
        module.fail_json(msg="Description required for state=present", rc=1)
    dcos_acl_user_absent(module.params)


if __name__ == '__main__':
    main()
