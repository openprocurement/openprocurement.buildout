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
import sys

logger = logging.getLogger('dumper')


def dump(db_url, dump_uri):
    """
    Dump to smart_open file
    """
    db = Database(db_url)
    with smart_open.smart_open(dump_uri, 'wb',
                               min_part_size=20 * 1024 ** 2) as dump_file:
        with GzipFile("dump", 'wb', 5, fileobj=dump_file) as gzip:
            backuped_docs = 0
            for item in db.iterview('_all_docs', 500, include_docs=True):
                if item.id.startswith("_design/"):
                    continue
                gzip.write(json.dumps(item.doc) + '\n')
                backuped_docs += 1
                logger.debug('Write docs: {}'.format(backuped_docs),
                             extra={'BACKUPED_DOCS': backuped_docs,
                                    'MESSAGE_ID': 'doc_backuped'})


def load(db_url, dump_uri):
    """
    Dump to smart_open file
    """
    db = Database(db_url)
    with smart_open.smart_open(dump_uri, 'rb') as dump_file:
        with GzipFile("dump", 'rb', 5, fileobj=dump_file) as gzip:
            buf = []
            restored_docs = 0
            for line in gzip:
                buf.append(json.loads(line))
                if len(buf) == 100:
                    db.update(buf)
                    buf = []
                restored_docs += 1
                logger.debug('Docs restored: {}'.format(restored_docs),
                             extra={'RESTORED_DOCS': restored_docs,
                                    'MESSAGE_ID': 'doc_restored'})
            db.update(buf)


def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description='---- CouchDb Dumper ----')
    parser.add_argument('config', type=str, help='Path to configuration file')
    args = parser.parse_args()
    if os.path.isfile(args.config):
        with open(args.config) as config_file_obj:
            config = yaml_load(config_file_obj.read())
            logging.config.dictConfig(config)
            cmd = config.get('dump', {}).get('cmd')
            db_url = config.get('dump', {}).get('db_url')
            dump_uri = config.get('dump', {}).get('dump_uri')
            if cmd == "dump":
                t_now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
                dump_uri_with_timestamp = '{}_{}.back'.format(dump_uri, t_now)
                dump(db_url, dump_uri_with_timestamp)
            elif cmd == "load":
                load(db_url, dump_uri)


##############################################################
if __name__ == "__main__":
    main()
