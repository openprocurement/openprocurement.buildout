# -*- coding: utf-8 -*-
"""
Couchdb Dumper
"""
import logging
import argparse
import smart_open
from couchdb.client import Database
import json

from gzip import GzipFile
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def dump(db_url, dump_uri):
    """
    Dump to smart_open file
    """
    db = Database(db_url)
    with smart_open.smart_open(dump_uri, 'wb', min_part_size=20 * 1024 ** 2) as dump_file:
        with GzipFile("dump", 'wb', 5, fileobj=dump_file) as gzip:
            for item in db.iterview('_all_docs', 500, include_docs=True):
                if item.id.startswith("_design/"):
                    continue
                gzip.write(json.dumps(item.doc) + '\n')

def load(db_url, dump_uri):
    """
    Dump to smart_open file
    """
    db = Database(db_url)
    with smart_open.smart_open(dump_uri, 'rb') as dump_file:
        with GzipFile("dump", 'rb', 5, fileobj=dump_file) as gzip:
            buf = []
            for line in gzip:
                buf.append(json.loads(line))
                if len(buf) == 100:
                    db.update(buf)
                    buf = []
            db.update(buf)


def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description='---- CouchDb Dumper ----')
    parser.add_argument('cmd', type=str, help='http://{user}:{password}@{host}:{port}/{database}')
    parser.add_argument('db_url', type=str, help='http://{user}:{password}@{host}:{port}/{database}')
    parser.add_argument('dump_uri', type=str, help='like s3://{bucket}/{key}')
    args = parser.parse_args()
    if args.cmd == "dump":
        dump(args.db_url, args.dump_uri)
    elif args.cmd == "load":
        load(args.db_url, args.dump_uri)

##############################################################
if __name__ == "__main__":
    main()
