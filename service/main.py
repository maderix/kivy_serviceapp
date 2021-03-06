from time import sleep
import socket
from plyer import notification
from cStringIO import StringIO
import sys
from kivy.resources import resource_find,resource_add_path
import subprocess

PORT = 5995
IPDEF = "192.168.0.105"
#IP = "127.0.0.1"
HKEY_LEN = 256
HKEY = "TinyVPL"
CMD_LEN = 256
MOD_DIR = '../assets'

def get_ip(ifname):
   ipfile = open('ip','wb')
   subprocess.call('ifconfig ' + ifname +  ' | grep "inet addr" | cut -b21-33' , shell=True, stdout=ipfile)
   ipfile = open('ip','rb')
   op = ipfile.read()
   if op != '':
       print 'Manjeet: IP:', op.split('\n')[0]
       return op.split('\n')[0]
   else:
       return IPDEF

def get_mod(modname,moddir):
    mod_str = ''
    resource_add_path(moddir)
    modpath = resource_find(modname + '.module')
    print 'Manjeet: modpath ',modpath
    if modpath == None:
        print 'Module not found' , modpath
        return mod_str
    with open(modpath,'r') as mf:
        mod_str += mf.read()
    print 'Manjeet: module str:\n', mod_str
    return mod_str


#combine module files into a single text block
def combine_modules(module_dir):
    mod_blob = ''
    resource_add_path(module_dir)
    mfp = resource_find('modules')
    print mfp
    with open(mfp,'r') as mf:
        mods = mf.readlines()
        for mod in mods:
            print mod
            mod_path = resource_find(mod[:len(mod)-1])
            print mod_path
            if mod_path != None:
                modf = open(mod_path,'r')
                mod_blob += modf.read()
    return mod_blob

sock = socket.socket(socket.AF_INET, #INTERNET
                   socket.SOCK_STREAM) #TCP

IP = get_ip('enp0s3')
sock.bind((IP, PORT))
print 'Manjeet: initing TCP service @', IP, ':',PORT


if __name__ =='__main__':
    while 1:
        src=''
        sock.listen(1)
        conn, addr = sock.accept()
        print "Manjeet : initing TCP socket in service.Address=", addr
        #print "Manjeet : waiting for handshake key"
        #data = conn.recv(HKEY_LEN)
        #if data != HKEY:
        #    print "Incorrect handshake"
        #    conn.close()
        #    break
        #else:
        #    print "Handshake OK.Receiving command"
        #recv command
        cmd = conn.recv(CMD_LEN)
        if cmd == "source":
            while True:
                data = conn.recv(1024) #buffer size is 1024 bytes
                #print data
                #sleep(.1)
                src += data
                if 'def end_program():' in data:
                    break
        #try:
            print "Manjeet: received source:", src
            old_stdout = sys.stdout
            redirected_output = sys.stdout = StringIO()
            exec src
            sys.stdout = old_stdout
            result = redirected_output.getvalue()
            print 'Manjeet:result=' + result
            notification.notify(title='python code notification',message=result,
                                        app_name="kivy_test")
            conn.send(result) #send response
        #except:
        #    print 'Unexpected error ',sys.exc_info()[0]
        #    conn.close()
        #    exit(0)
        elif cmd == "schema":
            print 'Manjeet : Processing schema'
            #get the module name
            mod_name = conn.recv(CMD_LEN)
            print 'Manjeet:module name:',mod_name
            mb = get_mod(mod_name, MOD_DIR)
            conn.send(mb)
        else:
            print 'Unknown command'

        conn.close()
        print 'Manjeet: Connection closed'


