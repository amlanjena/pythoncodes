import requests
def login(Username, Password):
    header = {'Content-Type':'application/json'}
    payload = {"username":Username,"password":Password}
    API = "https://api.prismacloud.io"
    response = requests.request('POST', '{}/login'.format(API), json=payload, headers=header)
    json_response = response.json()
    return json_response['token']

