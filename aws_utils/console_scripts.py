import click
from . import assume_role

@click.command()
@click.option('-p', '--profile-name', default='default', help='AWS Profile to use')
@click.option('-a', '--assume-role-arn', required=True, help='AWS Role to assume')
@click.option('-r', '--region_name', default='eu-west-1', help='AWS Region')
@click.option('-o', '--output', default='environment', help='Output format')
@click.option('-v', '--verbose', is_flag=True, default=False, help='Output to console')
def assume_role_proxy(profile_name, assume_role_arn, region_name, output, verbose):
    result = assume_role(profile_name, assume_role_arn, region_name, output)
    if verbose:
        print(result)
