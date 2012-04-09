#!/usr/bin/python

from  x7_start.server.x7_mq import MqServer
import simplejson
import sys, os
import subprocess

def handle_message( pkg, message):
    print("Received message: %r" % (pkg, ))
    message.ack()
    params = simplejson.loads( pkg )

    #begin write file 
    if os.path.isfile('localrc'):
        os.remove('localrc')
    
    eth_interface = params.get("FLAT_INTERFACE","eth0")
    subprocess.Popen(["./startup_2.sh", eth_interface])
    exit(-1);
    #file = open ( 'localrc', 'w' )
    #for k in params.keys():
    #    file.write( "%s=%s \n"  % (k,params[k]) )

    #file.close()
    
    
if __name__ == '__main__':
    w2sDict = { 'X7_Q':'X7_Q_W2S', 'X7_E':'X7_E_W2S', 'X7_RK':'X7_PK_W2S' }
    
    mq_server = MqServer( handle_message, w2sDict )
    mq_server.connect()
    message = mq_server.run(once=True)

