from os.path import expanduser
import requests
import toml
import urlparse


def _dcos_read_configuration():
    home = expanduser("~")
    with open("{}/.dcos/dcos.toml".format(home)) as conffile:
        try:
            config = toml.loads(conffile.read())
            return config.get('core', {})
        except Exception as e:
            raise Exception("Error parsing dcos.toml file: " + str(e))


def _dcos_parse_url(url, endpoint):
    result = urlparse.urlsplit(url)
    netloc = result.netloc.split('@')[-1]
    result = result._replace(netloc=netloc)
    path = "acs/api/v1{endpoint}".format(endpoint=endpoint)
    result = result._replace(path=path)
    return urlparse.urlunsplit(result)


def _dcos_get_configuration(endpoint):
    core = _dcos_read_configuration()
    token = core.get('dcos_acs_token', '')
    if not token:
        subprocess.check_output("dcos auth login".split())
        core = _dcos_read_configuration()
        token = core.get('dcos_acs_token', 'bogus')
    url = _dcos_parse_url(core.get('dcos_url', ''), endpoint)
    ssl_verify = core.get('ssl_verify', True)

    return url, token, ssl_verify


def dcos_api(method, endpoint, body=None):
    url, token, ssl_verify = _dcos_get_configuration(endpoint)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': "token={}".format(token),
    }
    if method == 'GET':
        response = requests.get(url, headers=headers, verify=ssl_verify)
    elif method == 'PUT':
        response = requests.put(url, json=body, headers=headers, verify=ssl_verify)
    elif method == 'PATCH':
        response = requests.patch(url, json=body, headers=headers, verify=ssl_verify)
    elif method == 'DELETE':
        response = requests.delete(url, headers=headers, verify=ssl_verify)

    try:
        response_json = response.json()
    except Exception as e:
        response_json = {}
        pass
        #return {'rc': 1, 'failed': True, 'msg': "Exception: {}".format(str(e))}

    return {
        'url': url,
        'status_code': response.status_code,
        'text': response.text,
        'json': response_json,
        'request_body': body,
        'request_headers': headers,
    }
