import click
from os.path import expanduser
import time
import nl.randstadgroep.aws.iam as iam
import logging

logging.basicConfig(level=logging.INFO)


@click.command()
@click.option('-u', '--user-name', type=str, required=True, help='User name')
@click.option('-c', '--credentials-file', type=str, default=None, help='Credentials file to update')
@click.option('-p', '--profile', type=str, default='default', help='Profile to update')
@click.option('-r', '--region-name', type=str, default='eu-west-1', help='Region name')
@click.option('-s', '--sleep', type=int, default=30, help='Seconds to allow new access key to become active')
def main(credentials_file, profile, user_name, region_name, sleep):
    # Load the credentials file
    if credentials_file is None:
        credentials_file = f'{expanduser("~")}/.aws/credentials'
    credentials = iam.load_config(credentials_file)
    logging.info(f'Loaded credentials file {credentials_file}')

    # Get current access_key_id and secret_access_key from the credentials
    current_access_key_id = credentials.get(profile, 'aws_access_key_id')
    current_secret_access_key = credentials.get(profile, 'aws_secret_access_key')

    try:
        # Delete inactive access keys and create a new one
        new_access_key, deleted_access_keys = iam.create_access_key(
            current_access_key_id,
            current_secret_access_key,
            region_name,
            user_name
        )
        new_access_key_id = new_access_key['AccessKeyId']
        new_secret_access_key = new_access_key['SecretAccessKey']
        if len(deleted_access_keys) > 0:
            logging.info(f'Deleted access_key_ids {",".join(deleted_access_keys)}')
        logging.info(f'Created new access_key_id {new_access_key_id}')

        # Sleep a while as the new access key is not immediately usable
        logging.info(f'Pausing {sleep} seconds to allow the new access key to be activated')
        time.sleep(sleep)

        # Section name for the inactive profile
        inactive_profile = f'{profile}-inactive'

        try:
            # Deactivate the current access key by using the new access key
            iam.deactivate_access_key(new_access_key_id, new_secret_access_key,
                                      region_name, user_name,
                                      current_access_key_id
                                      )
            logging.info(f'Deactivated access_key_id {current_access_key_id}')

            # Store the old access_key_id and secret_access_key in an 'inactive' section
            if not credentials.has_section(inactive_profile):
                credentials.add_section(inactive_profile)
            credentials[inactive_profile]['aws_access_key_id'] = current_access_key_id
            credentials[inactive_profile]['aws_secret_access_key'] = current_secret_access_key
            logging.info(f'Created a backup for access_key_id {current_access_key_id} in profile {inactive_profile}')

            # Store the new access key in the credentials file
            credentials[profile]['aws_access_key_id'] = new_access_key_id
            credentials[profile]['aws_secret_access_key'] = new_secret_access_key
            logging.info(f'Updated profile {profile} to use access_key_id {new_access_key_id}')

        except:
            logging.info(f'Deactivating {current_access_key_id} failed. Deleting new access_key_id {new_access_key_id}')
            iam.delete_access_key(
                current_access_key_id, current_secret_access_key,
                region_name, user_name,
                new_access_key_id
            )
            if credentials.has_section(inactive_profile):
                logging.info(f'Removed {inactive_profile} section from credentials')
                credentials.remove_section(inactive_profile)

        # Save the credentials file
        with open(credentials_file, 'w') as configfile:
            credentials.write(configfile)
        logging.info(f'Saved credentials file, rotation done')

    except Exception as e:
        logging.info(f'Could not create new access_key_id: {e}')


if '__main__' == __name__:
    main()
