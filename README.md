# openprocurement.buildout
Backup Buildout of OpenProcurement

Follow the instructions:

  1. Bootstrap the buildout with Python 2.7:
  
     ```
     $ python bootstrap.py
     ```
     
  2. Build the buildout:
  
      ```
      $ bin/buildout -N
      ```
      
  3. If you haven’t configured bakthat yet, you should run:
  
      ```
      $ bin/bakthat configure
      $ bin/bakthat configure_backups_rotation
      ```

     >Bakthat rely on the GrandFatherSon module to compute rotations, so if you need to setup more complex rotation scheme 
     >(like hourly backups), refer to the docs and change the rotation settings manually in your configuration file.

     More about [Bakthat Configuration](https://github.com/tsileo/bakthat/blob/master/docs/user_guide.rst#configuration)

  4. Add 'backup-hourly' part to pars and re-build buildout

  