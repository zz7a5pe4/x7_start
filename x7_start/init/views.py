# Create your views here.
#!/usr/bin/python/
from django.shortcuts import render_to_response
from params import Params
from server.x7_mq import MqClient,MqReader,MqServer
import simplejson

import datetime

def home(request):
    return render_to_response('init/index.html')

def submit_env(request):
    params = Params( request.POST )
    
    w2sDict = { 'X7_Q':'X7_Q_W2S', 'X7_E':'X7_E_W2S', 'X7_RK':'X7_PK_W2S' }
    client = MqClient( w2sDict )
    client.connect()
    client.send( params.json() )      
    s2wDict = { 'X7_Q':'X7_Q_S2W', 'X7_E':'X7_E_S2W', 'X7_RK':'X7_PK_S2W' }
    srv = MqServer(None,s2wDict)
    srv.connect()
    return render_to_response('init/progress.html')


def get_progress( request ):
    #data = {}
    #now = datetime.datetime.now()
        
    #read from mq
    s2wDict = { 'X7_Q':'X7_Q_S2W', 'X7_E':'X7_E_S2W', 'X7_RK':'X7_PK_S2W' }
    reader = MqReader( s2wDict )
    reader.connect()
    
    dataList = []
    for i in range(1,6):
        mesg = reader.get()
        if mesg is not None:
            dataList.append( mesg.payload )
        else:
            break
    #data['msg'] = 'hello world! ' + now.strftime("%Y-%m-%d %H:%M:%S")
    #data['progress'] = '50'
    json = simplejson.dumps( dataList )
    #print json
    return render_to_response("init/ajax.html", { 'json': json }  )
    
