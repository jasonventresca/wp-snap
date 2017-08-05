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


def _fname(project_name, extension):
    timestamp = str(datetime.utcnow()).replace(' ', '_').replace(':', '-')
    return '/tmp/{}_{}.{}'.format(project_name, timestamp, extension)


def tarball(webroot_path, tar_fname):
    check_call(['sudo', 'tar', '-cf', tar_fname, webroot_path])
    check_call(['sudo', 'gzip', '-f', tar_fname])

    tar_gz_fname = '{}.gz'.format(tar_fname)
    check_call(['sudo', 'chown', 'ubuntu:ubuntu', tar_gz_fname])

    return tar_gz_fname


def sql_dump(config, sql_fname):
    db_config = config['mysql']
    cmd = [
            'mysqldump',
            "--user={}".format(db_config['user']),
            "--password={}".format(db_config['password']),
            '--host={}'.format(db_config['host']),
            db_config['db_name'],
    ]
    with open(sql_fname, 'w') as sql_f:
        check_call(cmd, stdout=sql_f)

    check_call(['gzip', '-f', sql_fname])

    return '{}.gz'.format(sql_fname)


def create_snapshot(config, sql_fname, tar_fname):
    sql_gz_fname = sql_dump(config, sql_fname)
    tar_gz_fname = tarball(config['webroot_path'], tar_fname)

    return [
            sql_gz_fname,
            tar_gz_fname,
    ]


def _upload(local_path, s3_bucket, s3_key_name):
    s3 = boto3.client('s3')
    s3.upload_file(local_path, s3_bucket, s3_key_name)


def upload_all(frequency, snapshot_files, config):
    for local_path in snapshot_files:
        s3_key_name = '{}/{}/{}'.format(config['project_name'], frequency, basename(local_path))
        _upload(local_path, config['s3_bucket'], s3_key_name)


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

    sql_fname = _fname(config['project_name'], 'sql')
    tar_fname = _fname(config['project_name'], 'tar')
    gz_files = (
            sql_fname + '.gz',
            tar_fname + '.gz',
    )

    try:
        snapshot_files = create_snapshot(config=config, sql_fname=sql_fname, tar_fname=tar_fname)
        upload_all(frequency, snapshot_files, config)
        rotate_old_uploads(frequency, config)
        assert set(gz_files) == set(snapshot_files)

    finally:
        # Clean up all temp files, regardless of whether the uploads succeeded.
        all_possible_files = (sql_fname, tar_fname) + gz_files
        for fname in all_possible_files:
            check_call(['sudo', 'rm', '-rf', fname])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a snapshot of a WordPress installation.')
    parser.add_argument('frequency', choices=BACKUP_FREQUENCIES,
                        help='One of {}.'.format(BACKUP_FREQUENCIES))
    parser.add_argument('config_file', type=str,
                        help='Path to JSON config file.')
    args = parser.parse_args()

    main(args.frequency, args.config_file)
