import boto3


def check_response(response: dict) -> bool:
    return 200 == response.get('ResponseMetadata').get('HTTPStatusCode')


def get_client(client: str):
    return boto3.client(client)
