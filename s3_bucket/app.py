import boto3
from botocore.exceptions import ClientError


# Initialization
# access_key = 'AKIAJ6F5URPXMRHJQZ4A'
# secret_key = 'jE3Mj4I/Z84wO3uusFkg1iK1ISUVoYqH6DrBZlA7'
bucket_name = 'sam-s3-bucket-2024'  # Replace with your bucket name
subfolders = ['predawn-raw-s3', 'predawn-curated-s3', 'predawn-serve-s3']  # List of bucket names to create
access_key = 'AKIA2HHAGSCLDKHZH7YG'
secret_key = 'qwWCLnrl0te80HnV5uAh7DKlRbQURvVTgt+CV1qw'
region = 'ap-southeast-2'  # Replace with your desired region

def check_bucket_exists(bucket_name):
    s3_client = boto3.client('s3', aws_access_key_id=access_key,aws_secret_access_key=secret_key)
    try:
        response = s3_client.list_buckets()
        for bucket in response['Buckets']:
            if bucket["Name"] == bucket_name:
                return True
        return False
    except ClientError as e:
        print(f"An error occurred: {e}")
        return False

def create_bucket(bucket_name, region=None):
    try:
        s3_client = boto3.client('s3', aws_access_key_id=access_key,aws_secret_access_key=secret_key)
        if region is None:
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
    except ClientError as e:
        print(e)
        return False
    return True

def check_subfolder_exists(bucket_name, subfolder_name):
    s3_client = boto3.client('s3', aws_access_key_id=access_key,aws_secret_access_key=secret_key)
    try:
        # Ensure the subfolder name ends with a '/'
        if not subfolder_name.endswith('/'):
            subfolder_name += '/'

        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=subfolder_name)
        return 'Contents' in response
    except ClientError as e:
        print(f"An error occurred: {e}")
        return False

def create_subfolder(bucket_name, subfolder_name):
    s3_client = boto3.client('s3', aws_access_key_id=access_key,aws_secret_access_key=secret_key)
    try:
        s3_client.put_object(Bucket=bucket_name, Key=(subfolder_name + '/'))
        return True
    except ClientError as e:
        print(f"Error creating subfolder: {e}")
        return False

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

def cmd():
    # Create s3 bucket
    res = check_bucket_exists(bucket_name)
    if res:
        print(f"'{bucket_name}' s3 bucket already exists")
        pass
    else:
        create_bucket(bucket_name, region)
        print(f"Bucket '{bucket_name}' created successfully.")

    # Create subfolders
    for folder in subfolders:
        if check_subfolder_exists(bucket_name, folder):
            print(f"'{folder}' folder already exists in the '{bucket_name} bucket'")
            pass
        else:
            if create_subfolder(bucket_name, folder):
                print(f"Subfolder '{folder}' created successfully.")
            else:
                print(f"Failed to create subfolder '{folder}'")

def main():
    cmd()



if __name__ == "__main__":
    main()


