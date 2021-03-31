import csv
import sys
import login
import query

url = "https://api.prismacloud.io/search/config"

Query_IP_Addr_AWS = "{\"timeRange\":{\"value\":{\"unit\":\"hour\",\"amount\":24},\"type\":\"relative\"},\"withResourceJson\":true,\"query\":\"config from cloud.resource where cloud.type = 'aws' AND api.name = 'aws-ec2-describe-network-interfaces' and  resource.status = Active and json.rule = association.publicIp exists and attachment.status contains attached and status contains in-use \"}"
Query_IP_Addr_Azure = "{\"timeRange\":{\"value\":{\"unit\":\"hour\",\"amount\":24},\"type\":\"relative\"},\"withResourceJson\":true,\"query\":\"config from cloud.resource where cloud.type = 'azure' AND api.name = 'azure-network-public-ip-address' AND resource.status = Active and json.rule = properties.ipAddress exists and properties.ipAddress is not empty addcolumn properties.ipAddress\"}"
Query_IP_Addr_GCP= "{\"timeRange\":{\"value\":{\"unit\":\"hour\",\"amount\":24},\"type\":\"relative\"},\"withResourceJson\":true,\"query\":\"config from cloud.resource where cloud.type = 'gcp' AND api.name = 'gcloud-compute-interfaces-list' AND resource.status = Active AND json.rule = accessConfigs[*].natIP none empty and accessConfigs[*].natIP exists\"}"

field_names = ['ip_address','account_name','account_id','region_name','eni_id']


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

def writeToCsv1(writer,ip_addr):
    for json_dict in ip_addr['data']['items']:
        public_ip_tags_azure = json_dict['data']['properties']['ipAddress']
        acct_name = json_dict['accountName']
        acct_id_tags = json_dict['accountId']
        region = json_dict['regionName']
        resource_id = json_dict['id'] 
        #att_time = json_dict['data']['attachment']['attachTime']
        row = dict(ip_address = public_ip_tags_azure,account_name = acct_name,account_id = acct_id_tags,region_name = region, eni_id = resource_id)
        writer.writerow(row)
            
def writeToCsv2(writer,ip_addr):
    for json_dict in ip_addr['data']['items']:
        public_ip_tags_gcp = json_dict['data']['accessConfigs'][0]['natIP']
        acct_name = json_dict['accountName']
        acct_id_tags = json_dict['accountId']
        region = json_dict['regionName']
        resource_id = json_dict['id'] 
        #att_time = json_dict['data']['attachment']['attachTime']
        row = dict(ip_address = public_ip_tags_gcp,account_name = acct_name,account_id = acct_id_tags,region_name = region, eni_id = resource_id)
        writer.writerow(row)            
            
def main():
    UN = sys.argv[1]
    Pass = sys.argv[2]
    JWT_TOKEN = login.login(UN, Pass)
    REQ_HEADER = {'Content-Type':'application/json','x-redlock-auth':JWT_TOKEN}
    
    with open('C:/Dev/Prisma_Search_IpAddress_AWS_Azure_GCP.csv', 'w+', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, quoting=csv.QUOTE_ALL,
                                delimiter=',', dialect='excel', fieldnames=field_names)
        writer.writeheader()
        json_output = query.queryRQL(REQ_HEADER,url,Query_IP_Addr_AWS)
        writeToCsv(writer,json_output)

        json_output = query.queryRQL(REQ_HEADER,url,Query_IP_Addr_Azure)
        writeToCsv1(writer,json_output)
        
        json_output = query.queryRQL(REQ_HEADER,url,Query_IP_Addr_GCP)
        writeToCsv2(writer,json_output)

    csvfile.close()
    
    

if __name__ == '__main__':
    main()
    
    ## Elimination of Duplicate Rows ##
    rows = csv.reader(open("C:/Dev/Prisma_Search_IpAddress_AWS_Azure_GCP.csv", "r"))
    newrows = []
    for row in rows:
        if row not in newrows:
            newrows.append(row)
    writer = csv.writer(open("C:/Dev/Prisma_Search_IpAddress_AWS_Azure_GCP.csv","w",newline=''))
    writer.writerows(newrows)