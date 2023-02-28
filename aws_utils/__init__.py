import random
from typing import Union
import string
import re
import boto3
from configparser import ConfigParser


def assume_role(
        profile_name: str, assume_role_arn: str, region_name: str, output: str
) -> Union[str, dict]:
    """

    :param profile_name: name of the AWS profile to use
    :param assume_role_arn: arn of the AWS role to assume
    :param region_name: AWS region name
    :param output: yml, yaml, environment, dictionary or bare
    :return:
    """
    credentials = boto3.Session(profile_name=profile_name).client('sts').assume_role(
        RoleArn=assume_role_arn,
        RoleSessionName=''.join(random.choice(string.ascii_lowercase) for _ in range(10))
    )['Credentials']

    yaml_re = re.compile(r'^ya?ml([0-9]*)?$')
    if 'environment' == output:
        return f'''export AWS_REGION={region_name}
export AWS_ACCESS_KEY_ID={credentials["AccessKeyId"]}
export AWS_SECRET_ACCESS_KEY={credentials["SecretAccessKey"]}
export AWS_SESSION_TOKEN={credentials["SessionToken"]}'''

    if yaml_re.match(output) is not None:
        matches = yaml_re.match(output)
        indentation = ' ' * int(matches[1]) if '' != matches[1] else ''
        return f'''{indentation}AWS_REGION: {region_name}
{indentation}AWS_ACCESS_KEY_ID: {credentials["AccessKeyId"]}
{indentation}AWS_SECRET_ACCESS_KEY: {credentials["SecretAccessKey"]}
{indentation}AWS_SESSION_TOKEN: {credentials["SessionToken"]}'''

    if 'dictionary' == output:
        return {
            'AWS_REGION': region_name,
            'AWS_ACCESS_KEY_ID': credentials['AccessKeyId'],
            'AWS_SECRET_ACCESS_KEY': credentials['SecretAccessKey'],
            'AWS_SESSION_TOKEN': credentials['SessionToken']
        }

    if 'bare' == output:
        return credentials

    raise Exception(f'No way to handle output {output}')


def load_config(file):
    config_parser = ConfigParser()
    if len(config_parser.read(file)) != 1:
        raise Exception(f'Could not read file {file}')
    return config_parser


def get_session(access_key_id, secret_access_key, region_name):
    return boto3.Session(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=region_name
    )


def create_access_key(access_key_id, secret_access_key, region_name, user_name):
    client = get_session(access_key_id, secret_access_key, region_name).client('iam')
    deleted_access_keys = []
    for access_key in [
        k for k in client.list_access_keys(UserName=user_name)['AccessKeyMetadata'] if k['Status'] == 'Inactive'
    ]:
        inactive_access_key_id = access_key['AccessKeyId']
        client.delete_access_key(
            UserName=access_key['UserName'],
            AccessKeyId=access_key['AccessKeyId']
        )
        deleted_access_keys.append(inactive_access_key_id)
    return client.create_access_key(UserName=user_name)['AccessKey'], deleted_access_keys


def deactivate_access_key(access_key_id, secret_access_key, region_name, user_name, old_access_key_id):
    get_session(access_key_id, secret_access_key, region_name).client('iam').update_access_key(
        UserName=user_name,
        AccessKeyId=old_access_key_id,
        Status='Inactive'
    )


def delete_access_key(access_key_id, secret_access_key, region_name, user_name, old_access_key_id):
    get_session(access_key_id, secret_access_key, region_name).client('iam').delete_access_key(
        UserName=user_name,
        AccessKeyId=old_access_key_id
    )
