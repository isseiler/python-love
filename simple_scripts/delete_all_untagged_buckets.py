#author isseiler
#date: Jan 09, 2017
#description: deletes all S3 buckets on an account that are untagged.
# uses creds from local aws CLI config files.

import boto3
from functools import reduce  # forward compatibility for Python 3
import operator 
from botocore.exceptions import ClientError

#boto3.set_stream_logger('botocore') #debug logging at the ready!, just uncomment beginning of line

s3resource = boto3.resource('s3')    
client = boto3.client('s3', region_name='us-east-2') #change region to something else if seeing ghost buckets, e.g. S3 says bucket is deleted but it still shows up in GET.SERVICE API calls
bucket_name_array = []  
buckets_without_tags = []
bucket_list_response = client.list_buckets() # get a list of buckets

for bucket in bucket_list_response["Buckets"]:
    #print(bucket['Name'])
    bucket_name_array.append(bucket['Name']) #send every bucket name received from GET.SERVICE to an array


for bucket in bucket_name_array:
  try:
    resp = client.get_bucket_tagging(Bucket=bucket)
  except ClientError as e:
      buckets_without_tags.append(bucket) #for each bucket that errors out due to tags not existing, add it to an array


for i in buckets_without_tags:
    print("Deleting bucket named: " + i)
    bucket_resource = s3resource.Bucket(i)
    bucket_resource.objects.all().delete() #attempt to delete all objects that exist n the bucket
    bucket_resource.delete() #delete the bucket since it should now be empty
