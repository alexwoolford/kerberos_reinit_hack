#!/usr/bin/env python

import logging
import os
import subprocess
import sys
import time
import argparse

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Kerberos reinit keeps the kerberos ticket alive.')
parser.add_argument('-r', '--reinit_frequency', help='reinitialization frequency in seconds', required=True)
parser.add_argument('-kp', '--kerberos_principal', help='kerberos principal', required=True)
parser.add_argument('-kt', '--keytab', help='kerberos keytab path', required=True)
parser.add_argument('-cc', '--credential_cache', help='kerberos credential cache', required=True)
args = vars(parser.parse_args())


def renew_from_kt():
    # Checks that the kinit executable is in the path
    kinit_path = which('kinit')
    if not kinit_path:
        raise EnvironmentError("kinit is not in the path.")

    reinit_frequency = "{0}s".format(args['reinit_frequency'])  # appends "s" to the number of seconds

    # create command
    cmdv = [kinit_path,
            "-r", reinit_frequency,
            "-k",  # host ticket
            "-t", args['keytab'],             # specify keytab
            "-c", args['credential_cache'],   # specify credentials cache
            args['kerberos_principal']]

    LOG.info("Reinitting kerberos from keytab: " + " ".join(cmdv))

    # execute command
    subp = subprocess.Popen(cmdv,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            close_fds=True,
                            bufsize=-1)
    subp.wait()

    if subp.returncode != 0:
        LOG.error("Couldn't reinit from keytab! `kinit` exited with %s.\n%s\n%s" % (
            subp.returncode,
            "\n".join(subp.stdout.readlines()),
            "\n".join(subp.stderr.readlines())))
        sys.exit(subp.returncode)


def run():
    while True:
        renew_from_kt()
        time.sleep(int(args['reinit_frequency']))


def which(program):
    """
    Mimics the behavior of Linux's 'which'. Credit to this StackOverflow post: http://stackoverflow.com/a/377028/2626491
    :param program: name of executable, e.g. kinit
    :return: full path to executable, e.g. /usr/bin/kinit
    """
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

if __name__ == "__main__":
    run()
