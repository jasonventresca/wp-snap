#! /usr/bin/env python3

from subprocess import check_call
import argparse
import json


BACKUP_FREQUENCIES = (
        'daily',
        'weekly',
        'monthly',
)


def tarball(direc_path):
    output_file = '/tmp/gato_tar_20170507'
    check_call(['tar', '-cf', '{output_file}.tar', '{input_dir}'])
    check_call(['gzip', '-f', '{output_file}.tar'])

    return '{}.tar.gz'.format(output_file)


def create_snapshot(webroot_path):
    tarball_file = tarball(webroot_path)

    return {
            'sql_dump': 'dummy', # TODO
            'webroot_tarball': tarball_file,
    }


def main(frequency, config_file):
    config = json.load(open(config_file))
    create_snapshot(config['webroot_path'])

    # TODO - rm files from /tmp (.tar.gz + .sql)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a snapshot of a WordPress installation.')
    parser.add_argument('frequency', choices=BACKUP_FREQUENCIES, required=True,
                        help='One of {}.'.format(BACKUP_FREQUENCIES))
    parser.add_argument('config_file', type=str, required=True,
                        help='Path to JSON config file.')
    args = parser.parse_args()

    main(args.frequency, args.config_file)
