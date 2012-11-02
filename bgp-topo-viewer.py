#!/usr/bin/env python2.7

import argparse,copy
import json, sys, threading, os, time
import urllib2, urlparse
import SimpleHTTPServer, SocketServer

FL_TOPO = "/wm/topology/links/json"
FL_SWS = "/wm/core/controller/switches/json"
FL_FLOWS = "/wm/core/switch/all/flow/json"
FL_BGP = "/wm/bgp/json"

NON_SDN_AS = [ {"group" : 0, "name" : 'host' }, {"group" : -1, "name" : "AS2" },   {"group" : -2, "name" : "AS3" }, {"group" : -3, "name" : "AS4" } ]

NON_OF_FLOW = {"00:00:00:00:00:00:00:a3:4" : (["AS2"],'00:00:00:00:00:00:00:a5',3), "00:00:00:00:00:00:00:a2:3" : (["AS3", "AS4"],'00:00:00:00:00:00:00:a6',3), \
                "00:00:00:00:00:00:00:a5:3" : (["AS2"],'00:00:00:00:00:00:00:a3',4), "00:00:00:00:00:00:00:a6:3" : (["AS4", "AS3"],'00:00:00:00:00:00:00:a2',3)}

FAKES = [ {"source" : "00:00:00:00:00:00:00:a3", "target" : "AS2" },
          {"target" : "00:00:00:00:00:00:00:a5", "source" : "AS2" },
          {"source" : "00:00:00:00:00:00:00:a2", "target" : "AS3" },
          {"source" : "AS3", "target" : "AS4" },
          {"source" : "AS4", "target" : "00:00:00:00:00:00:00:a6" },
          {"source" : "host", "target" : "00:00:00:00:00:00:00:a1" }]


DESC = "Collects topology and other information from Floodlight and exposes it over a webserver"

# Parse command line arguments
parser = argparse.ArgumentParser(prog='bgp-topo-viewer', description=DESC)
parser.add_argument('-v', '--verbose', action="store_true", help="debug output", default=False)
parser.add_argument('-s', '--simple', action="store_true", help="Send bare essentials to D3", default=False)
parser.add_argument('-p', '--httpport', type=int, help="http server port", default=8000)
parser.add_argument('-t', '--httphost', help='host on which the http server runs', default='localhost')
parser.add_argument('-u', '--update', type=int, help='Interval to update flows', default='2')
parser.add_argument('-f', '--filter', help='JSON filter to filter flows on', 
                default="[ { 'networkDestination' : '172.16.20.0' }, { 'networkDestination' : '172.16.30.0' }]")
parser.add_argument('servers', help="list of floodlights with format SRV:PORT",nargs=argparse.REMAINDER)
args = parser.parse_args()

for s in args.servers:
    if not ":" in s:
        print "Server list must be supplied in the SRV:PORT format"
        parser.print_help()
        sys.exit(0)


def flatten(l, ltypes=(list, tuple)):
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)

def treeize(data, dpid):
    tree = { 'name' : dpid, 'children' : []}
    
    for j,fe in enumerate(data):
        baseElem = []
        matchElem = []
        actionElem = []
        for key,value in fe.items():
            if key == 'match':
                for k,v in value.items():
                    matchElem.append( {'name' : "%s : %s" % (k,v) })
            elif key == 'actions':
                for i,val in enumerate(value):
                    subact = []
                    for k,v in val.items():
                        subact.append({ 'name' : "%s : %s" % (k, v) })
                    actionElem.append({ 'name' : i+1, 'children' : subact })
            else:
                baseElem.append( { 'name' : "%s : %s" % (key, value) } )    
        base = { 'name' : 'base', 'children' : baseElem }
        match = { 'name' : 'match', 'children' : matchElem }
        actions = { 'name' : 'actions', 'children' : actionElem }
        tree['children'].append({ 'name' : j + 1, 'children' : [ base, match, actions ] })
    if len(tree['children']) == 0:
        tree['children'].append({ 'name' : 'No Flow Entries' })
    return tree
        

def debug(msg):
    if args.verbose:
        print msg

def isTraffic(flows):
    for dpid,fes in flows.items():
        if len(fes) > 0:
            return True

    return False

def do_url(url):
    request = urllib2.Request(url, None, {'Content-Type':'application/json'})
    while True:
        try:
            response = urllib2.urlopen(request)
            resp_text =  response.read()
            break
        except Exception as e:
            debug("%s on url %s, waiting 2 secs" % (e, url))
            time.sleep(2)
            #sys.exit(1)  
    return json.loads(resp_text)

def d3ize(sws, topo, fake_links):
    d3_dict = {}
    if args.simple:
        nodes = NON_SDN_AS
        node_index = ["host", "AS2", "AS3", "AS4"]
        for group in range(len(sws)):
            nodes = nodes + [ { "group" : group, "name" : sw['dpid'] } for sw in sws[group] ]
            node_index = node_index + [ sw['dpid'] for sw in sws[group] ] 
        d3_dict['nodes'] = nodes
        links = [ { "source" : node_index.index(link["src-switch"]), "target" : node_index.index(link["dst-switch"]) } for link in topo ]
        for i, l in enumerate(FAKES):
            if (i+1) in fake_links:
                link = copy.copy(l)
                link['source'] = node_index.index(link['source'])
                link['target'] = node_index.index(link['target'])
                links.append(link)
        d3_dict["links"] = links     
    else:
        pass
        # send all info you got
    return (node_index, d3_dict)

def fromAS(dpid, fe):
    if NON_OF_FLOW.has_key('%s:%s' % (dpid, fe['match']['inputPort'])):
        (AS, dp, port) = NON_OF_FLOW['%s:%s' % (dpid, fe['match']['inputPort'])]
        return (AS[0], True)
    return (None, False)

def isA1(value):
    if value == '00:00:00:00:00:00:00:a1':
        return True
    return False

def buildTopoHash(topo):
    thash = {}
    for conn in topo:
        if conn['src-switch'] not in thash:
            thash[conn['src-switch']] = {}
        thash[conn['src-switch']][conn['src-port']] = ( conn['dst-switch'] , conn['dst-port'] )

        if conn['dst-switch'] not in thash:
            thash[conn['dst-switch']] = {}
        thash[conn['dst-switch']][conn['dst-port']] = ( conn['src-switch'] , conn['src-port'] )


    return thash
        
def determineSourceFlows(flows, thash):
    srcs = {}
    for dpid, flowEntries in flows.items():
         entries = []
         for fe in flowEntries:
             if fe['packetCount'] == 0:
                continue
             try:
                 thash[dpid][fe['match']['inputPort']]
             except KeyError as e:
                 entries.append(fe)
         srcs[dpid] = entries
    return srcs

def findNextHop(flows, nextHop, inport, dl_dst):
    for fe in flows[nextHop]:
         if fe['packetCount'] == 0:
             continue
         if fe['match']['inputPort'] == inport and fe['match']['dataLayerDestination'] == dl_dst:
             for f in fe['actions']:
                 if f['type'] == 'OUTPUT':
                    return (nextHop, f['port']) 
    return (None, None)

def passFilter(filt, fe, dpid):
    if filt == 'all':
        return True
    if filt == 'None':
        return False
    ret = False
    for rule in filt:
        attrs = True
        for key, value in rule.items():
            if key == 'dpid':
                if value == dpid:
                    continue
                else:
                    attrs = False
                    break
            if fe['match'][key] != value:
                attrs = False
                break
        ret = ret | attrs
    return ret

ENDS = { '172.16.20.0' : 'AS2', '172.16.30.0' : 'AS3', '172.16.40.0' : 'AS4' }


def findEndingAS(ip):
    if ENDS.has_key(ip):
        return ENDS[ip]
    else:
        return None

def findFlowPaths(flows, thash, filt = 'None'):
    sources = determineSourceFlows(flows, thash)
    paths = []
    if len(sources.keys()) == 0:
        return paths
    for dpid, flowEntries in sources.items():
        for fe in flowEntries:
            if (not passFilter(filt, fe, dpid)):
                continue
            path = []
            (AS, truth) = fromAS(dpid, fe)
            if truth:
                path.append(AS)
            path.append(dpid)
            port = -1
            dl_dst = None
            ip_dst = fe['match']['networkDestination']
            fAS = findEndingAS(ip_dst)
            for f in fe['actions']:
                if f['type'] == 'OUTPUT':
                    port = f['port']
                elif f['type'] == 'SET_DL_DST':
                    dl_dst = f['dataLayerAddress']
                else:
                    continue
            dp = dpid
            F_NON_OF = False
            while True:
                F_NON_OF = False
                if NON_OF_FLOW.has_key("%s:%s" % (dp, port)):
                   (ases, dp, port) = NON_OF_FLOW['%s:%s' % (dp,port)]
                   path.append(ases)
                   path.append(dp)
                   path = flatten(path)
                   (dp,port) = findNextHop(flows, dp, port, dl_dst)
                   F_NON_OF = True
                try:
                    (nextHop,inport) = thash[dp][port] 
                except KeyError as e:
                    if F_NON_OF and len(path) > 0:
                        path.pop()
                    break
                path.append(nextHop)
                (dp, port) = findNextHop(flows, nextHop, inport, dl_dst)
            while len(path) > 0 and fAS != None and path[-1] != fAS:
                path.pop()
            if (isA1(path[0])):
                path = ['host'] + path;
            if (isA1(path[-1])):
                path.append('host')
            paths.append(path)
    return paths
    
class TopoFetcher():
    def __init__(self, args):
        self.servers = args.servers
        self.debug = args.verbose
        HTTPHandler.topo = self.getTopo
        self.cv = threading.Condition()
        self.fcv = threading.Condition()
        self.filtcv = threading.Condition()
        self.filt = eval(args.filter)
        self.fake_links = range(1,len(FAKES)+1)
        self.flowupdateEvent = threading.Event()
        self.topoupdateEvent = threading.Event()
        self.flowupdate = threading.Thread(target=self.update_flows)
        self.topoupdate = threading.Thread(target=self.update_topo)
        self.fetch_topology() 
        self.fetch_flows()
        self.httpd = TCPServer((args.httphost, args.httpport), HTTPHandler)
        try:
            debug("Starting flow update thread")
            self.flowupdate.start()
            debug("Starting topology update thread")
            self.topoupdate.start()
            debug("Firing up HTTP server, now serving forever on host %s and port %s" \
                                        % (args.httphost,args.httpport) )
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            debug("Stopping flow update thread")
            self.flowupdateEvent.set()
            self.topoupdateEvent.set()
            debug("Shutdown http server")
    
    def getTopo(self):
        return self

    def update_topo(self):
        while not self.topoupdateEvent.is_set():
            self.fetch_topology()
            time.sleep(args.update)

    def update_flows(self):
        try:
            while not self.flowupdateEvent.is_set():
                self.fetch_flows()
                time.sleep(args.update)
        except Exception, e:
            debug(e)

    def fetch_topology(self):
        topo = []
        sws = []
        for server in self.servers:
            url = "http://%s%s" % (server, FL_TOPO)
            debug("Fetching Topo info from %s" % url)
            topo = topo + do_url(url)
            url = "http://%s%s" % (server, FL_SWS)
            debug("Fetching devices info from %s" % url)
            sws.append(do_url(url))
        if (len(topo) > 0 and len(sws) > 0):
            self.cv.acquire()
            topo.sort()
            self.d3_dict = None
            (self.node_index, self.d3_dict) = d3ize(sws, topo, self.fake_links)
            self.cv.notify()
            self.cv.release()

    def fetch_flows(self):
        topo = []
        fls = []
        bgps = []
        for server in self.servers:
            url = "http://%s%s" % (server, FL_TOPO)
            topo = topo + do_url(url)
            url = "http://%s%s" % (server, FL_FLOWS)
            fls.append(do_url(url))
            url = "http://%s%s" % (server, FL_BGP)
            bgps.append(do_url(url))
        if len(fls) == 1:
            flows = fls.pop(0)
        else:
            flows = dict(fls.pop(0),**fls.pop(0))
            for fl in fls:
                flows = dict(flows, **fl)     
        debug("Obtained flow info")
        if len(topo) > 0 and isTraffic(flows) > 0:
            fls = []
            for flow in findFlowPaths(flows, buildTopoHash(topo), filt = self.getFilter()):
                fls.append(map(lambda x: self.node_index.index(x), flow))
            self.fcv.acquire()
            self.flow_paths = None
            self.bgps = None
            self.flowtables = None
            self.flow_paths = fls
            self.flowtables = flows
            self.bgps = bgps  
            self.fcv.notify()
            self.fcv.release()

    def uplink(self, no):
        linkno = int(no)
        if linkno > 0 and linkno <= len(FAKES):
            self.cv.acquire()
            while self.d3_dict == None:
                self.cv.wait()
            if linkno not in self.fake_links:
                self.fake_links.append(linkno)
            self.cv.release()
            return True
        else:
            return False

    def downlink(self, no):
        linkno = int(no)
        if linkno > 0 and linkno <= len(FAKES):
            self.cv.acquire()
            while self.d3_dict == None:
                self.cv.wait()
            if linkno in self.fake_links:
                self.fake_links.remove(linkno)
            self.cv.release()
            return True
        else:
            return False


    def getTopology(self):
        self.cv.acquire()
        while self.d3_dict == None:
            self.cv.wait()
        topo = self.d3_dict
        self.cv.release()
        return topo

    def getFlowTables(self, dpid):
        self.fcv.acquire()
        while self.flowtables == None:
            self.fcv.wait()
        if dpid in self.flowtables:
            flows = self.flowtables[dpid]
        else: flows = []
        self.fcv.release()
        return flows

    def getDevices(self):
        self.cv.acquire()
        while self.d3_dict == None:
            self.cv.wait()
        sws = self.d3_dict['nodes']
        self.cv.release()
        return sws
    
    def getFlows(self):
        self.fcv.acquire()
        while self.flow_paths == None:
            debug("Waiting for flows")
            self.fcv.wait()
        flows = self.flow_paths
        self.fcv.release()
        return flows

    def getBGP(self, bgp):
        self.fcv.acquire()
        while self.bgps == None:
            debug("Waiting for flows")
            self.fcv.wait()
        bgps = self.bgps
        self.fcv.release()
        return bgps[bgp]

    def setFilter(self, filt):
        debug("Filter is %s" % filt) 
        self.filtcv.acquire()
        self.filt = filt
        self.filtcv.release()
    

    def getFilter(self):
        self.filtcv.acquire()
        filt =  self.filt
        self.filtcv.release()
        return filt



class HTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def send_resp(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2))

    def do_GET(self):
        if self.path.startswith("/flowtable"):
            dpid = self.path.split('/')[-1];
            resp = treeize(self.topo().getFlowTables(dpid), dpid)
            if resp != None:
                self.send_resp(resp)
            else:
                self.send_response(404)
            return
        if self.path.startswith("/downlink"):
            linkno = self.path.split('/')[-1]
            resp = self.topo().downlink(linkno)
            self.send_resp(resp)
            return
        if self.path.startswith("/uplink"):
            linkno = self.path.split('/')[-1]
            resp = self.topo().uplink(linkno)
            self.send_resp(resp)
            return
        if self.path.startswith("/topology"):
            resp = self.topo().getTopology()
            if resp != None:
                self.send_resp(resp)
            else:
                self.send_response(404)
            return
        if self.path.startswith("/flows"):
            resp = self.topo().getFlows()
            debug("Sending flow paths to d3 : %s" % resp)
            if resp != None:
                self.send_resp(resp)
            else:
                self.send_reponse(404)
            return
        if self.path.startswith("/bgp1"):
            resp = self.topo().getBGP(0)
            debug("Sending BGP1 info -> %s" % resp)
            if resp != None:
                self.send_resp(resp)
            else:
                self.send_reponse(404)
            return
        if self.path.startswith("/bgp2"):
            resp = self.topo().getBGP(1)
            if resp != None:
                self.send_resp(resp)
            else:
                self.send_reponse(404)
            return
        if self.path.startswith("/listdevices"):
            self.send_resp(self.topo().getDevices())
            return
        
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path.startswith("/filter"):
            length = int(self.headers.getheader('content-length'))        
            data_string = dict(urlparse.parse_qsl(self.rfile.read(length)))
            debug(data_string)
            data = eval(data_string['filter'])
            self.topo().setFilter(data)

    def topo(self):
        pass



class TCPServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True



if __name__ == "__main__":
    TopoFetcher(args)
