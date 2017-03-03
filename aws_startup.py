import argparse
import urlparse
import os
import ConfigParser
import subprocess
from requests import Session

cur_dir = os.path.dirname(__file__)
parser = argparse.ArgumentParser(description='------ AWS Startup Script ------')
parser.add_argument('api_dest', type=str, help='Destination to database')
params = parser.parse_args()
api_ini_file_path = os.path.join(cur_dir, 'etc/openprocurement.api.ini')
session = Session()
resp = session.get('http://169.254.169.254/latest/meta-data/placement/availability-zone')
if resp.status_code == 200:
    zone = resp.text
    domain = '{}.{}'.format(zone, params.api_dest)
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

        with open(api_ini_file_path, 'wb') as configfile:
            config.write(configfile)

subprocess.check_call([os.path.join(cur_dir, 'bin/circusd'), "--daemon"])
