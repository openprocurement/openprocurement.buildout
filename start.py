import ConfigParser, os, uuid, subprocess


cur_dir = os.path.dirname(__file__)
couchdb_ini_file_path = os.path.join(cur_dir, 'etc/couchdb.ini')
if os.path.isfile(couchdb_ini_file_path):
    config = ConfigParser.ConfigParser()

    config.read([couchdb_ini_file_path])
    config.set('couchdb', 'uuid', uuid.uuid4().hex)

    with open(couchdb_ini_file_path, 'wb') as configfile:
        config.write(configfile)

subprocess.check_call([os.path.join(cur_dir, 'bin/circusd'), "--daemon"])