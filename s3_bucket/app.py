import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from forex_python.converter import CurrencyRates
from requests_html import HTMLSession
from bs4 import BeautifulSoup as bs

import boto3
from botocore.exceptions import ClientError


# Initialization

bucket_name = 'predawnsuper/tech'  # Replace with your bucket name
region = 'ap-southeast-2'  # Replace with your desired region
create_bucket(bucket_name, region)


def create_bucket(bucket_name, region=None):
    try:
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
    except ClientError as e:
        print(e)
        return False
    return True



def send_email(subject, body):
    from_email = '156709406@qq.com'
    to_email = '156709406@qq.com'
    smtp_server = 'smtp.qq.com'
    smtp_port = 587
    smtp_username = '156709406@qq.com'
    smtp_password = 'esdrnpzdsscbcajj'

    message = MIMEMultipart()
    message['From'] = from_email
    message['To'] = to_email
    message['Subject'] = subject

    # Attach the body of the email
    message.attach(MIMEText(body, 'plain'))

    print(f'Start to send email')

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # Login to the email server
            server.starttls()
            server.login(smtp_username, smtp_password)

            # Send the email
            print(f'Start to send the message')
            server.sendmail(from_email, to_email, message.as_string())
            server.quit()
            # If successful, return 0

        # If successful, return 0
        return 0

    except Exception as e:
        # If there's an error, return the error message
        return str(e)



def main():
    cmd_email()


if __name__ == "__main__":
    main()



