import json

def lambda_handler(event, context):
 import requests
 import csv
 import sys
 import os
 import AwsIP
 import AzureIP
 import GcpIP
 import query
 import login
 import pymsteams
 import boto3
 
 url = "https://api3.prismacloud.io/search/config"
 UN = os.environ["username"]
 Pass = os.environ["password"]
 JWT_TOKEN = login.login(UN, Pass)
 REQ_HEADER = {'Content-Type':'application/json','x-redlock-auth':JWT_TOKEN}
 

 Query_IP_Addr_AWS = "{\"timeRange\":{\"value\":{\"unit\":\"hour\",\"amount\":24},\"type\":\"relative\"},\"withResourceJson\":true,\"query\":\"config from cloud.resource where cloud.type = 'aws' AND api.name = 'aws-ec2-describe-network-interfaces' and  resource.status = Active and json.rule = association.publicIp exists and attachment.status contains attached and status contains in-use \"}"
 Query_IP_Addr_Azure = "{\"timeRange\":{\"value\":{\"unit\":\"hour\",\"amount\":24},\"type\":\"relative\"},\"withResourceJson\":true,\"query\":\"config from cloud.resource where cloud.type = 'azure' AND api.name = 'azure-network-public-ip-address' AND resource.status = Active and json.rule = properties.ipAddress exists and properties.ipAddress is not empty addcolumn properties.ipAddress\"}"
 Query_IP_Addr_GCP= "{\"timeRange\":{\"value\":{\"unit\":\"hour\",\"amount\":24},\"type\":\"relative\"},\"withResourceJson\":true,\"query\":\"config from cloud.resource where cloud.type = 'gcp' AND api.name = 'gcloud-compute-interfaces-list' AND resource.status = Active AND json.rule = accessConfigs[*].natIP none empty and accessConfigs[*].natIP exists\"}"

 field_names = ['ip_address','account_name','account_id','region_name','eni_id']
 


 
    
 with open('/tmp/PublicIPs.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, quoting=csv.QUOTE_ALL,
                                delimiter=',', dialect='excel', fieldnames=field_names)
        writer.writeheader()
        json_output = query.queryRQL(REQ_HEADER,url,Query_IP_Addr_AWS)
        AwsIP.writeToCsv(writer,json_output)

        json_output = query.queryRQL(REQ_HEADER,url,Query_IP_Addr_Azure)
        AzureIP.writeToCsv1(writer,json_output)
        
        json_output = query.queryRQL(REQ_HEADER,url,Query_IP_Addr_GCP)
        GcpIP.writeToCsv2(writer,json_output)
        
        File_Name = "/tmp/PublicIPs.csv"
            
 s3 = boto3.client('s3')
 #with open(File_Name, "rb") as file:
 s3.upload_file(File_Name,"combinedipaddresslambdatest","PublicIps.csv",ExtraArgs={'ACL': 'public-read'})

 csvfile.close()
    
    

 # if __name__ == '__main__':
 #    main()
    
 #    ## Elimination of Duplicate Rows ##
 #    rows = csv.reader(open("C:/Dev/Prisma_Search_IpAddress_AWS_Azure_GCP.csv", "r"))
 #    newrows = []
 #    for row in rows:
 #        if row not in newrows:
 #            newrows.append(row)
 #    writer = csv.writer(open("C:/Dev/Prisma_Search_IpAddress_AWS_Azure_GCP.csv","w",newline=''))
 #    writer.writerows(newrows)
    
 myTeams = pymsteams.connectorcard("https://refinitiv.webhook.office.com/webhookb2/f01ca3b6-32fd-4a85-9925-62fac321139f@71ad2f62-61e2-44fc-9e85-86c2827f6de9/IncomingWebhook/a13763f9930b4411b485efacdaa132a3/48002594-4a94-4545-8415-9d1ff742c9e4")
 myTeams.title("Public IP Report for AWS, Azure and GCP")
 myTeams.text("Testing")
 myTeams.text("Report Generated from Dev Tenant")
 #myTeams.text("Please link on the below link to download the report")
 myTeams.addLinkButton("Click here to download the report", "https://combinedipaddresslambdatest.s3-ap-south-1.amazonaws.com/PublicIPs.csv")
 myTeams.send()  
 
 return {
         #print(json_info)
        'statusCode': 200,
        #'body':
    }
