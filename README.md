# openprocurement.api-backup.buildout
Backup Buildout of OpenProcurement

Follow the instructions:

  1. Copy `buildout.cfg.example` to `buildout.cfg` with including all needed items.
      * For using monitoring add profile `profiles/statsd.cfg` to `extends`
      * In `dump.yaml` section option:
        * `cmd` receive two commands `dump` or `load`
          * `dump` - for backup
          * `load` - for restore from backup
        * `db_url` - url to couchdb with data for backuping
        * `dump_uri` - path to backup storage (can be path/on/drive or S3-path)

  1. Bootstrap the buildout with Python 2.7:

     ```
     $ python bootstrap.py
     ```

  1. Build the buildout:

      ```
      $ bin/buildout -N
      ```

  1. If you haven’t configured bakthat yet, you should run:

      ```
      $ bin/bakthat configure
      $ bin/bakthat configure_backups_rotation
      ```

     >Bakthat rely on the GrandFatherSon module to compute rotations, so if you need to setup more complex rotation scheme
     >(like hourly backups), refer to the docs and change the rotation settings manually in your configuration file.

     More about [Bakthat Configuration](https://github.com/tsileo/bakthat/blob/master/docs/user_guide.rst#configuration)

  1. Add 'backup-hourly' part to pars and re-build buildout
