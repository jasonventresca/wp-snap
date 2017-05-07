#! /usr/bin/env python3

from subprocess import check_call
import argparse
import json
from os.path import basename
from os import unlink
from datetime import datetime

import boto3

from expiry import ExpiryChecker


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


def _upload(local_path, s3_bucket, s3_key_name):
    s3 = boto3.client('s3')
    s3.upload_file(local_path, s3_bucket, s3_key_name)


def upload_all(frequency, snapshot_files, config):
    for local_path in snapshot_files:
        s3_key_name = '{}/{}/{}'.format(config['project_name'], frequency, basename(local_path))
        _upload(local_path, config['s3_bucket'], s3_key_name)

    # Upload all files before deleting any.
    for local_path in snapshot_files:
        unlink(local_path)


def rotate_old_uploads(frequency, config):
    bucket = boto3.resource('s3').Bucket(config['s3_bucket'])
    prefix = '{}/{}'.format(config['project_name'], frequency)
    expiry = ExpiryChecker(frequency, config['rotate'][frequency])

    for s3obj in bucket.objects.filter(Prefix=prefix):
        print("key: {}, mtime: {}".format(s3obj.key, s3obj.last_modified))
        if expiry.is_expired(s3obj.last_modified):
            print(" -> deleting object: s3://{}/{}".format(config['s3_bucket'], s3obj.key))
            s3obj.delete()


def main(frequency, config_file):
    config = json.load(open(config_file))
    snapshot_files = create_snapshot(config)

    upload_all(frequency, snapshot_files, config)

    rotate_old_uploads(frequency, config)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a snapshot of a WordPress installation.')
    parser.add_argument('frequency', choices=BACKUP_FREQUENCIES,
                        help='One of {}.'.format(BACKUP_FREQUENCIES))
    parser.add_argument('config_file', type=str,
                        help='Path to JSON config file.')
    args = parser.parse_args()

    main(args.frequency, args.config_file)
