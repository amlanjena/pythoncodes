import requests
import json
import csv
import re



def login():
     header = {'Content-Type':'application/json'}
     payload = {"username":"fe8db7b2-d095-4f65-8880-f5a867d02efc","password":"2BDjEla1yh0H3D4xQkvx0oRNTxc="}
     API = "https://api3.prismacloud.io"
     response = requests.request('POST', '{}/login'.format(API), json=payload, headers=header)
     json_response = response.json()
     return json_response['token']

JWT_TOKEN = login()
#print(JWT_TOKEN)
REQ_HEADER = {'Content-Type':'application/json','x-redlock-auth':JWT_TOKEN}

url = "https://api.prismacloud.io/search/config"

Query_IP_Addr = "{\"timeRange\":{\"value\":{\"unit\":\"hour\",\"amount\":24},\"type\":\"relative\"},\"withResourceJson\":true,\"query\":\"config from cloud.resource where cloud.type = 'aws' AND api.name = 'aws-ec2-describe-network-interfaces' and  resource.status = Active and json.rule = association.publicIp exists and attachment.status contains attached and status contains in-use \"}"

field_names = ['ip_address','account_name','account_id','region_name','eni_id']

def queryRQL(REQ_HEADER,url,RQLquery):
    response = requests.request("POST", url, data=RQLquery, headers=REQ_HEADER)
    json_string = json.dumps(response.json())
    json_data = json.loads(json_string)
    # json_obj = json.dumps(json_data, indent = 2)
    # File = open("C:/Dev/IP_ADDR_Json.txt", "a+")
    # File.write(json_obj)
    # print(json_obj)
    return json_data

def extractJsonData(JSon_Output):
    ip_addr = []
    for json_dict in JSon_Output['data']['items']:
        # for public_ip_tags in json_dict['data']['association']:
            public_ip_tags = json_dict['data']['association']['publicIp']
            print(public_ip_tags)
            ip_addr.append(public_ip_tags)
           # print(ip_addr)
    return ip_addr

def writeToCsv(writer,ip_addr):
    for json_dict in ip_addr['data']['items']:
        public_ip_tags = (json_dict['data']['association']['publicIp'])
        acct_name = json_dict['accountName']
        acct_id_tags = json_dict['accountId']
        region = json_dict['regionName']
        resource_id = json_dict['id'] 
        #att_time = json_dict['data']['attachment']['attachTime']
        row = dict(ip_address = public_ip_tags,account_name = acct_name,account_id = acct_id_tags,region_name = region, eni_id = resource_id)
                       
        writer.writerow(row)
                    
            
JSon_Output = queryRQL(REQ_HEADER,url,Query_IP_Addr)
ip_addr = extractJsonData(JSon_Output)

def main(): 
    with open('C:/Dev/Prisma_Search_IpAddress.csv', 'w+', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, quoting=csv.QUOTE_ALL,
                                delimiter=',', dialect='excel', fieldnames=field_names)
        writer.writeheader()
        json_output = queryRQL(REQ_HEADER,url,Query_IP_Addr)
        writeToCsv(writer,json_output)         

    csvfile.close()

if __name__ == '__main__':
    main()
    ## Elimination of Duplicate Rows ##
    rows = csv.reader(open("C:/Dev/Prisma_Search_IpAddress.csv", "r"))
    newrows = []
    for row in rows:
        if row not in newrows:
            newrows.append(row)
    writer = csv.writer(open("C:/Dev/Prisma_Search_IpAddress.csv","w",newline=''))
    writer.writerows(newrows)