import json
import boto3

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    sns = boto3.client('sns')
    
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        if not key.endswith(".csv"):
            continue  # skip irrelevant files

        obj = s3.get_object(Bucket=bucket, Key=key)
        rows = obj['Body'].read().decode('utf-8').splitlines()
        
        # Ignore header
        if len(rows) <= 1:
            print("No alerts found.")
            return

        message = f"⚠️ High Failed Payments Detected\n\n{len(rows)-1} customer(s) exceeded threshold.\n\nDetails:\n" + "\n".join(rows[1:])
        
        sns.publish(
            TopicArn='arn:aws:sns:us-east-1:YOUR_ACCT_ID:LoanAlerts',
            Subject='High Failed Payments Alert',
            Message=message
        )
