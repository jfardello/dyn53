Dyn53
=====

A tool for updating route53 addresses, simulating a dynamic DNS service by
asking `ipify.org <http://ipify.org>`_ and using boto3, it is meant to run
via crontab on python3 enabled devices. It uses, dnspython, certifi, requests,
and boto3.

Install
-------

    ``pip install dyn53``

Alternatively, download the package, decompress and run:

 ``python setup.py install``


Usage
-----

Configure dyn53 by editing ~/.config/dyn53.conf, if the file is not present,
a sample one will be created. Boto3 config is not required, nor used.

.. code-block:: bash

    > dyn53
    2016-07-25 14:22:58,212 - dyn53 - INFO - Creating sample config file: /home/user/.config/dyn53.conf.sample
    No config file found, exiting.

    > cat ~/.config/dyn53.conf.sample
    [dyn53]
    hosted_zone_id = My hosted Zone Id
    domain = domain.tld.
    ttl = 300
    debug = False
    aws_sec_key = MY SECRET KEY
    aws_key = MY KEY

    > mv ~/.config/dyn53.conf.sample ~/.config/dyn53.conf
    > vi ~/.config/dyn53.conf

    > dyn53  -s myhost --debug
    2016-07-26 00:42:31,646 - dyn53 - DEBUG - Got ip: 52.37.72.89
    2016-07-26 00:42:31,707 - dyn53 - DEBUG - FQDN is already pointing to 52.37.72.89

Notes
-----

* If no address is passed as argument ([-a address]), ipify.org service will
  be checked via https to resolve the current public IP address.
* dyn53 is lazy, if the domain is already pointing to the resolved or given
  address, it wont update the record.
