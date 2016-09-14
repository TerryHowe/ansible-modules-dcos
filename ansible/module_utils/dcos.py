import requests

def dcos_api(method, endpoint, body=None, params=None):
    url = "{url}acs/api/v1{endpoint}".format(
                            url=params['dcos_credentials']['url'],
                            endpoint=endpoint)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': "token={}".format(params['dcos_credentials']['token']),
    }
    verify = params.get('ssl_verify', True)
    if method == 'GET':
        response = requests.get(url, headers=headers, verify=verify)
    elif method == 'PUT':
        response = requests.put(url, json=body, headers=headers, verify=verify)
    elif method == 'PATCH':
        response = requests.patch(url, json=body, headers=headers, verify=verify)
    elif method == 'DELETE':
        response = requests.delete(url, headers=headers, verify=verify)

    try:
        response_json = response.json()
    except:
        response_json = {}

    return {
        'url': url,
        'status_code': response.status_code,
        'text': response.text,
        'json': response_json,
        'request_body': body,
        'requiest_headers': headers,
    }
