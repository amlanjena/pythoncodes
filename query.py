import requests
import json

def queryRQL(REQ_HEADER,url,RQLquery):
    response = requests.request("POST", url, data=RQLquery, headers=REQ_HEADER)
    json_string = json.dumps(response.json())
    json_data = json.loads(json_string)
    json_obj = json.dumps(json_data, indent = 2)
    File = open("C:/Dev/IP_ADDR_Json_combined.txt", "a+")
    File.write(json_obj)
    print(json_obj)
    return json_data