#!/usr/bin/env python

import argparse
import boto3
import configparser
import logging
import os
import sys


logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

logging.getLogger("botocore").setLevel(logging.WARNING)  # Only show request alerts if they are warnings / critcal


def main(username, profile, credentials_file):
    """
    Rotate AWS Access Keys
    """
    if not os.path.exists(credentials_file):
        logger.info("{} file does not exist".format(credentials_file))
        return 1

    config = configparser.ConfigParser()

    try:
        with open(credentials_file, 'r') as credentials_fh:
            config.read_file(credentials_fh)
    except IOError as err:
        logger.info("Unable to open {}: {}".format(credentials_file, err))
        return 1

    client = boto3.client(
        'iam',
        aws_access_key_id=config[profile]['aws_access_key_id'],
        aws_secret_access_key=config[profile]['aws_secret_access_key']
    )

    logger.info("Creating new credentials")
    resp = client.create_access_key(UserName=username)

    new_access_key_id = resp['AccessKey']['AccessKeyId']
    new_secret_access_key = resp['AccessKey']['SecretAccessKey']

    logger.info("Deleting old credentials")
    resp = client.delete_access_key(
        UserName=username,
        AccessKeyId=config[profile]['aws_access_key_id'],
    )

    config[profile]['aws_access_key_id'] = new_access_key_id
    config[profile]['aws_secret_access_key'] = new_secret_access_key

    try:
        logger.info("Writing new credentials")
        with open(credentials_file, 'w') as newconfig_fh:
            config.write(newconfig_fh)
    except IOError as err:
        logger.info("Unable to write to {}: {}\n".format(credentials_file, err))
        logger.info("AccessKeyID: {}".format(new_access_key_id))
        logger.info("SecretAccessKey: {}".format(new_secret_access_key))
        return 1

    return 0


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Rotate AWS Credentials")

    parser.add_argument(
        '-p',
        '--profile',
        dest='profile',
        help="AWS profile",
        required=True
    )
    parser.add_argument(
        '-c',
        '--credentials-file',
        dest="credentials_file",
        help="AWS credentials file",
        default=os.path.join(os.environ.get('HOME'), '.aws', 'credentials')
    )
    parser.add_argument(
        '-u',
        '--username',
        dest='username',
        help="AWS username",
        required=True
    )

    args = parser.parse_args()

    sys.exit(main(args.username, args.profile, args.credentials_file))
