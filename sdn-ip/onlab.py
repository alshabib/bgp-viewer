#!/usr/bin/python

"""
Start up a Simple topology
"""

from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.util import quietRun
from mininet.moduledeps import pathCheck

from sys import exit
import os.path
from subprocess import Popen, STDOUT, PIPE

IPBASE = '192.168.10.0/24'
IPCONFIG_FILE = '/home/ubuntu/cs144_lab3/IP_CONFIG'
IP_SETTING={}

class SDNTopo( Topo ):
    "SDN Topology"
    
    def __init__( self, *args, **kwargs ):
        Topo.__init__( self, *args, **kwargs )
        sw1 = self.add_switch('sw1', dpid='00000000000000a1')
        sw2 = self.add_switch('sw2', dpid='00000000000000a2')
        sw3 = self.add_switch('sw3', dpid='00000000000000a3')
        sw4 = self.add_switch('sw4', dpid='00000000000000a4')
        sw5 = self.add_switch('sw5', dpid='00000000000000a5')
        sw6 = self.add_switch('sw6', dpid='00000000000000a6')

        host1 = self.add_host( 'host1' )
        host2 = self.add_host( 'host2' )
        root1 = self.add_host( 'root1', inNamespace=False )
        root2 = self.add_host( 'root2', inNamespace=False )

        self.add_link( host1, sw1 )
        self.add_link( host2, sw1 )

        ## Internal Connection To Hosts ##
        self.add_link( root1, host1 )
        self.add_link( root2, host2 )

        self.add_link( sw1, sw2 )
        self.add_link( sw1, sw3 )
        self.add_link( sw2, sw4 )
        self.add_link( sw3, sw4 )
        self.add_link( sw3, sw5 )
        self.add_link( sw4, sw6 )
        self.add_link( sw5, sw6 )

def startsshd( host ):
    "Start sshd on host"
    info( '*** Starting sshd\n' )
    name, intf, ip = host.name, host.defaultIntf(), host.IP()
    banner = '/tmp/%s.banner' % name
    host.cmd( 'echo "Welcome to %s at %s" >  %s' % ( name, ip, banner ) )
    host.cmd( '/usr/sbin/sshd -o "Banner %s"' % banner, '-o "UseDNS no"' )
    info( '***', host.name, 'is running sshd on', intf, 'at', ip, '\n' )

def startsshds ( hosts ):
    for h in hosts:
        startsshd( h )

def stopsshd( ):
    "Stop *all* sshd processes with a custom banner"
    info( '*** Shutting down stale sshd/Banner processes ',
          quietRun( "pkill -9 -f Banner" ), '\n' )


def starthttp( host ):
    "Start simple Python web server on hosts"
    info( '*** Starting SimpleHTTPServer on host', host, '\n' )
    #host.cmd( 'cd ~/http_%s/; python -m SimpleHTTPServer 80 >& /tmp/%s.log &' % (host.name, host.name) )
    #host.cmd( 'cd ~/http_%s/; nohup python2.7 ~/http_%s/webserver.py >& /tmp/%s.log &' % (host.name, host.name, host.name) )
    host.cmd( 'cd ~/http_%s/; nohup python2.7 ~/http_%s/webserver.py &' % (host.name, host.name) )
    #host.cmd( 'cd ~/http_%s/; screen -S webserver -D -R python2.7 ~/http_%s/webserver.py ' % (host.name, host.name) )

def set_default_route(host):
    info('*** setting default gateway of host %s\n' % host.name)
    if(host.name == 'server1'):
        routerip = IP_SETTING['sw0-eth1']
    elif(host.name == 'server2'):
        routerip = IP_SETTING['sw0-eth2']
    print host.name, routerip
    host.cmd('route add default gw %s dev %s-eth0' % (routerip, host.name))
    #HARDCODED
    #host.cmd('route del -net 10.3.0.0/16 dev %s-eth0' % host.name)
    ips = IP_SETTING[host.name].split(".") 
    host.cmd('route del -net %s.0.0.0/8 dev %s-eth0' % (ips[0], host.name))

def get_ip_setting():
    if (not os.path.isfile(IPCONFIG_FILE)):
        return -1
    f = open(IPCONFIG_FILE, 'r')
    for line in f:
        if( len(line.split()) == 0):
          break
        name, ip = line.split()
        print name, ip
        IP_SETTING[name] = ip
    return 0

def sdn1net():
    "Create a simple network for cs144"
#    r = get_ip_setting()
#    if r == -1:
#        exit("Couldn't load config file for ip addresses, check whether %s exists" % IPCONFIG_FILE)
#    else:
#        info( '*** Successfully loaded ip settings for hosts\n %s\n' % IP_SETTING)

    topo = SDNTopo()
    info( '*** Creating network\n' )
    net = Mininet( topo=topo, controller=RemoteController )

    host1, host2  = net.get( 'host1', 'host2' )

    ## Adding 2nd, 3rd and 4th interface to host1 connected to sw1 (for another BGP peering)
    sw1 = net.get('sw1')
    link1 = host1.linkTo( sw1 )
    link1.intf1.setIP('192.168.20.101', 24 )
    link2 = host1.linkTo( sw1 )
    link2.intf1.setIP('192.168.30.101', 24 )
    link3 = host1.linkTo( sw1 )
    link3.intf1.setIP('192.168.40.101', 24 )

    # Net has to be start after adding the above link
    net.start()

    sw2 = net.get('sw3')
    sw2.attach('tap0')
    sw3 = net.get('sw5')
    sw3.attach('tap1')

    sw4 = net.get('sw2')
    sw4.attach('tap2')
    sw6 = net.get('sw6')
    sw6.attach('tap3')

    host1.defaultIntf().setIP('192.168.10.101/24') 
#    host1.cmd('ifconfig %s-eth0:1 192.168.30.101 netmask 255.255.255.0 up' % (host1.name))
    host1.cmd('/home/ubuntu/ZebOS-BGPd/bgpd -d -f /home/ubuntu/ZebOS-BGPd/bgpd.sdn1vpc.conf')
    host1.cmd('/usr/sbin/tcpdump -n -i host1-eth1 -s0 -w /home/ubuntu/sdn/sdn1vpc.host1-eth1.pcap "!tcp port 22" &')
    host1.cmd('/sbin/route add default gw 192.168.10.254 dev %s-eth0' % (host1.name))

    # Configure new host interfaces
#    host1.setIP( link1.inf1, '192.168.30.101', 24 )
    host2.defaultIntf().setIP('172.16.10.2/24') 
    host2.defaultIntf().setMAC('00:00:00:00:00:02') 
    host2.cmd('/sbin/route add default gw 172.16.10.254 dev %s-eth0' % (host2.name))
    #start add by linpp
    host2.cmd('sudo arp -s 172.16.10.254 00:00:00:00:00:03')
    #end add by linpp
#    host2.defaultIntf().setIP('192.168.10.102/24') 
#    host2.cmd('route add default gw 192.168.10.254 dev %s-eth0' % (host1.name))
#    host2.cmd('route add -net 192.168.20.0/24 gw 192.168.10.1 dev %s-eth0' % (host2.name))

    root1, root2  = net.get( 'root1', 'root2' )
    host1.intf('host1-eth1').setIP('1.1.1.1/24')
    root1.intf('root1-eth0').setIP('1.1.1.2/24')
    host2.intf('host2-eth1') .setIP('1.1.2.1/24')
    root2.intf('root2-eth0').setIP('1.1.2.2/24')

    hosts = [ host1, host2 ];
    stopsshd ()
    startsshds ( hosts )

#    CLI( net )
#    stopsshd()
#    host1.cmd('pkill -TERM zebra')
#    host1.cmd('pkill -TERM bgpd')
#    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    sdn1net()
