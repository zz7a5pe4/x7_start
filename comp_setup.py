#!/usr/bin/env python
# coding: utf-8

import os
import sys
import ssh
import subprocess
import time


def main(co):
    count = 10
    while(count):
        p = subprocess.Popen(('nc -z {0} 22'.format(co)).split(),
		                    shell=False,
		                    stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
        stdout, stderr = p.communicate())
        count -= 1;
        r = p.wait();
        print str(r)
        if r != 0:
	        print "pinging failed, trying, " + str(count) + " left"
	        time.sleep(2)
	        continue
        else :
            break;
    else:
        print "connecting failed"
        exit(-1)
    
    s = ssh.Connection(host=co,username="stack",password="vai123",port=22)
    s.put('stack.tar.gz')
    s.put('devstack.tar.gz')
    s.put('pip.tar.gz')
    s.put('imroot')
    s.put('localrc_compute')
    s.put('start_compute.sh')
    s.execute("chmod +x imroot");
    o = s.execute('echo vai123 | /home/stack/imroot')
    #print o
    s.execute("chmod +x start_compute.sh")
    o = s.execute('/home/stack/start_compute.sh')
    for l in o:
        print l.rstrip()
    s.close()


if __name__ == '__main__':
    main("10.0.0.101")
    sys.exit(0)