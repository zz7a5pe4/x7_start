#!/usr/bin/python

"""
X7 mq server function
"""
from  x7_start.server.x7_mq import MqClient

import sys;

def main():
    msg = sys.argv[2:]
    w2sDict = { 'X7_Q':'X7_Q_S2W', 'X7_E':'X7_E_S2W', 'X7_RK':'X7_PK_S2W' }
    client = MqClient( w2sDict )
    client.connect()  
    msg = int(msg) if sys.argv[1] == "prog" else msg
    client.send({"type":sys.argv[1], "mesg":msg})
    print(msg)
    client.close()



if __name__ == "__main__":
	if(len(sys.argv) < 3):
		print "bad parameters"
	else:
		main();
