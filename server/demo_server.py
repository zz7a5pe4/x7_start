"""
X7 mq server function
"""
from x7_mq import MqServer

w2sDict = { 'X7_Q':'X7_Q_W2S', 'X7_E':'X7_E_W2S', 'X7_RK':'X7_PK_W2S' }

#: This is the callback applied when a message is received.
def handle_message( pkg, message):
    print("Received message: %r" % (pkg, ))
    message.ack()

if __name__ == '__main__':
    mq_server = MqServer( handle_message, w2sDict )
    mq_server.connect()
    mq_server.run(once=False)



