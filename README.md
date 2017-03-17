# openprocurement.edge.buildout
Development Buildout of OpenProcurement Edge

Follow the instructions:
  1. Copy `buildout.cfg.example` to `buildout.cfg` with including all needed items. For example:
  `buildout.cfg` for **Edge prozorro sandbox** with available resources [`contracts`, `plans`, `tenders`]:
  ```
  [buildout]
  extends =
      profiles/production.cfg
      profiles/contracts.cfg
      profiles/plans.cfg
      profiles/tenders.cfg

  [edge_data_bridge_defaults]
  user_agent = my_platform_name
  resources_api_server = http://public.api-sandbox.openprocurement.org  
  ```
  2. Bootstrap the buildout with Python 2.7:

     ```
     $ python bootstrap.py
     ```

  3. Build the buildout:

      ```
      $ bin/buildout -N
      ```

System requirements (Fedora 24):

    dnf install zeromq3-devel git gcc python-devel file python2-systemd python-virtualenv sqlite-devel libffi-devel openssl-devel libsodium libsodium-devel redhat-rpm-config logrotate libselinux-python bash-completion policycoreutils-python policycoreutils-python-utils nginx

Local development environment also requires additional dependencies:

    dnf install couchdb ctorrent

To start environment services:

    bin/circusd --daemon

To debug problems (if any) see `var/log/circus.log` and other `var/log/*.log` log files.

To to run *openprocurement.edge* instance:

    bin/chaussette paste:etc/openprocurement.edge.ini

To to run one of *databridge* instance:

    bin/edge_data_bridge etc/edge_data_bridge_tenders.yaml
You can replace `etc/edge_data_bridge_tenders.yaml` to:
  * `etc/edge_data_bridge_auctions.yaml`
  * `etc/edge_data_bridge_contracts.yaml`
  * `etc/edge_data_bridge_plans.yaml`

before configuring `buildout.cgf` according resources.
