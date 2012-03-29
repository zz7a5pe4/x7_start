"""
X7 mq client function
"""

from x7_mq import MqClient

#Message from web to server
s2wDict = { 'X7_Q':'X7_Q_S2W', 'X7_E':'X7_E_S2W', 'X7_RK':'X7_PK_S2W' }

client = MqClient( s2wDict )
client.connect()
client.send( {"type": "log", "mesg":"hello1"} )      
client.send( {"type": "prog", "mesg":90} )  
client.send( {"type": "cmd", "mesg":"complete"} )     
   
