#author isseiler
#date: Jan 09, 2017
#description: Deletes S3 buckets and Lambda functions that have a tag of NHT-2018-S3 on them.
# uses creds from local aws CLI config files.

import boto3
from functools import reduce  # forward compatibility for Python 3
import operator

#boto3.set_stream_logger('botocore') #debug logging at the ready!

def lambda_handler(event, context):
    
    boto_s3_client = boto3.client('s3', region_name='us-east-1')
    bucket_name_array = []  
    bucket_list_response = boto_s3_client.list_buckets() # get a list of buckets
    found_a_nht_bucket = 0
    found_a_nht_lambda_function = 0
    resource_tag_to_target_for_deletion = 'NHT-2018-S3'
    
    
    ######################################
    # Remove all NHT Lambda functions    #
    ######################################
    boto_lambda_client = boto3.client('lambda')
    lambda_list_functions_response = boto_lambda_client.list_functions()

    list_of_lambda_functions = []
    list_of_nht_lambda_function_arns = []

    for i in lambda_list_functions_response['Functions']:
        lambda_function_arns = i['FunctionArn']    
        list_of_lambda_functions.append(i['FunctionArn'])
        
    for arn in list_of_lambda_functions:
        try:
            resp = boto_lambda_client.list_tags(Resource=arn)
            try:
                if resp['Tags'] and resp['Tags']['Name'] == resource_tag_to_target_for_deletion:
                    #print(arn)
                    list_of_nht_lambda_function_arns.append(arn)
                    found_a_nht_lambda_function += 1
            except KeyError as e:
                print(e)
                
        except KeyError as e:
            print(e)

    for arn in list_of_nht_lambda_function_arns:
        print("Deleting Lambda function: " + arn + " !")
        response = boto_lambda_client.delete_function(FunctionName=arn)    

    ######################################
    # Remove all S3 NHT buckets          #
    ######################################
        
    for bucket in bucket_list_response["Buckets"]:
        #print(bucket['Name'])
        bucket_name_array.append(bucket['Name'])
    #print(bucket_name_array)   

    for bucket_name in bucket_name_array:
        try:
            tag_response = boto_s3_client.get_bucket_tagging(
        Bucket=bucket_name)         
            
            #Delete buckets with the tag name below!
            if resource_tag_to_target_for_deletion in tag_response['TagSet'][0]['Value']: 
                found_a_nht_bucket += 1
                print("deleting bucket named: " + bucket_name + "!")
                s3resource = boto3.resource('s3')
                bucket_resource = s3resource.Bucket(bucket_name)
                bucket_resource.objects.all().delete() #attempt to delete all objects that exist in the bucket
                bucket_resource.delete() #delete the bucket since it should now be empty
            
        except Exception:
            pass

    if found_a_nht_bucket >= 1:
        print("we found and deleted " + str(found_a_nht_bucket) + " bucket(s)!")
        if found_a_nht_lambda_function >= 1:
            print("we found and deleted " + str(found_a_nht_lambda_function) + " lambda function(s)!")
            print("Script exiting! Have a nice day!")
        else:
            print("Script exiting! Have a nice day!")
            
    if found_a_nht_bucket == 0: 
        print("No buckets or Lambda functions found that have NHT tags on them")
        print("Script exiting! Have a nice day!")
        

if __name__ == '__main__':
    lambda_handler('event', 'handler')
