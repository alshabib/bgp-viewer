#!/usr/bin/env python2.7

import json,sys,threading,os
import SimpleHTTPServer, SocketServer
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from jsonrpc import ServiceProxy, JSONParam, proxy
import urllib2


IP="45.0.88.7"

class JSONParamEncoder(json.JSONEncoder):
    def default(self, obj):
      if isinstance(obj, JSONParam):
        return obj.getValueAsJson()
      elif isinstance(obj, FlowSpaceChangeRequest):
        return {'entry': obj.getEntry(), 'changeType': obj.getChangeType()}
      elif isinstance(obj, FlowSpaceEntry):
        ruleMatchStr = "OFMatch["
        for rule in obj.rules:
          ruleMatchStr = "%s%s=%s," % (ruleMatchStr, rule.key, rule.val)
        ruleMatchStr = ruleMatchStr[0:len(ruleMatchStr)-1] + "]"
        actionsList = []
        for action in obj.actions:
          actionDict = {}
          actionsList.append(actionDict)
          if action.type == 'Slice':
            actionDict['vendor'] = (1 - pow(2, 31))
          actionDict['type'] = "VENDOR"
          actionDict['length'] = 8
          actionDict['sliceName'] = action.key
          actionDict['slicePerms'] = action.val
        return {'id':obj.id, 'ruleMatch':ruleMatchStr, 'actionsList':actionsList, 'dpid':obj.dpid, 'priority':obj.priority}
      else:
        return json.JSONEncoder.default(self, obj)

class fv2d3():
    def __init__(self, user = "fvadmin", passw="0penfl0w", \
		host="flowvisor.openflow.interop.net", port = 9090, jsonport = 8081):
        self.id = -1
        self.cntstr = "https://%s:%s@%s:%d" % (user, passw, host, int(jsonport))
        self.serverport = port
        self.connect()
        self.initialize()
        self.registerCallbacks()
        self.httpd = TCPServer((IP, 8000), FVHTTPHandler)
        self.startservers()

    def nextid(self):
	self.id = self.id + 1
	return self.id

    def getFLLinks(self):
        url = 'http://45.0.88.7:8080/wm/topology/links/json'
        request = urllib2.Request(url, None, {'Content-Type':'application/json'}) 
        try:
            response = urllib2.urlopen(request)
            resp_text =  response.read()
        except:
            print "Exception:", e
        print resp_text
    #
    # Get the current state from FV
    #
    def initialize(self):
        self.ls = json.loads(self.fv.getLinks()['valueAsJson'])
        self.dev = json.loads(self.fv.listDevices()['valueAsJson'])
        self.slices = json.loads(self.fv.listSlices()['valueAsJson'])
        self.flowspace = json.loads(self.fv.listFlowSpace()['valueAsJson'])
	self.setHash()
        self.compute()

    def setHash(self):
	self.dev.sort()
	self.devices = []
	for d in self.dev:
		self.devices.append(d)
	self.links = []
	for link in self.ls:
		link["id"] = self.nextid()
		self.links.append(link)
	del self.dev
	del self.ls		

    def compute(self):
        self.buildSliceInfo()
        self.buildTopos()

    def buildSliceInfo(self):
	self.nodesPerSlice = { slice:[] for slice in self.slices }
	self.linksPerSlice = {}
	for fe in self.flowspace:
		slices = [ actions['sliceName'] for actions in fe['actionsList'] ]
		for slice in slices:
			inport = fe['ruleMatch']['inputPort']
			dpid = fe['dpid']
			if dpid == "all_dpids":
				break;
			if (dpid, inport) not in self.linksPerSlice:
				self.linksPerSlice[(dpid, inport)] = []
			self.linksPerSlice[(dpid, inport)].append(slice)
			if slice in self.nodesPerSlice.keys() and \
				dpid not in self.nodesPerSlice[slice]:
				self.nodesPerSlice[slice].append(dpid)				

    def buildTopos(self):
        self.sliceTopos = { slice:[] for slice in self.slices} 
        for link in self.links:
            src = (link['srcDPID'], int(link['srcPort']))
            dst = (link['dstDPID'], int(link['dstPort']))
            try:
                for slice in self.linksPerSlice[src]:
                    if slice in self.linksPerSlice[dst] and \
				link not in self.sliceTopos[slice]:
                        self.sliceTopos[slice].append(link)
            except KeyError as inst:
		continue
                #print "KeyError on: %s" % inst
        self.convertTod3()

    def convertTod3(self):
        self.topos = {}
        self.topos['full'] = {}
        for slice in self.slices:
            self.topos[slice] = {}
	    self.topos[slice]['nodes'] = []
	    curr = {}
	    self.id = -1
	    for dev in self.nodesPerSlice[slice]:
		curr[dev] = self.nextid()
		self.topos[slice]['nodes'].append({"id" : curr[dev], "name" : dev })
            try:
                self.topos[slice]['links'] = [ {"source" :curr[link['srcDPID']],\
   
                                    "target" : curr[link['dstDPID']], \
                                    "value" : 0, "id" : link['id']} \
                                    for link in self.sliceTopos[slice] ]
            except Exception as inst:
                print "Error during slice topo build: %s" % inst
       
        try:
            self.topos['full']['nodes'] = [ {"id" : self.devices.index(dev), "name" : dev,  \
						"index" : self.devices.index(dev) } \
					 for dev in self.devices ]
            self.topos['full']['links'] = [ {"source" : self.devices.index(link['srcDPID']), \
                                    "target" : self.devices.index(link['dstDPID']), \
                                    "value" : 0, "id" : link['id'] } \
                                    for link in self.links ]
        except Exception as inst:
            print "Error duing full topo build: %s" % inst

    def contains(self, dpid, port, link):
        if (link['srcDPID'] == dpid and link['srcPort'] == port or
            link['dstDPID'] == dpid and link['dstPort'] == port):
            return True
        return False

    def removeLinkDevice(self, device):
        for link in self.links:
            if (link['srcDPID'] == device or link['dstDPID'] == device):
                try:
                    self.links.remove(link)
                except Exception as inst:
                    print "Error link remove from device: %s" % inst

    def removeLink(self, dpid, port):
        for link in self.links:
            if contains(dpid, port, link):
                self.links.remove(link)

    def removeFullLink(self, link):
	for l in self.links:
		if l['srcDPID'] == link['srcDPID'] and \
			l['srcPort'] == link['srcPort'] and \
			l['dstDPID'] == link['dstDPID'] and \
			l['dstPort'] == link['dstPort']:
			self.links.remove(l)
			return
    
    def connect(self):
        try:
            FVHTTPHandler.fv = self.getFV
            self.fv = ServiceProxy(self.cntstr, JSONParamEncoder)
        except:
            print "Connection to FlowVisor using %s failed" % self.cntstr
            sys.exit()

    def getFV(self):
        return self

    def registerCallbacks(self):
	host = "http://%s:9090" % IP
        self.fv.registerTopologyEventCallback(host, "deviceConnected", "DEVICE_CONNECTED")
        self.fv.registerTopologyEventCallback(host, "deviceDisconnected", "DEVICE_DISCONNECTED")
        self.fv.registerTopologyEventCallback(host, "portAdded", "PORT_ADDED")
        self.fv.registerTopologyEventCallback(host, "portRemoved", "PORT_REMOVED")
        self.fv.registerTopologyEventCallback(host, "linkup", "LINK_UP")
        self.fv.registerTopologyEventCallback(host, "linkdown", "LINK_DOWN")

    def deviceConnected(self, dev):
        device = dev['valueAsJson']
	print "Device %s came up" % device
        if device not in self.devices:
            self.devices.append(device)
        self.compute()

    def deviceDisconnected(self, dev):
        device = dev['valueAsJson']
        self.devices.remove(device)
	print "Device %s went down" % device
        self.removeLinkDevice(device)
        self.compute()

    def portAdded(self, dpid, port):
        p = port['valueAsJson']
        dp = dpid['valueAsJson']
	print "Port %s on %s was added" % (p, dp)
	

    def portRemoved(self, dpid, port):
        p = port['valueAsJson']
        dp = dpid['valueAsJson']
	print "Port %s on %s was removed" % (p, dp) 
        self.removeLink(dp, p)
        self.buildTopos()

   
    def linkup(self, linkad):
        l_up = json.loads(linkad['valueAsJson'])
        print "Link up %s" % l_up
	l_up['id'] = self.nextid()
	self.links.append(l_up)
        self.buildTopos()

    def linkdown(self, linkad):
        l_down = json.loads(linkad['valueAsJson'])
	print "link down %s" % l_down
        try:
            self.removeFullLink(l_down)
            self.buildTopos()
        except Exception as inst:
            print "Error while removing link: %s" % inst
        

    def slice(self,slicename):
        if slicename in self.topos:
            return self.topos[slicename]
        else:
            return None

    def startservers(self):
        server = SimpleJSONRPCServer((IP, self.serverport))
        server.register_function(self.deviceConnected)
        server.register_function(self.deviceDisconnected)
        server.register_function(self.portAdded)
        server.register_function(self.portRemoved)
        server.register_function(self.linkup)
        server.register_function(self.linkdown)


        try:
            self.fvthread = threading.Thread(target=server.serve_forever)
            print "Start callback server"
            self.fvthread.start()
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            server.shutdown()
            self.unregisterFromFV()
    
    def unregisterFromFV(self):
            self.fv.deregisterTopologyEventCallback("deviceConnected", "DEVICE_CONNECTED")
            self.fv.deregisterTopologyEventCallback("deviceDisconnected", "DEVICE_DISCONNECTED") 
            self.fv.deregisterTopologyEventCallback("portAdded", "PORT_ADDED")
            self.fv.deregisterTopologyEventCallback("portRemoved", "PORT_REMOVED")
            self.fv.deregisterTopologyEventCallback("linkup", "LINK_UP")
            self.fv.deregisterTopologyEventCallback("linkdown", "LINK_DOWN")
            self.httpd.shutdown()
            print "Cleanup done!"


class FVHTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def send_resp(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2))

    def do_GET(self):
        if self.path.startswith("/slice"):
            resp = self.fv().slice(self.path.split("/")[-1])
            if resp != None:
                self.send_resp(resp)
            else:
                self.send_response(404)
            return
        if self.path.startswith("/listslices"):
            self.send_resp(self.fv().slices)
            return
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        pass

    def fv(self):
        pass

class TCPServer(SocketServer.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    fv2d3()

