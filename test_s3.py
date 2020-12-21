"""
Returns names of accessible s3 buckets"
"""

import boto3
import config

session = boto3.Session(
    aws_access_key_id=config.conf.S3_SETTINGS.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.conf.S3_SETTINGS.AWS_SECRET_ACCESS_KEY,
)
s3 = session.resource('s3')

for bucket in s3.buckets.all():
    print(bucket.name)
