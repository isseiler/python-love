#author isseiler
#date: Jan 09, 2017
#description: creates different buckets for new hires to help learn S3.
# uses creds from local aws CLI config files.

import boto3
import string
import random
import json
from botocore.vendored import requests

#set to True when ready to officially deploy / do final testing
enable_public_buckets = False#True
bucket_tag_name_value = 'NHT-2018-S3'

region_name_we_want_to_create_buckets_in = 'us-west-2'

def lambda_handler(event, context):

    def random_generator(size=4, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for x in range(size))


    #START create_public_bucket_with_bucket_owner_full_control    
    def create_public_bucket_with_bucket_owner_full_control():
        bucket_name = "s3-nht-require-bucket-owner-full-control-" + random_generator() #our bucket name

        print(bucket_name)
        s3 = boto3.client('s3', region_name=region_name_we_want_to_create_buckets_in) #initialize s3 client  
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region_name_we_want_to_create_buckets_in}) #create the bucket!

        s3resource = boto3.resource('s3')
        bucket_tagging = s3resource.BucketTagging(bucket_name)

        response = bucket_tagging.put(
            Tagging={
                'TagSet': [
                    {
                        'Key': 'Name',
                        'Value': bucket_tag_name_value
                    },
                ]
            }
        )
                
        # Create the bucket policy
        bucket_policy = {
            'Version': '2012-10-17',
            'Statement': [{
                'Sid': 'Require bucket owner full control in the PUT request :) ',
                'Effect': 'Allow',
                'Principal': '*',
                'Action': ['s3:PutObject'],
                'Resource': "arn:aws:s3:::%s/*" % bucket_name,
                "Condition": {
             "StringEquals": {
                 "s3:x-amz-acl": "bucket-owner-full-control"
                 } #string equals close
                } #condition close
            }] #end policy statement
        } #end bucket policy

        # Convert the policy to a JSON string
        bucket_policy = json.dumps(bucket_policy)

        # Set the new policy on the given bucket
        if enable_public_buckets == True:
            s3.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)
            
            #add a public acl to the bucket which grants reads and writes to anyone
            bucket_acl = s3resource.BucketAcl(bucket_name)
            response = bucket_acl.put(
            ACL='public-read-write'
            )    
    
    #END create_public_bucket_with_bucket_owner_full_control
    
    #START create_public_bucket_with_request_payer
    
    def create_public_bucket_with_request_payer():
        bucket_name = "s3-nht-require-bucket-owner-full-control-request-payer-" + random_generator() #our bucket name

        print(bucket_name)
        s3 = boto3.client('s3', region_name=region_name_we_want_to_create_buckets_in) #initialize s3 client  
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region_name_we_want_to_create_buckets_in}) #create the bucket!


        s3resource = boto3.resource('s3')
        bucket_tagging = s3resource.BucketTagging(bucket_name)
        bucket_request_payment = s3resource.BucketRequestPayment(bucket_name)
        response = bucket_tagging.put(
            Tagging={
                'TagSet': [
                    {
                        'Key': 'Name',
                        'Value': bucket_tag_name_value
                    },
                ]
            }
        )
        
        response = bucket_request_payment.put(
            RequestPaymentConfiguration={
                'Payer': 'Requester'
                }
        )
        
        # Create the bucket policy
        bucket_policy = {
            'Version': '2012-10-17',
            'Statement': [{
                'Sid': 'Require bucket owner full control in the PUT request :) ',
                'Effect': 'Allow',
                'Principal': '*',
                'Action': ['s3:PutObject'],
                'Resource': "arn:aws:s3:::%s/*" % bucket_name,
                "Condition": {
             "StringEquals": {
                 "s3:x-amz-acl": "bucket-owner-full-control"
                 } #string equals close
                } #condition close
            }] #end policy statement
        } #end bucket policy

        # Convert the policy to a JSON string
        bucket_policy = json.dumps(bucket_policy)

        # Set the new policy on the given bucket
        if enable_public_buckets == True:
            s3.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)    
            #add a public acl to the bucket which grants reads and writes to anyone
            bucket_acl = s3resource.BucketAcl(bucket_name)
            response = bucket_acl.put(
            ACL='public-read-write'
            )    
            
    #END create_public_bucket_with_request_payer
            
    #START create_a_bucket_that_requires_root_creds_to_delete

    def create_a_bucket_that_requires_root_creds_to_delete():
        bucket_name = "s3-nht-try-and-delete-this-bucket-" + random_generator() #our bucket name

        print(bucket_name)
        s3 = boto3.client('s3', region_name=region_name_we_want_to_create_buckets_in) #initialize s3 client  
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region_name_we_want_to_create_buckets_in}) #create the bucket!


        s3resource = boto3.resource('s3')
        bucket_tagging = s3resource.BucketTagging(bucket_name)
        bucket_request_payment = s3resource.BucketRequestPayment(bucket_name)
        response = bucket_tagging.put(
            Tagging={
                'TagSet': [
                    {
                        'Key': 'Name',
                        'Value': bucket_tag_name_value
                    },
                ]
            }
        )
        
        # Create the bucket policy
        bucket_policy = {
            'Version': '2012-10-17',
            'Statement': [{
                'Sid': 'Require bucket owner full control in the PUT request :)',
                'Effect': 'Deny',
                'Principal': '*',
                'Action': ['s3:*'],
                'Resource': "arn:aws:s3:::%s" % bucket_name,
                "Condition": {
             "StringEquals": {
                 "s3:x-amz-acl": "bucket-owner-full-control"
                 } #string equals close
                } #condition close
            }] #end policy statement
        } #end bucket policy

        # Convert the policy to a JSON string
        bucket_policy = json.dumps(bucket_policy)

        # Set the new policy on the given bucket
        if enable_public_buckets == True:
            s3.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)              
    
    #END create_a_bucket_that_requires_root_creds_to_delete

    #START create_bucket_broken_event_notifications    

    def create_bucket_broken_event_notifications():
        bucket_name = "s3-nht-broken-event-notifications-" + random_generator() #our bucket name

        print(bucket_name)
        s3 = boto3.client('s3', region_name=region_name_we_want_to_create_buckets_in) #initialize s3 client  
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region_name_we_want_to_create_buckets_in}) #create the bucket!


        s3resource = boto3.resource('s3')
        bucket_tagging = s3resource.BucketTagging(bucket_name)
        response = bucket_tagging.put(
            Tagging={
                'TagSet': [
                    {
                        'Key': 'Name',
                        'Value': bucket_tag_name_value
                    },
                ]
            }
        )
        
        #TO DO:
        #create a year= prefix in this bucket
        directory_name = "year=" #it's name of your folders
        s3.put_object(Bucket=bucket_name, Key=(directory_name+'/'))
        
        #create a lambda function for this bucket and put the lambda ARN in the event notification
            #new lambda function - brokenLambdaEventNotificationArn
            #do all the things!
        
        bucket_notification = s3resource.BucketNotification(bucket_name)
        response = bucket_notification.put(
        NotificationConfiguration={
            'LambdaFunctionConfigurations': [
                {
                    'Id': "What'sBrokenWithThisEvent",
                    'LambdaFunctionArn': #brokenLambdaEventNotificationArn,
                    'Events': ['s3:ObjectCreated:*'],
                    'Filter': {
                        'Key': {
                            'FilterRules': [
                                {
                                    'Name': 'prefix',
                                    'Value': 'year='
                                },
                            ]
                        }
                    }
                },
            ],
        }
        )
            
    #END create_bucket_broken_event_notifications    
    
    #create buckets!
    
    #create_public_bucket_with_bucket_owner_full_control()
    #create_public_bucket_with_request_payer()
    #create_a_bucket_that_requires_root_creds_to_delete()
    create_bucket_broken_event_notifications()
    
    
    #misc - allow CFN to finish up:    
    responseStatus = 'SUCCESS' #Magic  - DON'T TOUCH THIS.
    responseData = {} #Magic  - DON'T TOUCH THIS.
    send(event, context, responseStatus, responseData) #Magic  - DON'T TOUCH THIS.
   

   #CFN response function - DON'T TOUCH THIS.
def send(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False):
    responseUrl = event['ResponseURL']

    print(responseUrl)

    responseBody = {}
    responseBody['Status'] = responseStatus
    responseBody['Reason'] = 'See the details in CloudWatch Log Stream: ' + context.log_stream_name
    responseBody['PhysicalResourceId'] = physicalResourceId or context.log_stream_name
    responseBody['StackId'] = event['StackId']
    responseBody['RequestId'] = event['RequestId']
    responseBody['LogicalResourceId'] = event['LogicalResourceId']
    responseBody['NoEcho'] = noEcho
    responseBody['Data'] = responseData

    json_responseBody = json.dumps(responseBody)

    print("Response body:\n" + json_responseBody)

    headers = {
        'content-type' : '',
        'content-length' : str(len(json_responseBody))
    }

    try:
        response = requests.put(responseUrl,
                                data=json_responseBody,
                                headers=headers)
        print("Status code: " + response.reason)
    except Exception as e:
        print("send(..) failed executing requests.put(..): " + str(e))
        
        
lambda_handler(1,1)
