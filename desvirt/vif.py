import atexit
import random
import re
import shlex
import subprocess
import time

from .vnet import VirtualNet

class VirtualInterface():
    def __init__(self, macaddr=None, up=True, net=None, vmname=None,create=True,node=None,tap=None):
        self.tap = tap

        if create:
            self.tap = mktap(tap)
            
        self.state = 'down'
        self.vmname = vmname

        if not macaddr:
            macaddr = genmac()

        self.macaddr = macaddr
        
        if up and create:
            self.up()

        if net:
            self.net = net
            net.addif(self.tap,setup=create)

    def create(self):
        mktap(self.tap)

    def __str__(self):
        return self.tap
    
    def __repr__(self):
        return self.tap

    def delete(self):
        if self.state=='up':
            try:
                self.down()
            except Exception as e:
                print (e)

        for i in range(0,20):
            if rmtap(self.tap):
                break
#            print("tap %s busy, retrying..." % self.tap)
            time.sleep(1)

    def up(self):
        self.ifconfig('up')
        self.state='up'

    def down(self):
        self.ifconfig('down')
        self.state='down'

    def ifconfig(self, cmd):
        subprocess.call(shlex.split("ifconfig %s %s" % (self.tap, cmd))) 

#if __name__='__main__':
#    print('vif test:')

def mktap(tap=None):
    args = [ 'tunctl', '-u', 'libvirt-qemu']
    if tap:
        args.extend(['-t', tap])

    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    (stdout, stderr) = p.communicate()

    if p.poll() != 0:
        return None

    if tap:
        return tap

    output = stdout.encode('utf-8')
    
    re_tap = re.compile("^Set '(?P<tap>.+)' persistent and owned by uid (?P<uid>[0-9]+)$")
    m = re_tap.match(output)

    return m.group('tap')
    
def rmtap(name):
    null = open('/dev/null', 'wb')
    retcode = subprocess.call(['tunctl', '-d', name], stdout=null)
    null.close()
    return retcode == 0

def genmac():
    mac = [ 0x50, 0x51, 0x52,  
    random.randint(0x00, 0x7f),  
    random.randint(0x00, 0xff),  
    random.randint(0x00, 0xff) ]  

    return (':'.join(map(lambda x: "%02x" % x, mac)))

