#!/usr/bin/python

DOCUMENTATION = '''
---
module: dcos_package
short_description: Manage packages on DCOS
options:
    package:
        description: Name of the package to be installed.
        required: true
    app_id:
        description: Marathon app-id.
        required: true
    options:
        description:
            - Options passed to the C(dcos package install) command via JSON.
            See Marathon documentation for available options.
        required: false
    state:
        description:
            - If C(present), ensure the package is installed. If C(absent),
            ensure the package is not installed. Defaults to C(present).
        required: false
        default: present
        choices: [ present, absent ]
    delete_empty_group:
        description:
            - Delete the marathon group from which the package was uninstalled
            if it was the last item removed from the group. To leave an emtpy
            group, set this to C(false). Defaults to C(true).
        required: false
        default: true
    dcos_credentials:
        description:
            - Credentials for actions against DCOS, acquired via C(dcos_facts).
        required: true
'''

EXAMPLES = '''
- name: Install Marathon for a user
  dcos_package:
    package: marathon
    app_id: "/testuser/marathon-testuser"
    options:
      service:
        name: "marathon-testuser"
        cpus: 2.0
        mem: 1536
        instances: 1
    dcos_credentials: "{{ dcos_credentials }}"

- name: Uninstall user Marathon
  dcos_package:
     package: marathon
     app_id: "/testuser/marathon-testuser"
     state: absent
     dcos_credentials: "{{ dcos_credentials }}"
'''

import json
import os
import subprocess
import tempfile
from ansible.module_utils.basic import *
from ansible.module_utils.dcos import dcos_api


def dcos_cli(args):
    command = [ 'dcos' ]
    command.extend(args)
    p = subprocess.Popen(command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                close_fds=True)
    stdout = p.communicate()[0]
    rc = p.returncode
    return rc, stdout


def _check_installed_packages(params):
    rc, output = dcos_cli(['package', 'list', '--json'])
    package_list = json.loads(output)
    for package in package_list:
        if params['app_id'] in package['apps']:
            if params['package'] == package['name']:
                # package already installed
                return True, package_list
            else:
                # wrong package installed at app_id!
                module.fail_json(msg='Wrong package ({package}) installed at app_id ({appid})!'.format(
                        package=package['name'], appid=params['app_id']
                    ))
    return False, package_list


def _clean_up_group(params):
    if not params['delete_empty_group']:
        return False

    # check if group is empty, delete it if so
    appid = params['app_id']
    if appid.rfind('/') == 0:
        # we're at the root. no deleting the root!
        return False
    group_id = appid[:appid.rfind('/')]
    group_list_command = [ 'marathon', 'group', 'show' ]
    group_list_command.append(group_id)
    rc, output = dcos_cli(group_list_command)
    if 'does not exist' in output:
        # group doesn't exist
        return False
    group_list = json.loads(output)
    if len(group_list['apps']) != 0:
        # group contains other packages
        return False
    group_delete_command = [ 'marathon', 'group', 'remove' ]
    group_delete_command.append(group_id)
    rc, output = dcos_cli(group_delete_command)
    if rc != 0:
        module.fail_json(msg='Failed to delete group',
                debug={'output': output, 'deletecommand': group_delete_command})
    return True


def dcos_package_absent(params):
    installed, package_list = _check_installed_packages(params)
    if not installed:
        group_clean = _clean_up_group(params)
        return group_clean or False, package_list

    uninstall_command = ['package', 'uninstall',
                            '--app-id={}'.format(params['app_id']),
                            params['package']]
    rc, output = dcos_cli(uninstall_command)
    if rc != 0:
        module.fail_json(msg='Failed to uninstall package',
                debug={'output': output, 'uninstall_command': uninstall_command})

    _clean_up_group(params)

    return True, params


def dcos_package_present(params):
    installed, package_list = _check_installed_packages(params)
    if installed:
        return False, package_list

    # package is missing, install it
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, 'w') as f:
        json.dump(params['options'], f)
    install_command = [ 'package', 'install', params['package'], '--yes' ]
    install_command.append('--app-id={}'.format(params['app_id']))
    install_command.append('--options={}'.format(path))
    rc, output = dcos_cli(install_command)
    if rc != 0:
        module.fail_json(msg='Installation failed', debug=output)
    os.remove(path)

    # TODO: conditionally poll for successful startup (needed for jenkins)

    return False, output


def main():
    global module
    module = AnsibleModule(argument_spec={
        'package': { 'type': 'str', 'required': True },
        'app_id': { 'type': 'str', 'required': True },
        'options': { 'type': 'dict', 'required': False, 'default': {} },
        'state': {
            'type': 'str',
            'required': False,
            'default': 'present',
            'choices': [ 'present', 'absent' ]
        },
        'delete_empty_group': { 'type': 'bool', 'required': False, 'default': True },
        'dcos_credentials': { 'type': 'dict', 'required': True },
    })
    if module.params['state'] == 'present':
        if module.params['options']:
            has_changed, meta = dcos_package_present(module.params)
        else:
            module.fail_json(msg='Options required for state=present')
    else:
        has_changed, meta = dcos_package_absent(module.params)
    module.exit_json(changed=has_changed, meta=meta)


if __name__ == '__main__':
    main()
