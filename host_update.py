#!/usr/bin/env python
# coding: utf-8

import os
import sys
import ssh
import subprocess
import time


def main(co):
    for h in co:
        s = ssh.Connection(host=h,username="stack",password="vai12345",port=22)
        s.put('conf/etc/hosts')
        s.execute("sudo cp -f hosts /etc/hosts");
        s.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "usage: {0} COMPIP1 COMPIP2 COMPIP3 ....".format(sys.argv[0]);
    else:
        main(sys.argv[1:])
    sys.exit(0)

