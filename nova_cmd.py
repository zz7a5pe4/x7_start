"""utility for executing nova commands and filtering the output"""
import subprocess
import re

#Binary    Host         Zone       Status     State Updated_At
def service_list(stderr=False):
    """ nova-manage service list
    
    """
    p = subprocess.Popen(['nova-manage', 'service', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
#    print err+'\n'

    # out
    out_list = []
    lines = out.split('\n')
    del lines[0]
    # delete the extra empty item in list <lines> produced by the new-line character at the end of string <output>
    del lines[-1]
    for line in lines:
        words = line.split()
        dic = { 'Binary':words[0],
                'Host':words[1],
                'Zone':words[2],
                'Status':words[3],
                'State':words[4],
                'Updated_At':words[5]+' '+words[6]
              }
        out_list.append(dic) 
    if stderr:
        err_list = _get_err_list(err)
        return {'out':out_list, 'err':err_list}
    else:
        return out_list

def nova_list(stderr=False):
    """ nova list
    list all vm instances
    """
    p = subprocess.Popen(["nova", "list"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
 
    out_list = []
    lines = out.split('\n')
    del lines[0:3]
    for line in lines:
        if (not line.startswith("|" ) ) :
            continue
        words = line.split("|")
        del words[0]
        del words[-1]
        dic = { 'ID':words[0].strip(),
                'Name':words[1].strip(),
                'Status':words[2].strip(),
                'Networks':words[3].strip()
              }
        out_list.append(dic)
    if stderr:
        err_list = _get_err_list(err)
        return {'out':out_list, 'err':err_list}
    else:
        return out_list

def migrate(instance,stderr=False):
    """ migration

    $ nova migrate instance-00000002
    """
    p = subprocess.Popen(["nova", "migrate", instance], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    exit_code = p.wait()
    if stderr:
        err_list = _get_err_list(err)
        return {'out':[], 'err':err_list, 'exit':exit_code}
    else:
        return


def live_migrate(instance,host,stderr=False):
    """ live migration
    Don't use this function for the time being ...
    $ nova-manage vm live_migration instance-00000002 host105
    """
    p = subprocess.Popen(["nova-manage", "vm", "live_migration", instance, host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    out_list = []
    lines = out.split('\n')
#    del lines[0]
    # delete the extra empty item in list <lines> produced by the new-line character at the end of string <output>
    del lines[-1]
    for line in lines:
        out_list.append(line) 

    if stderr:
        err_list = _get_err_list(err)
        return {'out':out_list, 'err':err_list}
    else:
        return out_list


def resize_confirm(instance,stderr=False):
    """ resize confirm
    $ nova resize-confirm instance
    """
    p = subprocess.Popen(["nova", "resize-confirm",  instance], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    if stderr:
        err_list = _get_err_list(err)
        return {'out':[], 'err':err_list}
    else:
        return []


def host_list(stderr=False):
    """ nova-manage host list

    """
    p = subprocess.Popen(['nova-manage', 'host', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    out_list = []
    lines = out.split('\n')
    del lines[0]
    # delete the extra empty item in list <lines> produced by the new-line character at the end of string <output>
    del lines[-1]
    for line in lines:
        words = line.split()
        dic = { 'host':words[0],
                'zone':words[1],
              }
        out_list.append(dic)

    if stderr:
        err_list = _get_err_list(err)
        return {'out':out_list, 'err':err_list}
    else:
        return out_list


def vm_list(host=None,stderr=False):
    """ nova-manage vm list.

    """
    p = subprocess.Popen(['nova-manage', 'vm', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    lines = out.splitlines()
    del lines[0]
    out_list = []
    widths = [11,16,11,11,11,16,10,10,11,11,11,11,5]
    for line in lines:
        words = _split(line,widths)
        dic = { 'instance':words[0],
                'node':words[1],
                'type':words[2],
                'state':words[3],
                'launched':words[4]+words[5],
                'image':words[6],
                'kernel':words[7],
                'ramdisk':words[8],
                'project':words[9],
                'user':words[10],
                'zone':words[11],
                'index':words[12]}
        out_list.append(dic)

    if stderr:
        err_list = _get_err_list(err)
        return {'out':out_list, 'err':err_list}
    else:
        return out_list


def host_vm_list():
    """ list hosts and vms

    """
    # get hosts ---------------------------------
    p = subprocess.Popen(['nova-manage', 'host', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    hosts = []
    lines = out.splitlines()
    del lines[0]
    for line in lines:
        words = line.split()
        dic = { 'host':words[0],
                'zone':words[1],
                'instances':[]
              }
        hosts.append(dic)
    err_list = _get_err_list(err)

    # get instances ----------------------------- 
    p = subprocess.Popen(['nova-manage', 'vm', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    lines = out.splitlines()
    del lines[0]
    vms = []
    widths = [11,16,11,11,11,16,10,10,11,11,11,11,5]
    for line in lines:
        words = _split(line,widths)
        dic = { 'instance':words[0],
                'node':words[1],
                'type':words[2],
                'state':words[3],
                'launched':words[4]+words[5],
                'image':words[6],
                'kernel':words[7],
                'ramdisk':words[8],
                'project':words[9],
                'user':words[10],
                'zone':words[11],
                'index':words[12]}
        vms.append(dic)
    err_list = _get_err_list(err)

    # attach each vm instance to its host
    for vm in vms:
        node_name = vm['node']
        for host in hosts:
            host_name = host['host']
            if node_name == host_name:
                host['instances'].append(vm)
    return hosts
    
def _split(string, widths=None):
    """Split the string to n words with n = `len(widths)`. Each word has a minimum length specified by `widths`,
       hence whitespaces are filled to the rear of the words that have insufficient letters.
       The rest whitespaces are used as delimiter strings.
       
       `string` is the output of `print` statement, e.g. 
            print "%-10s %-15s ..." % (
                instance['display_name'],
                instance['host'],
                ...)

    """
    string = string.strip()
    pattern = '( +|[^ ]+)'
    words = []
    sub_strs = re.findall(pattern, string)
    if widths is None:
        for i in range(0,len(sub_strs),2):
            words.append(sub_strs[i])
    else:
        i = 0
        sp_shift = 0
        width = widths[0]
        for word in sub_strs:
            length = len(word)
            if word.startswith(' '):
                i += 1
                width = widths[i]
                sp_shift = sp_shift + width 
                while length > sp_shift:
                    words.append('')
                    sp_shift = sp_shift + width
                    i += 1
                    width = widths[i]
            else:
                if length > width:
                    sp_shift = 0
                else: 
                    sp_shift = width - length
                words.append(word)
    return words
   

def _get_err_list(err_msg):
    """ split a block of error messages into a list

    """
    err_list = []
    lines = err_msg.split('\n')
    # delete the extra empty item in list <lines> produced by the new-line character at the end of string <output>
    del lines[-1]
    for line in lines:
        err_list.append(line)   
    return err_list
