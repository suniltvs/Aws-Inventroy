#!/usr/bin/env python

# This Script is to create Inventory file from AWS using the credentails specified it in credentials file
# created By : suniltvs@gmail.com
# yes offcourse with the help of google ;)

import boto3
import sys
from botocore.exceptions import ClientError
Instances = open('instance.txt','r')
sys.stdout = open('/var/www/html/index.html', 'w')
client = boto3.client('ec2')
Reg = {'US-East-Virginia':'us-east-1a,us-east-1b,us-east-1c,us-east-1d,us-east-1e,us-east-1f','US-West-Oregon':'us-west-2a,us-west-2b,us-west-2c','US-West-N.California':'us-west-1a,us-west-1b','EU-Ireland':'eu-west-1a,eu-west-1b,eu-west-1c,eu-west-2a,eu-west-2b,eu-west-2c','EU-Frankfurt':'eu-central-1a,eu-central-1b,eu-central-2a,eu-central-2b','AP-Singapore':'ap-southeast-1a,ap-southeast-1b','Aus-Sydney':'ap-southeast-2a,ap-southeast-2b,ap-southeast-2c','Japan-Tokyo':'ap-northeast-1a,ap-northeast-1c','Sao-Paulo': 'sa-east-1a,sa-east-1b,sa-east-1c','India-Mumbai':'ap-south-1a,ap-south-1b','Canada-Central':'ca-central-1a,ca-central-1b,ca-central-1c,ca-central-2a,ca-central-2b,ca-central-2c'}
regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
account = ['Production','Dev-Account','Shared-Account','Website-Account']
for accounts in account:
    boto3.setup_default_session(profile_name=(accounts))
    for region in regions:
        client = boto3.client('ec2', region_name=(region))
        paginator = client.get_paginator('describe_instances')
        response_iterator = paginator.paginate()
        for page in response_iterator:
            for obj in page['Reservations']:
                for instance in obj['Instances']:
                    InstanceName = None
                    Platform = "linux"
                    for tag in instance["Tags"]:
                        if tag["Key"] == 'Name': InstanceName = tag["Value"]
                    PrivateIP = None
                    PublicIPADDDR = None
                    ec2 = boto3.resource('ec2', region_name=region)
                    InstanceDetails = ec2.Instance(instance['InstanceId'])
                    Volumes = InstanceDetails.volumes.all()
                    ec2vol = list()
                    for Volume in Volumes:
                        Vol = ec2.Volume(id=Volume.id)
                        ec2vol.append(' Device Name: ' +str(Vol.attachments[0][u'Device']))
                        ec2vol.append(' Vol Size: '+str(Vol.size)+'GB')
                    if len(instance['NetworkInterfaces'])  <= 1:
                        for inet in instance['NetworkInterfaces']:
                            if 'Association' in inet and 'PublicIp' in inet['Association']: PublicIPADDDR = inet['Association']['PublicIp']
                            Ninterface = len (inet['PrivateIpAddresses'])
                            ips=[]
                            for inter in (range(0,(Ninterface))):
                                ips.append(inet['PrivateIpAddresses'][(inter)]['PrivateIpAddress'])
                    else:
                        ips = []
                        for inet in instance['NetworkInterfaces']:
                            if 'Association' in inet and 'PublicIp' in inet['Association']: PublicIPADDDR = inet['Association']['PublicIp']
                            Ninterface = len(inet['PrivateIpAddresses'])
                            for inter in (range(0, (Ninterface))):
                                ips.append (inet['PrivateIpAddresses'][(inter)]['PrivateIpAddress'])
                    if 'Platform' in instance: Platform = instance['Platform']
                    if 'PrivateIpAddress' in instance: PrivateIP = instance['PrivateIpAddress']
                    #HW = data['compute']['models'][region][instance["InstanceType"]]
                    for inst in (Instances):
                        inst = (inst.strip().split(','))
                        if (instance["InstanceType"]) in inst:
                            CPU = (inst[1])
                            MEM = ((inst[2])+str('GB'))
                    print '<l1>AWS-Account : ', (accounts),'</l1><br>'
                    for key,value in Reg.items():
                        reg_name = (instance['Placement']['AvailabilityZone'])
                        Awsr = "None"
                        if (reg_name).strip() in value:
                            Awsr = (key)
                            print '<l1>AWS-Region : ', (Awsr),'</l1><br>'
                    Customer = 'No Tag'
                    if (instance["Tags"]) is not None:
                        data = (instance["Tags"])
                        ldata = len(data)
                        for i in range(0,ldata):
                           if (data[i]['Key']) =='Customer' or (data[i]['Key']) =='customer':
                                Customer = (data[i]['Value'])
                                print '<l1>Customer : ',(Customer),'</l1><br>'
                    print '<l1>Availability Zone : ', (instance['Placement']['AvailabilityZone']),'</l1><br>'
                    print '<l1>Instance Name : ', (InstanceName),'</l1><br>'
                    print '<l1>Instance Id : ', (instance["InstanceId"]),'</l1><br>'
                    print '<l1>Instance Type : ' , (instance["InstanceType"]),'</l1><br>'
                    print '<l1>Platform : ', (Platform),'</l1><br>'
                    print '<l1>Public IP : ', (PublicIPADDDR),'</l1><br>'
                    print '<l1>Private IP : ', ','.join([str(elem) for elem in ips]),'</l1><br>'
                    print '<l1>State : ', (instance['State']['Name']),'</l1><br>'
                    print '<l1>Volumes : ', ','.join([str(elems) for elems in ec2vol]),'</l1><br>'
                    print '<l1>No of CPU : ', (CPU),'</l1><br>'
                    print '<l1>Memory in GB : ' , (MEM),'</l1><br>'
                    print '<l1>-----------------------------------------------------------------</l1><br>'
