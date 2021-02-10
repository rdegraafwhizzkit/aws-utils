import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import re
from .boto import get_client


def get_wait_parameters(**kwargs):
    return {
        k: v for k, v in kwargs.items() if k in (
            'StackName',
            'NextToken',
            'WaiterConfig',
            'ChangeSetName'
        )
    }


def get_delete_stack_parameters(**kwargs):
    return {
        k: v for k, v in kwargs.items() if k in (
            'StackName',
            'RetainResources',
            'RoleARN',
            'ClientRequestToken'
        )
    }


def get_create_stack_parameters(**kwargs):
    return {
        k: v for k, v in kwargs.items() if k in (
            'StackName',
            'TemplateBody',
            'TemplateURL',
            'Parameters',
            'DisableRollback',
            'RollbackConfiguration',
            'TimeoutInMinutes',
            'NotificationARNs',
            'Capabilities',
            'ResourceTypes',
            'RoleARN',
            'OnFailure',
            'StackPolicyBody',
            'StackPolicyURL',
            'Tags',
            'ClientRequestToken',
            'EnableTerminationProtection'
        )
    }


def get_create_change_set_parameters(**kwargs):
    return {
        k: v for k, v in kwargs.items() if k in (
            'StackName',
            'TemplateBody',
            'TemplateURL',
            'UsePreviousTemplate',
            'Parameters',
            'Capabilities',
            'ResourceTypes',
            'RoleARN',
            'RollbackConfiguration',
            'NotificationARNs',
            'Tags',
            'ChangeSetName',
            'ClientToken',
            'Description',
            'ChangeSetType',
            'ResourcesToImport',
            'IncludeNestedStacks'
        )
    }


def create_stack_or_change_set(**kwargs):
    if stack_exists(kwargs.get('StackName')):
        return create_change_set(**kwargs)
    else:
        return create_stack(**kwargs)


def create_change_set(**kwargs):
    client = get_client('cloudformation')

    kwargs['ChangeSetName'] = 'change-set-{}-{}'.format(
        re.sub(r'[^a-zA-Z0-9-]', '-', kwargs.get('StackName')),
        datetime.now().strftime('%Y%m%d-%H%M%S')
    )

    response = client.create_change_set(**get_create_change_set_parameters(**kwargs))

    if kwargs.get('wait', False):
        client.get_waiter('change_set_create_complete').wait(**get_wait_parameters(**kwargs))

    return response


def create_stack(**kwargs):
    client = get_client('cloudformation')

    response = client.create_stack(**get_create_stack_parameters(**kwargs))

    if kwargs.get('wait', False):
        client.get_waiter('stack_create_complete').wait(**get_wait_parameters(**kwargs))

    return response


def delete_stack(**kwargs):
    client = get_client('cloudformation')

    response = client.delete_stack(**get_delete_stack_parameters(**kwargs))

    if kwargs.get('wait', False):
        client.get_waiter('stack_delete_complete').wait(**get_wait_parameters(**kwargs))

    return response


def stack_exists(stack_name: str) -> bool:
    try:
        boto3.client('cloudformation').describe_stacks(StackName=stack_name)
    except ClientError as error:
        return not f'Stack with id {stack_name} does not exist' == error.response.get('Error').get('Message')
    return True


def create_parameter_dict(parameters: dict) -> list:
    return [
        {
            'ParameterKey': k,
            'ParameterValue': str(v)
        } for k, v in parameters.items()
    ]


def create_tag_dict(tags: dict) -> list:
    return [
        {
            'Key': k,
            'Value': str(v)
        } for k, v in tags.items()
    ]
