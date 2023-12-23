from datetime import datetime
import boto3

client = boto3.client('bedrock')
paginator = client.get_paginator('list_provisioned_model_throughputs')
print(paginator.paginate(
    ModelName='string',
    MaxResults=123,
    NextToken='string'
))