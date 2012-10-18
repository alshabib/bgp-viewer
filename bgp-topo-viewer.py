#!/usr/bin/env python2.7

import argparse
import json, sys, threading, os, time
import urllib2
import SimpleHTTPServer, SocketServer

FL_TOPO = "/wm/topology/links/json"
FL_SWS = "/wm/core/controller/switches/json"
FL_FLOWS= "/wm/core/switch/all/flow/json"

NON_SDN_AS = [ {"group" : -1, "name" : "AS1" },   {"group" : -1, "name" : "AS2" }, {"group" : -1, "name" : "AS3" } ]

NON_OF_FLOW = {"00:00:00:00:00:00:00:a4:2" : (["AS1"],'00:00:00:00:00:00:00:b4',2), "00:00:00:00:00:00:00:a5:2" : (["AS2", "AS3"],'00:00:00:00:00:00:00:b5',2), \
                "00:00:00:00:00:00:00:b4:2" : (["AS1"],'00:00:00:00:00:00:00:a4',2), "00:00:00:00:00:00:00:b5:2" : (["AS3", "AS2"],'00:00:00:00:00:00:00:a5',2)}

DESC = "Collects topology and other information from Floodlight and exposes it over a webserver"

# Parse command line arguments
parser = argparse.ArgumentParser(prog='bgp-topo-viewer', description=DESC)
parser.add_argument('-v', '--verbose', action="store_true", help="debug output", default=False)
parser.add_argument('-s', '--simple', action="store_true", help="Send bare essentials to D3", default=False)
parser.add_argument('-p', '--httpport', type=int, help="http server port", default=8000)
parser.add_argument('-t', '--httphost', help='host on which the http server runs', default='localhost')
parser.add_argument('-u', '--update', type=int, help='Interval to update flows', default='2')
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
    try:
        response = urllib2.urlopen(request)
        resp_text =  response.read()
    except Exception as e:
        print "Exception on url %s" % url, e
        sys.exit(1)  
    return json.loads(resp_text)

def d3ize(sws, topo):
    d3_dict = {}
    if args.simple:
        nodes = NON_SDN_AS
        node_index = ["AS1", "AS2", "AS3"]
        for group in range(len(sws)):
            nodes = nodes + [ { "group" : group, "name" : sw['dpid'] } for sw in sws[group] ]
            node_index = node_index + [ sw['dpid'] for sw in sws[group] ] 
        d3_dict['nodes'] = nodes
        debug(node_index)
        links = [ { "source" : node_index.index(link["src-switch"]), "target" : node_index.index(link["dst-switch"]) } for link in topo ]
        links.append({"source" : node_index.index("00:00:00:00:00:00:00:a4"), "target" : node_index.index("AS1") })
        links.append({"target" : node_index.index("00:00:00:00:00:00:00:b4"), "source" : node_index.index("AS1") })
        links.append({"source" : node_index.index("00:00:00:00:00:00:00:a5"), "target" : node_index.index("AS2") })
        links.append({"source" : node_index.index("AS2"), "target" : node_index.index("AS3") })
        links.append({"source" : node_index.index("AS3"), "target" : node_index.index("00:00:00:00:00:00:00:b5") })

        d3_dict["links"] = links     
    else:
        pass
        # send all info you got
    debug(json.dumps(d3_dict, indent=2))
    return (node_index, d3_dict)


def buildTopoHash(topo):
    thash = {}
    for conn in topo:
        if conn['src-switch'] not in thash:
            thash[conn['src-switch']] = {}
        thash[conn['src-switch']][conn['src-port']] = ( conn['dst-switch'] , conn['dst-port'] )

        if conn['dst-switch'] not in thash:
            thash[conn['dst-switch']] = {}
        thash[conn['dst-switch']][conn['dst-port']] = ( conn['src-switch'] , conn['src-port'] )


    debug(thash)
    return thash
        
def determineSourceFlows(flows, thash):
    srcs = {}
    for dpid, flowEntries in flows.items():
         entries = []
         for fe in flowEntries:
             try:
                 thash[dpid][fe['match']['inputPort']]
             except KeyError as e:
                 entries.append(fe)
         srcs[dpid] = entries
    return srcs

def findNextHop(flows, nextHop, inport):
    for fe in flows[nextHop]:
         if fe['match']['inputPort'] == inport:
             for f in fe['actions']:
                 if f['type'] == 'OUTPUT':
                     return (nextHop, f['port']) 
    return (None, None)

def findFlowPaths(flows, thash):
    sources = determineSourceFlows(flows, thash)
    paths = []
    for dpid, flowEntries in sources.items():
        for fe in flowEntries:
            path = []
            path.append(dpid)
            port = -1
            for f in fe['actions']:
                if f['type'] == 'OUTPUT':
                    port = f['port']
                else:
                    continue
            dp = dpid
            while True:
                if NON_OF_FLOW.has_key("%s:%s" % (dp, port)):
                   (ases, dp, port) = NON_OF_FLOW['%s:%s' % (dp,port)]
                   path.append(ases)
                   path.append(dp)
                   path = flatten(path)
                   (dp,port) = findNextHop(flows, dp, port)

                try:
                    (nextHop,inport) = thash[dp][port] 
                except KeyError as e:
                    break
                path.append(nextHop)
                (dp, port) = findNextHop(flows, nextHop, inport)
                   
            paths.append(path)
    debug("Paths found %s" % paths)
    return paths
    
class TopoFetcher():
    def __init__(self, args):
        self.servers = args.servers
        self.debug = args.verbose
        HTTPHandler.topo = self.getTopo
        self.cv = threading.Condition()
        self.fcv = threading.Condition()
        self.flowupdateEvent = threading.Event()
        self.flowupdate = threading.Thread(target=self.update_flows)
        self.fetch_topology() 
        self.fetch_flows()
        self.httpd = TCPServer((args.httphost, args.httpport), HTTPHandler)
        try:
            debug("Starting flow update thread")
            self.flowupdate.start()
            debug("Firing up HTTP server, now serving forever on host %s and port %s" \
                                        % (args.httphost,args.httpport) )
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            debug("Stopping flow update thread")
            self.flowupdateEvent.set()
            debug("Shutdown http server")
    
    def getTopo(self):
        debug("Pointing webserver topo to Topo class")
        return self


    def update_flows(self):
        while not self.flowupdateEvent.is_set():
            self.fetch_flows()
            time.sleep(args.update)

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
            self.d3_dict = None
            (self.node_index, self.d3_dict) = d3ize(sws, topo)
            self.cv.notify()
            self.cv.release()

    def fetch_flows(self):
        topo = []
        fls = []
        self.flow_paths = None
        for server in self.servers:
            url = "http://%s%s" % (server, FL_TOPO)
            topo = topo + do_url(url)
            url = "http://%s%s" % (server, FL_FLOWS)
            fls.append(do_url(url))
        flows = dict(fls.pop(0),**fls.pop(0))
        for fl in fls:
            flows = dict(flows, **fl)     
        debug("Obtained flow info")
        if len(topo) > 0 and isTraffic(flows) > 0:
            fls = []
            for flow in findFlowPaths(flows, buildTopoHash(topo)):
                fls.append(map(lambda x: self.node_index.index(x), flow))
            self.fcv.acquire()
            self.flow_paths = None
            self.flow_paths = fls  
            self.fcv.notify()
            self.fcv.release()

    def getTopology(self):
        self.cv.acquire()
        while self.d3_dict == None:
            self.cv.wait()
        topo = self.d3_dict
        self.cv.release()
        return topo

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
            self.fcv.wait()
        flows = self.flow_paths
        self.fcv.release()
        return flows


class HTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def send_resp(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2))

    def do_GET(self):
        if self.path.startswith("/topology"):
            resp = self.topo().getTopology()
            debug("Sending to d3: %s" % resp)
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
        if self.path.startswith("/listdevices"):
            self.send_resp(self.topo().getDevices())
            return
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        pass

    def topo(self):
        pass



class TCPServer(SocketServer.TCPServer):
    allow_reuse_address = True



if __name__ == "__main__":
    TopoFetcher(args)
