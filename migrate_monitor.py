"""
X7 live migration monitor
"""
import sys, os, subprocess
import time
import nova_cmd
from  x7_start.server.x7_mq import MqServer, MqClient
import simplejson
   
def handle_message( pkg, message):
    """callback function.

    """
    print("Received message: %r" % (pkg, ))   
    
    # kombu.transport.virtual.Message.ack():
    # Acknowledge this message as being processed. This will remove the message from the queue.
    message.ack()
    params = simplejson.loads( pkg )
    # start migration
    instance = params["instance"]
    print "\nstart migration ----------------------------- \n"
    output = nova_cmd.migrate(instance,True)
    out = output["err"]
    exit_code = output["exit"]
    print out
    if exit_code != 0:
        print "nova_cmd.migrate(instance,True) != 0"
        return 1 
    # - start migration - 
    end_time = time.time() + 120         # time limit in seconds
    interval = 2                          # in seconds
    while True:
        if (time.time() > end_time): 
            client.send( {"type": "cmd", "mesg": "error","memo":"migration: can't start migration","instance":instance} )
            return
        print "timeout"
        vm = _get_vm(instance)
        if (vm == None): 
            client.send( {"type": "cmd", "mesg": "error","memo":"migration: unkown instance","instance":instance} )
            print "vm == None"
            return
        vm_state = vm["Status"]
        print vm_state
        if(vm_state == "ACTIVE"):
            print "ACTIVE"
            pass                         # wait to start
        elif(vm_state == "VERIFY_RESIZE"):
            print "VERIFY_RESIZE"
            break                        # go to the next step
        elif(vm_state == "RESIZE"):
            print "RESIZE"
            break                         # go to the next step
        else:
            print ("else")
            client.send( {"type": "cmd", "mesg": "error","memo":"migration: " + vm_state,"instance":instance} )
            return
        time.sleep(interval)

    # -resize -
    print "\nresize ----------------------------- \n"
    end_time = time.time() + 1200         # time limit in seconds
    interval = 2                          # in seconds
    while True:
        if (time.time() > end_time): 
            print "timeout"
            client.send( {"type": "cmd", "mesg": "error","memo":"resize: time out","instance":instance} )
            return
        vm = _get_vm(instance)
        if (vm == None): 
            print "vm == None"
            client.send( {"type": "cmd", "mesg": "error","memo":"resize: failed","instance":instance} )
            return
        vm_state = vm["Status"]
        if(vm_state == "ACTIVE"):
            print "ACTIVE"
            client.send( {"type": "cmd", "mesg": "success","memo":"migration succeded","instance":instance} )
            return
        elif(vm_state == "VERIFY_RESIZE"):
            print "VERIFY_RESIZE"
            break                        # go to the next step
        elif(vm_state == "RESIZE"):
            print "RESIZE"
            pass                         # waiting
        else:
            print "else"
            client.send( {"type": "cmd", "mesg": "error","memo":"resize: " + vm_state,"instance":instance} )
            return
        time.sleep(interval)

    # - verify resize -
    nova_cmd.resize_confirm(instance)
    print "\nverify resize ----------------------------- \n"

    end_time = time.time() + 120           # time limit in seconds
    interval = 2                          # in seconds
    while True:
        if (time.time() > end_time): 
            print "timeout"
            client.send( {"type": "cmd", "mesg": "error","memo":"verify_resize: time out","instance":instance} )
            return
        vm = _get_vm(instance)
        if (vm == None): 
            print "vm == None"
            client.send( {"type": "cmd", "mesg": "error","memo":"verify_resize: failed","instance":instance} )
            return
        vm_state = vm["Status"]
        if(vm_state == "ACTIVE"):
            print "RESIZE"
            client.send( {"type": "cmd", "mesg": "success","memo":"migration succeded","instance":instance} )
            return
        elif(vm_state == "VERIFY_RESIZE"):
            print "VERIFY_RESIZE"
            pass                          # waiting
        else:
            print "else"
            client.send( {"type": "cmd", "mesg": "error","memo":"verify_resize: " + vm_state,"instance":instance} )
            return
        time.sleep(interval)

    return

def _get_vm(instance):
    vms = nova_cmd.nova_list()
    for vm in vms:
        if(instance == vm["Name"] ):
            return vm
    return None

def _get_vm_use_vm_list(instance):   # deprecated. backup
    vms = nova_cmd.vm_list()
    for vm in vms:
        if(instance == vm["instance"] ):
            return vm
    return None

def handle_message_deprecated( pkg, message):
    """callback function. deprecated

    """
    print("Received message: %r" % (pkg, ))
    
    # kombu.transport.virtual.Message.ack():
    # Acknowledge this message as being processed. This will remove the message from the queue.
    message.ack()
    params = simplejson.loads( pkg )
    # start migration
    instance = params["instance"]
    host = params["host"]
    nova_cmd.live_migrate(instance,host)

    # check progress
    wait_limit = 600                      # in seconds
    end_time = time.time() #+ wait_time    #
    interval = 2 
    checking = True
    while checking and  time.time() < end_time:
        vms = nova_cmd.vm_list(host)
        for vm in vms:
            if(instance == vm["instance"] ):
                vm_state = vm["state"]
                if(vm_state == "running"):   # TODO
                    client.send( {"type": "cmd", "mesg": "success","memo":"","instance":instance} )
                    checking = False
                elif(vm_state == "error"):  #TODO
                    client.send( {"type": "cmd", "mesg": "ongoing","memo":"","instance":instance} )
                    checking = False
                else:
                    pass
        time.sleep(interval)
# end_time = time.time() + 10

    return

if __name__ == '__main__':
#    client.send( simplejson.dumps( data )  )
    #create MS2W queue     
    ms2wDict = { 'X7_Q':'X7_Q_MS2W', 'X7_E':'X7_E_MS2W', 'X7_RK':'X7_PK_MS2W' }
    server = MqServer( None, ms2wDict )
    server.create_queue()
     
    ms2wDict = { 'X7_Q':'X7_Q_MS2W', 'X7_E':'X7_E_MS2W', 'X7_RK':'X7_PK_MS2W' }
    client = MqClient( ms2wDict )
    client.connect()

    mw2sDict = { 'X7_Q':'X7_Q_MW2S', 'X7_E':'X7_E_MW2S', 'X7_RK':'X7_PK_MW2S' }
    mq_server = MqServer( handle_message, mw2sDict)
    mq_server.connect()
    message = mq_server.run()
