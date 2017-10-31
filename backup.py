# -*- coding: utf-8 -*-
"""
Couchdb Dumper
"""
import logging
import argparse
import smart_open
import os
from couchdb.client import Database
from datetime import datetime
from yaml import load as yaml_load
import json

from gzip import GzipFile
from boto.s3.connection import S3Connection, OrdinaryCallingFormat

logger = logging.getLogger('backup')


def backup(config):
    """
    Backup to smart_open file
    """
    now = datetime.now()
    database = Database(config['couchdb'])
    if config['storage'] in ('swift3', 's3',):
        logger.info('Init connection to {}'.format(config['storage']))
        if config['storage'] == 'swift3':
            connection = S3Connection(
                config['s3']['access_key'],
                config['s3']['secret_key'],
                host=config['s3']['host'],
                calling_format=OrdinaryCallingFormat()
            )
        else:
            connection = S3Connection(config['s3']['access_key'], config['s3']['secret_key'])
        if connection.lookup(config['s3']['bucket']):
            logger.info('Getting bucket {}'.format(config['s3']['bucket']))
            bucket = connection.get_bucket(config['s3']['bucket'])
        else:
            logger.info('Creating bucket {}'.format(config['s3']['bucket']))
            bucket = connection.create_bucket(config['s3']['bucket'])
        key_name = "{0}-{1:%Y-%m-%dT%H-%M-%S%z}.back".format(config['s3']['key_prefix'], now)
        backup_obj = bucket.get_key(key_name, validate=False)
        logger.info('Start backup to {}'.format(backup_obj))
    if backup_obj:
        with smart_open.smart_open(backup_obj, 'wb',
                                   min_part_size=20 * 1024 ** 2) as dump_file:
            with GzipFile("dump", 'wb', 5, fileobj=dump_file) as gzip:
                backuped_docs = 0
                for item in database.iterview('_all_docs', 500, include_docs=True):
                    if item.id.startswith("_design/"):
                        continue
                    gzip.write(json.dumps(item.doc) + '\n')
                    backuped_docs += 1
                    logger.debug('Write docs: {}'.format(backuped_docs),
                                 extra={'BACKUPED_DOCS': backuped_docs, 'MESSAGE_ID': 'doc_backuped'})
    logger.info('End backup to {}'.format(backup_obj))


def restore(config):
    """
    restore to smart_open file
    """
    database = Database(config['couchdb'])

    with smart_open.smart_open(config['storage_uri'], 'rb') as dump_file:
        with GzipFile("dump", 'rb', 5, fileobj=dump_file) as gzip:
            buf = []
            restored_docs = 0
            for line in gzip:
                buf.append(json.loads(line))
                if len(buf) == 100:
                    database.update(buf)
                    buf = []
                restored_docs += 1
                logger.debug('Docs restored: {}'.format(restored_docs),
                             extra={'RESTORED_DOCS': restored_docs,
                                    'MESSAGE_ID': 'doc_restored'})
            database.update(buf)


def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description='---- CouchDb Dumper ----')
    parser.add_argument('cmd', type=str, help='backup or restoe')
    parser.add_argument('config', type=str, help='Path to configuration file')
    args = parser.parse_args()
    if os.path.isfile(args.config):
        with open(args.config) as config_file_obj:
            config = yaml_load(config_file_obj.read())
            logging.config.dictConfig(config)
            config = config.get('config', {})
            if args.cmd == "backup":
                backup(config['backup'])
            elif args.cmd == "restore":
                restore(config['restore'])


##############################################################
if __name__ == "__main__":
    main()
