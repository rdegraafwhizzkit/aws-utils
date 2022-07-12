import boto3
import random
import string
import re


def assume_role(profile_name, assume_role_arn, region_name, output):
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
    elif yaml_re.match(output) is not None:
        matches = yaml_re.match(output)
        indentation = ' ' * int(matches[1]) if '' != matches[1] else ''
        return f'''{indentation}AWS_REGION: {region_name}
{indentation}AWS_ACCESS_KEY_ID: {credentials["AccessKeyId"]}
{indentation}AWS_SECRET_ACCESS_KEY: {credentials["SecretAccessKey"]}
{indentation}AWS_SESSION_TOKEN: {credentials["SessionToken"]}'''
    elif 'dictionary' == output:
        return {
            'AWS_REGION': region_name,
            'AWS_ACCESS_KEY_ID': credentials['AccessKeyId'],
            'AWS_SECRET_ACCESS_KEY': credentials['SecretAccessKey'],
            'AWS_SESSION_TOKEN': credentials['SessionToken']
        }
    elif 'bare' == output:
        return credentials