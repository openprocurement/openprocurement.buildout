import argparse
import urlparse
import os
import ConfigParser
import subprocess
from requests import Session

ZONE_TO_ID = {
    'eu-west-1a': 'a',
    'eu-west-1b': 'b',
    'eu-west-1c': 'c'
}

cur_dir = os.path.dirname(__file__)
parser = argparse.ArgumentParser(description='------ AWS Startup Script ------')
parser.add_argument('api_dest', type=str, help='Destination to database')
params = parser.parse_args()
api_ini_file_path = os.path.join(cur_dir, 'etc/openprocurement.api.ini')
session = Session()
resp = session.get('http://169.254.169.254/latest/meta-data/placement/availability-zone')
if resp.status_code == 200:
    zone = resp.text
    zone_suffix = ZONE_TO_ID.get(zone, '')
    if zone_suffix:
        domain = '{}.{}'.format(zone_suffix, params.api_dest)
    else:
        domain =  params.api_dest
    if os.path.isfile(api_ini_file_path):
        config = ConfigParser.ConfigParser()
        config.read([api_ini_file_path])
        for k in ['couchdb.url', 'couchdb.admin_url']:
            value = config.get('app:api', k)
            url = urlparse.urlparse(value)
            if url.username:
                url = url._replace(netloc='{}:{}@{}:{}'.format(url.username, url.password,
                                                               domain, url.port))
            else:
                url = url._replace(netloc='{}:{}'.format(domain, url.port))
            config.set('app:api', k, url.geturl())
        if zone_suffix:
            config.set('app:api', 'id', zone_suffix)

        with open(api_ini_file_path, 'wb') as configfile:
            config.write(configfile)
