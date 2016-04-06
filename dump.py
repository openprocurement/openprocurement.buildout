# -*- coding: utf-8 -*-
"""
Couchdb Dumper
"""
import argparse
import smart_open
from couchdb.client import Database
import json
# db_url = "http://admin:zaq1xsw2@localhost:12000/auctions"
# # dump_uri = 'auction_dump'
# dump_uri = "s3://openprocurement-database-backup-sandbox/test_dump.file"


def dump(db_url, dump_uri):
    """
    Dump to smart_open file
    """
    db = Database(db_url)
    with smart_open.smart_open(dump_uri, 'wb') as dump_file:
        for item in db.iterview('_all_docs', 10, include_docs=True):
            if item.id.startswith("_design/"):
                continue
            dump_file.write(json.dumps(item.doc) + '\n')


def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description='---- CouchDb Dumper ----')
    parser.add_argument('db_url', type=str, help='http://{user}:{password}@{host}:{port}/{database}')
    parser.add_argument('dump_uri', type=str, help='like s3://{bucket}/{key}')
    args = parser.parse_args()
    dump(args.db_url, args.dump_uri)

##############################################################
if __name__ == "__main__":
    main()
