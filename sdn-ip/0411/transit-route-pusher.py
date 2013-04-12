#! /usr/bin/python

import os
import sys
import subprocess
import json
import argparse
import io
import time

from flask import Flask

GatewayIPs={'192.168.10.1', '192.168.20.1', '192.168.30.1', '192.168.40.1'}
AS={"192.168.10.1": "AS2", "192.168.20.1":"AS2","192.168.30.1":"AS3","192.168.40.1":"AS4"}
controllerRestIp="127.0.0.1:8090"
BGPdRestIp="1.1.1.1:8080"
RouterId="192.168.10.101"

def log_debug ( string ):
    localtime = time.asctime( time.localtime(time.time()) )
    print "[DEBUG] " + localtime + " " + string

def log_error ( string ):
    localtime = time.asctime( time.localtime(time.time()) )
    print "[ERROR] " + localtime + " " + string

def log_warn ( string ):
    localtime = time.asctime( time.localtime(time.time()) )
    print "[WARN] " + localtime + " " + string

app = Flask(__name__)

@app.route("/")
def hello():
    return "Static Transit Route Pusher\nAvailable Commands:/bgp_update, /init, /topo_change\n"

@app.route("/bgp_update")
def bgp_update():
    time.sleep(2)
    log_debug("bgp_update received")
    resolve_gateway ( GatewayIPs )
    prefixbased_mac_rewrite()
    return "bgp_update done\n"

@app.route("/init")
def initialize():
    resolve_gateway ( GatewayIPs )
    install_routes ("all")
    log_debug("222")
    prefixbased_mac_rewrite()
    return "init command done\n"

@app.route("/topo_change")
def topo_change():
    time.sleep(2)
    log_debug("topo_change received")
    resolve_gateway ( GatewayIPs )
    install_routes ("all")
    prefixbased_mac_rewrite()
    return "topo_change done\n"


#add by linpp
#@app.route("/topo_change_lpp")
#def topo_change_lpp():
 #   time.sleep(2)
  #  log_debug("topo_change received")
   # resolve_gateway_lpp ( GatewayIPs )
   # install_routes ("all")
   # prefixbased_mac_rewrite()
   # return "topo_change done\n"
#end add by linpp




Gateway={}


#add by linpp

#Gateway={}
#def resolve_gateway_lpp ( GatewayIPs ):


           # result = {'192.168.40.1': {'mac': u'e6:d7:3a:7e:b0:db', 'ipv4': u'192.168.40.1', 'switch': u'00:00:00:00:00:00:00:a6', 'as': 'AS4', 'port': 3}, '192.168.30.1': {'mac': u'02:55:cf:ff:b1:29', 'ipv4': u'192.168.30.1', 'switch': u'00:00:00:00:00:00:00:a2', 'as': 'AS3', 'port': 3}, '192.168.20.1': {'mac': u'ce:33:f4:f1:de:0f', 'ipv4': u'192.168.20.1', 'switch': u'00:00:00:00:00:00:00:a5', 'as': 'AS2', 'port': 3}, '192.168.10.1': {'mac': u'06:b3:f3:97:07:22', 'ipv4': u'192.168.10.1', 'switch': u'00:00:00:00:00:00:00:a3', 'as': 'AS2', 'port': 4}}
        
 #       gateway2={}
  #      gateway2['mac']=u'06:b3:f3:97:07:22'
   #     gateway2['switch']=u'00:00:00:00:00:00:00:a3'
    #    gateway2['port']=4
     #   gateway2['ipv4']=u'192.168.10.1'
      #  gateway2['as']='AS2'
       # Gateway['192.168.10.1']=gateway2


#        gateway2={}
 #       gateway2['mac']=u'ce:33:f4:f1:de:0f'
  #      gateway2['switch']=u'00:00:00:00:00:00:00:a5'
   #     gateway2['port']=3
    #    gateway2['ipv4']=u'192.168.20.1'
     #   gateway2['as']='AS2'
      #  Gateway['192.168.20.1']=gateway2

#    	gateway2={}
 #       gateway2['mac']=u'02:55:cf:ff:b1:29'
  #      gateway2['switch']=u'00:00:00:00:00:00:00:a2'
   #     gateway2['port']=3
    #    gateway2['ipv4']=u'192.168.30.1'
     #   gateway2['as']='AS3'
      #  Gateway['192.168.30.1']=gateway2
##	
#	Gateway['192.168.30.1']={}
	
#	gateway2={}
 #       gateway2['mac']=u'e6:d7:3a:7e:b0:db'
  #      gateway2['switch']=u'00:00:00:00:00:00:00:a6'
   #     gateway2['port']=3
    #    gateway2['ipv4']=u'192.168.40.1'
#        gateway2['as']='AS4'
 #       Gateway['192.168.40.1']=gateway2

#end add by linpp




def resolve_gateway ( GatewayIPs ):

  
           # result = {'192.168.40.1': {'mac': u'e6:d7:3a:7e:b0:db', 'ipv4': u'192.168.40.1', 'switch': u'00:00:00:00:00:00:00:a6', 'as': 'AS4', 'port': 3}, '192.168.30.1': {'mac': u'02:55:cf:ff:b1:29', 'ipv4': u'192.168.30.1', 'switch': u'00:00:00:00:00:00:00:a2', 'as': 'AS3', 'port': 3}, '192.168.20.1': {'mac': u'ce:33:f4:f1:de:0f', 'ipv4': u'192.168.20.1', 'switch': u'00:00:00:00:00:00:00:a5', 'as': 'AS2', 'port': 3}, '192.168.10.1': {'mac': u'06:b3:f3:97:07:22', 'ipv4': u'192.168.10.1', 'switch': u'00:00:00:00:00:00:00:a3', 'as': 'AS2', 'port': 4}}
	
	#add by linpp
#	Gateway={}
	#end add by linpp
	gateway={}
        gateway['mac']=u'06:b3:f3:97:07:22'
        gateway['switch']=u'00:00:00:00:00:00:00:a3'
        gateway['port']=4
        gateway['ipv4']=u'192.168.10.1'
        gateway['as']='AS2'
	gateway['no']=3
        Gateway['192.168.10.1']=gateway


        gateway={}
        gateway['mac']=u'ce:33:f4:f1:de:0f'
        gateway['switch']=u'00:00:00:00:00:00:00:a5'
        gateway['port']=3
        gateway['ipv4']=u'192.168.20.1'
        gateway['as']='AS2'
	gateway['no']=5
        Gateway['192.168.20.1']=gateway

	gateway={}
        gateway['mac']=u'02:55:cf:ff:b1:29'
        gateway['switch']=u'00:00:00:00:00:00:00:a2'
        gateway['port']=3
        gateway['ipv4']=u'192.168.30.1'
        gateway['as']='AS3'
	gateway['no']=2
        Gateway['192.168.30.1']=gateway

	gateway={}
        gateway['mac']=u'e6:d7:3a:7e:b0:db'
        gateway['switch']=u'00:00:00:00:00:00:00:a6'
        gateway['port']=3
        gateway['ipv4']=u'192.168.40.1'
        gateway['as']='AS4'
	gateway['no']=6
        Gateway['192.168.40.1']=gateway

	print Gateway
	#add by linpp
#	log_debug(Gateway)
	#end add by linpp

def prefixbased_mac_rewrite():
#    bgp_command = "curl -s http://%s/wm/bgp/%s" % (BGPdRestIp, RouterId)
    bgp_command="curl -s http://%s/wm/bgp/json" % (controllerRestIp)
    bgp_result = os.popen(bgp_command).read()
    bgp_parsedResult = json.loads(bgp_result)
    log_debug("333")
    for f in Gateway:
        try:
            dpid = Gateway[f]['switch']
            ingressPort = Gateway[f]['port']
            smac = Gateway[f]['mac']
            s_ip = Gateway[f]['ipv4']
            for p in bgp_parsedResult['rib']:
                if p['nexthop'] != '0.0.0.0':
                    dst_subnet = p['prefix']
                    dst_ip = p['nexthop']
                    if dst_ip != s_ip:
                        found = 0
                        for t in GatewayIPs: 
                            if Gateway[t]['ipv4'] == dst_ip:
                                new_dmac = Gateway[t]['mac']
                                destSwitch = Gateway[t]['switch']
                                destPort = Gateway[t]['port']
                                found = 1
                                break;
                        log_debug("444")
			log_debug("found=%s" % found)    
                        if (found == 1):
		            log_debug("haha")
		            temp=Gateway[f]['no']
			    log_debug("Gateway[f]['no']: %d" % temp)
			    if (Gateway[f]['no'] <= Gateway[t]['no']): 
                            	command = "curl -s http://%s/wm/topology/route/%s/%s/%s/%s/json" % (controllerRestIp, dpid, ingressPort, destSwitch, destPort)
				log_debug("555")
			    else:
			
				command = "curl -s http://%s/wm/topology/route/%s/%s/%s/%s/json" % (controllerRestIp, destSwitch, destPort,dpid,ingressPort)
				log_debug("666")
			    #print command + "\n"
			    #add by linpp
			    log_debug("command111:")
			    log_debug(command)
			    #end add by linpp
                            result = os.popen(command).read()
			    #print result + "\n"
                            parsedResult = json.loads(result)
                            #del by linpp
			    #if range(len(parsedResult)) < 2:
                            #    log_error("Can't find route")
                            #else:
                            #    egressPort = parsedResult[1]['port']
			    #end del by linpp
			    #add by linpp
                            log_debug("result:")
                            log_debug(result)
			    if (Gateway[f]['no'] <= Gateway[t]['no']):
			    	egressPort = parsedResult['flowEntries'][0]['outPort']['value']
			    else:
				for f in parsedResult['flowEntries']:
					if (f['dpid']['value'] == dpid):
			        		egressPort = f['inPort']['value']
			    print "egressPort1: (%s)" % (egressPort)
			    #end add by linpp
                            name = "prefix" + "_" + dpid + "_" + dst_subnet
                            command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-mac\":\"%s\", \"ether-type\":\"%s\", \"dst-ip\":\"%s\", \"cookie\":\"0\", \"priority\":\"32767\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"set-dst-mac=%s,output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (dpid, dpid+"."+name, smac, "0x800", dst_subnet, ingressPort, new_dmac, egressPort, controllerRestIp)
                            log_debug("Prefix: source GW %s smac %s prefix %s nexthop %s sw %s inport %s outport %s rewrite %s" % (s_ip, smac, dst_subnet, dst_ip, dpid, ingressPort, egressPort, new_dmac))
			    log_debug("Mac-rewrite-command: %s" % command)
			    result = os.popen(command).read()

                            log_debug("Prefix: source GW %s smac %s prefix %s nexthop %s sw %s inport %s outport %s rewrite %s" % (s_ip, smac, dst_subnet, dst_ip, dpid, ingressPort, egressPort, new_dmac))

                        else:
                            log_error("Can't resolve next hop IP's  MAC GW %s prefix %s nexthop %s\n" % (s_ip, dst_subnet, dst_ip))
        except:
            pass

def install_routes ( type ):
    for fmGw in Gateway: 
        for toGw in Gateway:
	    if (Gateway[fmGw]['no'] < Gateway[toGw]['no']):
	    
	     
	    	if ( (Gateway[fmGw]['ipv4'] != Gateway[toGw]['ipv4']) and (Gateway[fmGw]['as'] != Gateway[toGw]['as'])):
                	sourceSwitch = Gateway[fmGw]['switch']
                	sourcePort = Gateway[fmGw]['port']
                	smac = Gateway[fmGw]['mac']

                	destSwitch = Gateway[toGw]['switch']
                	destPort = Gateway[toGw]['port']
                	dmac = Gateway[toGw]['mac']
		
                	command = "curl -s http://%s/wm/topology/route/%s/%s/%s/%s/json" % (controllerRestIp, sourceSwitch, sourcePort, destSwitch, destPort)
                	log_debug (command)
                	try: 
                    		result = os.popen(command).read()
                	except:
                    		continue
			#add by linpp
			log_debug ("result-linpp:")
                	log_debug (result)
			#flow_id = {}
			#flow_id['value'] = 5
			#flow_path = {}
  			#flow_path['flowId'] = flow_id
  		
			#flow_path['dataPath'] = result
			#flow_path_json = json.dumps(flow_path)
			#log_debug("flow_path_json:")
			#log_debug(flow_path_json)
			#command = "curl -s -H 'Content-Type: application/json' -d '%s' http://%s/wm/flow/add/json" % (flow_path_json,controllerRestIp)
 
	#		command = 
	#		{"flowId": {"value": 5}, "dataPath": "{\"srcPort\":{\"dpid\":{\"value\":\"00:00:00:00:00:00:00:a6\"},\"port\":{\"value\":3}},\"dstPort\":{\"dpid\":{\"value\":\"00:00:00:00:00:00:00:a2\"},\"port\":{\"value\":3}},\"flowEntries\":[{\"flowEntryId\":null,\"flowEntryMatch\":null,\"flowEntryActions\":null,\"dpid\":{\"value\":\"00:00:00:00:00:00:00:a6\"},\"inPort\":{\"value\":3},\"outPort\":{\"value\":1},\"flowEntryUserState\":\"FE_USER_UNKNOWN\",\"flowEntrySwitchState\":\"FE_SWITCH_UNKNOWN\",\"flowEntryErrorState\":null},{\"flowEntryId\":null,\"flowEntryMatch\":null,\"flowEntryActions\":null,\"dpid\":{\"value\":\"00:00:00:00:00:00:00:a4\"},\"inPort\":{\"value\":3},\"outPort\":{\"value\":1},\"flowEntryUserState\":\"FE_USER_UNKNOWN\",\"flowEntrySwitchState\":\"FE_SWITCH_UNKNOWN\",\"flowEntryErrorState\":null},{\"flowEntryId\":null,\"flowEntryMatch\":null,\"flowEntryActions\":null,\"dpid\":{\"value\":\"00:00:00:00:00:00:00:a2\"},\"inPort\":{\"value\":2},\"outPort\":{\"value\":3},\"flowEntryUserState\":\"FE_USER_UNKNOWN\",\"flowEntrySwitchState\":\"FE_SWITCH_UNKNOWN\",\"flowEntryErrorState\":null}]}"}
			#command = "curl -s -H 'Content-Type: application/json' -d '{\"srcPort\":{\"dpid\":{\"value\":\"00:00:00:00:00:00:00:a6\"},\"port\":{\"value\":3}},\"dstPort\":{\"dpid\":{\"value\":\"00:00:00:00:00:00:00:a2\"},\"port\":{\"value\":3}},\"flowEntries\":[{\"flowEntryId\":null,\"flowEntryMatch\":null,\"flowEntryActions\":null,\"dpid\":{\"value\":\"00:00:00:00:00:00:00:a6\"},\"inPort\":{\"value\":3},\"outPort\":{\"value\":1},\"flowEntryUserState\":\"FE_USER_UNKNOWN\",\"flowEntrySwitchState\":\"FE_SWITCH_UNKNOWN\",\"flowEntryErrorState\":null},{\"flowEntryId\":null,\"flowEntryMatch\":null,\"flowEntryActions\":null,\"dpid\":{\"value\":\"00:00:00:00:00:00:00:a4\"},\"inPort\":{\"value\":3},\"outPort\":{\"value\":1},\"flowEntryUserState\":\"FE_USER_UNKNOWN\",\"flowEntrySwitchState\":\"FE_SWITCH_UNKNOWN\",\"flowEntryErrorState\":null},{\"flowEntryId\":null,\"flowEntryMatch\":null,\"flowEntryActions\":null,\"dpid\":{\"value\":\"00:00:00:00:00:00:00:a2\"},\"inPort\":{\"value\":2},\"outPort\":{\"value\":3},\"flowEntryUserState\":\"FE_USER_UNKNOWN\",\"flowEntrySwitchState\":\"FE_SWITCH_UNKNOWN\",\"flowEntryErrorState\":null}]}' http://%s/wm/flow/add/json" % (controllerRestIp)
  		
			#log_debug("add_flow_path: %s" % command)
    			#result = os.popen(command).read()
    			#log_debug("result: %s" % result)
			#end add by linpp
                	parsedResult = json.loads(result)


                	log_debug ( "Static Route %s (%s %s) -> %s (%s %s)" % (fmGw, sourceSwitch, sourcePort, toGw, destSwitch, destPort) )
		
			#del by linpp
                	#for i in range(len(parsedResult)):
          	       #   if i % 2 == 0:
                	  #      dpid1 = parsedResult[i]['switch']
                	   #     ingressPort = parsedResult[i]['port']
            
                   	 #else:
                    	 #   dpid2 = parsedResult[i]['switch']
                          #  egressPort = parsedResult[i]['port']
              
                      	 # if dpid2 != dpid1:
                        #    log_error( "dpid does not match")
                       	# else:
                        #    dpid = dpid1
			#end del by linpp
			#add by linpp
			srcSwitch = parsedResult['srcPort']['dpid']['value'];
			srcPort = parsedResult['srcPort']['port']['value'];
  			dstSwitch = parsedResult['dstPort']['dpid']['value'];
  			dstPort = parsedResult['dstPort']['port']['value'];

  			print "DataPath: (src = %s/%s dst = %s/%s)" % (srcSwitch, srcPort, dstSwitch, dstPort);
			for f in parsedResult['flowEntries']:
                		ingressPort = f['inPort']['value'];
                		egressPort = f['outPort']['value'];
    				dpid = f['dpid']['value']
    				print "FlowEntry: (%s, %s, %s)" % (ingressPort, dpid, egressPort)

			#end add by linpp

                            # send one flow mod per pair of APs in route
                            # using StaticFlowPusher rest API

                            # IMPORTANT NOTE: current Floodlight StaticflowEntryPusher
                            # assumes all flow entries to have unique name across all switches
                            # this will most possibly be relaxed later, but for now we
                            # encode each flow entry's name with both switch dpid, src_mac, dst_mac

				command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-mac\":\"%s\", \"dst-mac\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (dpid, dpid+"."+fmGw+"."+toGw, smac, dmac, "0x800", ingressPort, egressPort, controllerRestIp)
                		result = os.popen(command).read()

                		log_debug( "   dpid %s in_port %s outport %s" % (dpid, ingressPort, egressPort))
				
				command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-mac\":\"%s\", \"dst-mac\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (dpid, dpid+"."+toGw+"."+fmGw, dmac, smac, "0x800", egressPort, ingressPort, controllerRestIp)
                                
				result = os.popen(command).read()
				log_debug("999")
				log_debug("Route_command:%s" % command)
                                log_debug( "   dpid %s in_port %s outport %s" % (dpid, egressPort, ingressPort))
				


if __name__ == "__main__":
    initialize()
    app.run(host="0.0.0.0", port=5001)
