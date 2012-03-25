"""
X7 mq client function
"""

from x7_mq import MqClient

#Message from web to server
w2sDict = { 'X7_Q':'X7_Q_W2S', 'X7_E':'X7_E_W2S', 'X7_RK':'X7_PK_W2S' }
client = MqClient( w2sDict )
client.connect()
client.send( {"hello": "world"} )      
client.send( {"hello1": "world1"} )     
   
