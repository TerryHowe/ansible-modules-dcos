#!/usr/bin/env python
#
# DC/OS Token Header Lookup Plugin
#
# A simple example of using the DC/OS Token header plugin in a role:
#    ---
#    - debug: msg="{{lookup('dcos_token_header')}}"
#
# The plugin can be run manually for testing:
#     python ansible/plugins/lookup/dcos_token_header.py
#
import json
import os
import requests
import sys
from urlparse import urljoin
import warnings

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.modules.dcos import dcos_token


class LookupModule(LookupBase):

    def run(self, terms, variables, **kwargs):
        result = dcos_token.get_token()
        if 'value' not in result:
            raise AnsibleError('Error reading DC/OS token: %s' % result.get('msg', 'msg not set'))
        return [{'Authorization': 'token=' + result['value']}]


def main(argv=sys.argv[1:]):
    print LookupModule().run(argv, None)[0]
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
