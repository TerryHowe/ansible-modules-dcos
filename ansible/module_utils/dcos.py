from os.path import expanduser
import requests
import toml
import urlparse


class DcosClient:
    def __init__(self):
        core = self._read_configuration()
        self.token = core.get('dcos_acs_token', '')
        if not self.token:
            subprocess.check_output("dcos auth login".split())
            core = self._read_configuration()
            self.token = core.get('dcos_acs_token', 'bogus')
        self.url = self._parse_url(core.get('dcos_url', ''))
        self.ssl_verify = core.get('ssl_verify', True)

    def _read_configuration(self):
        home = expanduser("~")
        with open("{}/.dcos/dcos.toml".format(home)) as conffile:
            try:
                config = toml.loads(conffile.read())
                return config.get('core', {})
            except Exception as e:
                raise Exception("Error parsing dcos.toml file: " + str(e))

    def _parse_url(self, url):
        result = urlparse.urlsplit(url)
        netloc = result.netloc.split('@')[-1]
        result = result._replace(netloc=netloc)
        path = "acs/api/v1{endpoint}"
        result = result._replace(path=path)
        return urlparse.urlunsplit(result)

    def _get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': "token={}".format(self.token),
        }

    def _result_create(self, response, url, headers, body=""):
        result = {
            'changed': False,
            'rc': 0,
            'failed': False,
        }
        result['status_code'] = response.status_code
        if result['status_code'] >= 300:
            result['rc'] = 1
            result['failed'] = True
            result['debug'] = {
                'text': response.text,
                'request': {
                    'url': url,
                    'body': body,
                }
            }
        try:
            result['json'] = response.json()
        except Exception:
            pass
        return result

    def get(self, endpoint):
        headers = self._get_headers()
        url = self.url.format(endpoint=endpoint)
        response = requests.get(url, headers=headers, verify=self.ssl_verify)
        return self._result_create(response, url, headers)

    def put(self, endpoint, body):
        headers = self._get_headers()
        url = self.url.format(endpoint=endpoint)
        response = requests.put(url, json=body, headers=headers, verify=self.ssl_verify)
        result = self._result_create(response, url, headers, body)
        if result['status_code'] == 201:
            result['changed'] = True
        return result

    def patch(self, endpoint, body):
        headers = self._get_headers()
        url = self.url.format(endpoint=endpoint)
        response = requests.patch(url, json=body, headers=headers, verify=self.ssl_verify)
        result = self._result_create(response, url, headers, body)
        if result['status_code'] == 204:
            result['changed'] = True
        return result

    def delete(self, endpoint):
        headers = self._get_headers()
        url = self.url.format(endpoint=endpoint)
        response = requests.delete(url, headers=headers, verify=self.ssl_verify)
        result = self._result_create(response, url, headers)
        if result['status_code'] < 300:
            result['changed'] = True
        if result['status_code'] == 400: # Does Not Exist
            result['rc'] = 0
            result['failed'] = False
            result.pop('debug', None)
        return result
