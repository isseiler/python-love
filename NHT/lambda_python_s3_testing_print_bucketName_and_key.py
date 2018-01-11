#author isseiler
#date: Jan 10, 2017
#description: When used as a Lambda Python 3 function as an S3 event lambda function, it'll print out the S3 Key name and bucket name to a CloudWatch log
# uses creds from the lambda role that is executing it

import json

print('Loading function')

def lambda_handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    s3_key_name = event['Records'][0]['s3']['object']['key']
    print("Success! The lambda event function fired successfully!")
    print("An S3 Key named " + s3_key_name + " was uploaded to the bucket named " + bucket_name + "!")
    return "SUCCESS"
    #raise Exception('Something went wrong')
