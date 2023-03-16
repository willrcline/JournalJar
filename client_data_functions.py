import pandas as pd
import boto3
import config
import io

def get_client_data():
    s3_client = boto3.client('s3',
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        )

    # s3 = session.resource('s3')
    obj = s3_client.get_object(
    Bucket = config.aws_bucket,
    Key = config.aws_key
    )
    # Read data from the S3 object.
    client_data = pd.read_csv(io.BytesIO(obj['Body'].read()))
    
    return client_data

def put_client_data(client_data):
    s3_client = boto3.client('s3',
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        )

    csv_buf = io.StringIO()
    client_data.to_csv(csv_buf, header=True, index=False)
    csv_buf.seek(0)
    s3_client.put_object(Bucket = config.aws_bucket,Key = config.aws_key, Body=csv_buf.getvalue())