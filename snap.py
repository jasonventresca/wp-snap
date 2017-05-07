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


def _fname_timestamp():
    return str(datetime.utcnow()).replace(' ', '_')


def tarball(webroot_path, project_name):
    timestamp = _fname_timestamp()
    tar_fname = '/tmp/{}_{}.tar'.format(project_name, timestamp)
    tar_gz_fname = '{}.gz'.format(tar_fname)

    check_call(['tar', '-cf', tar_fname, webroot_path])
    check_call(['gzip', '-f', tar_fname])

    return tar_gz_fname


def sql_dump(config):
    db_config = config['mysql']
    cmd = [
            'mysqldump',
            "--user={}".format(db_config['user']),
            "--password={}".format(db_config['password']),
            '--host={}'.format(db_config['host']),
            db_config['db_name'],
    ]
    timestamp = _fname_timestamp()
    sql_fname = '/tmp/{}_{}.sql'.format(config['project_name'], timestamp)
    with open(sql_fname, 'w') as sql_f:
        check_call(cmd, stdout=sql_f)

    check_call(['gzip', '-f', sql_fname])

    return '{}.gz'.format(sql_fname)


def create_snapshot(config):
    sqldump_fname = sql_dump(config)
    tarball_fname = tarball(config['webroot_path'], config['project_name'])

    return [
            sqldump_fname,
            tarball_fname,
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
