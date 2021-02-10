import boto3


def check_response(response: dict) -> bool:
    return 200 == response.get('ResponseMetadata').get('HTTPStatusCode')


def get_client(client: str):
    return boto3.client(client)

# def get_client_from_session(aws_access_key_id=None, aws_secret_access_key=None, aws_session_token=None, region_name=None, botocore_session=None, profile_name=None):
#     return boto3.session.Session()
