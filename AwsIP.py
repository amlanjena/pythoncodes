import csv
import json

def writeToCsv(writer,ip_addr):
    for json_dict in ip_addr['data']['items']:
        public_ip_tags = json_dict['data']['association']['publicIp']
        acct_name = json_dict['accountName']
        acct_id_tags = json_dict['accountId']
        region = json_dict['regionName']
        resource_id = json_dict['id'] 
        #att_time = json_dict['data']['attachment']['attachTime']
        row = dict(ip_address = public_ip_tags,account_name = acct_name,account_id = acct_id_tags,region_name = region, eni_id = resource_id)
        writer.writerow(row)