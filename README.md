# kinit hack for Superset
Superset doesn't yet support Kerberos, and so this is a dirty hack to make it possible to use Kerberized Hive as a Superset database.

## kerberos_reinit.py
This is a wrapper around `kinit`. It takes the following arguments:

- -r or --reinit_frequency
- -kp or --kerberos_principal
- -kt or --keytab
- -cc or --credential_cache

## enable Kerberos for PyHive
Superset uses PyHive to connect to Hive. The current version of PyHive (v0.2.1) doesn't work with Kerberos. Fortunately, there's a [pull request](https://github.com/dropbox/PyHive/pull/70) which adds support for Kerberos. To enable Kerberos in PyHive, just replace the code in `/usr/lib/python2.7/site-packages/pyhive/hive.py` with the [code from the pull request](https://github.com/axeisghost/PyHive/blob/ecd4a111c6e74648e79df427f1b16c6e0f24fee6/pyhive/hive.py).

## create the keytab
    ipa-getkeytab -s freeipa.woolford.io -p superset/superset.woolford.io@WOOLFORD.IO -k /etc/superset/superset.keytab superset
    chown superset:superset /etc/superset/superset.keytab
    chmod 440 /etc/superset/superset.keytab

## add to /etc/supervisord.conf
    [program:superset-kerberos-reinit]
    command=/usr/bin/python /home/superset/kerberos_reinit.py -r 3600 -kp superset/superset.woolford.io@WOOLFORD.IO -kt /etc/superset/superset.keytab -cc /tmp/superset_krb5_ccache
    user=superset
    stdout_logfile = /var/log/superset/superset-kerberos.log
    stdout_logfile_maxbytes = 100MB
    stdout_logfile_backups = 5 
    stderr_logfile = /var/log/superset/superset-kerberos.err
    stderr_logfile_maxbytes = 100MB
    stderr_logfile_backups = 5
