#! /usr/bin/env python3

from subprocess import check_call
import argparse
import json
from os.path import basename
from datetime import datetime

import boto3


BACKUP_FREQUENCIES = (
        'daily',
        'weekly',
        'monthly',
)


def tarball(webroot_path, project_name):
    timestamp = str(datetime.utcnow()).replace(' ', '_')
    tar_file = '/tmp/{}_{}.tar'.format(project_name, timestamp)
    tar_gz_file = '{}.gz'.format(tar_file)

    check_call(['tar', '-cf', tar_file, webroot_path])
    check_call(['gzip', '-f', tar_file])

    return tar_gz_file


def create_snapshot(config):
    tarball_file = tarball(config['webroot_path'], config['project_name'])

    return [
            tarball_file,
            # TODO - sql dump filename goes here
    ]


def upload(local_path, s3_bucket, s3_key_name):
    s3 = boto3.client('s3')
    s3.upload_file(local_path, s3_bucket, s3_key_name)


def main(frequency, config_file):
    config = json.load(open(config_file))
    snapshot_files = create_snapshot(config)

    for local_path in snapshot_files:
        s3_key_name = '{}/{}/{}'.format(config['project_name'], frequency, basename(local_path))
        upload(local_path, config['s3_bucket'], s3_key_name)

    # TODO - rm files from /tmp (.tar.gz + .sql)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a snapshot of a WordPress installation.')
    parser.add_argument('frequency', choices=BACKUP_FREQUENCIES,
                        help='One of {}.'.format(BACKUP_FREQUENCIES))
    parser.add_argument('config_file', type=str,
                        help='Path to JSON config file.')
    args = parser.parse_args()

    main(args.frequency, args.config_file)
