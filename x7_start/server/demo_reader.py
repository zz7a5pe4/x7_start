"""
X7 mq client function
"""

from x7_mq import MqReader

"""
read message with no wait
run this file and see result
and run demo_client.py and then run this file see result
and ...
"""
w2sDict = { 'X7_Q':'X7_Q_W2S', 'X7_E':'X7_E_W2S', 'X7_RK':'X7_PK_W2S' }
reader = MqReader( w2sDict )
reader.connect()
msg = reader.get( )      
if msg is not None:
    print msg.payload
else:
    print "read nothing"

   
