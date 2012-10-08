#!/usr/bin/env python2.7

import argparse
import json, sys, threading, os
import urllib2
import SimpleHTTPServer, SocketServer


FL_TOPO = "/wm/topology/links/json"
FL_SWS = "/wm/core/controller/switches/json"

NON_SDN_AS = [ {"group" : -1, "name" : "AS1" },   {"group" : -1, "name" : "AS2" }, {"group" : -1, "name" : "AS3" } ]


DESC = "Collects topology and other information from Floodlight and exposes it over a webserver"

# Parse command line arguments
parser = argparse.ArgumentParser(prog='bgp-topo-viewer', description=DESC)
parser.add_argument('-v', '--verbose', action="store_true", help="debug output", default=False)
parser.add_argument('-s', '--simple', action="store_true", help="Send bare essentials to D3", default=False)
parser.add_argument('-p', '--httpport', type=int, help="http server port", default=8000)
parser.add_argument('-t', '--httphost', help='host on which the http server runs', default='localhost')
parser.add_argument('servers', help="list of floodlights with format SRV:PORT", nargs=argparse.REMAINDER)
args = parser.parse_args()

for s in args.servers:
    if not ":" in s:
        print "Server list must be supplied in the SRV:PORT format"
        parser.print_help()
        sys.exit(0)

def debug(msg):
    if args.verbose:
        print msg

def do_url(url):
    request = urllib2.Request(url, None, {'Content-Type':'application/json'})
    try:
        response = urllib2.urlopen(request)
        resp_text =  response.read()
    except Exception as e:
        print "Exception:", e
        return []
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
        links.append({"target" : node_index.index("00:00:00:00:00:00:00:b1"), "source" : node_index.index("AS1") })
        links.append({"source" : node_index.index("00:00:00:00:00:00:00:a5"), "target" : node_index.index("AS2") })
        links.append({"source" : node_index.index("AS2"), "target" : node_index.index("AS3") })
        links.append({"source" : node_index.index("AS3"), "target" : node_index.index("00:00:00:00:00:00:00:b2") })

        d3_dict["links"] = links     
    else:
        pass
        # send all info you got
    debug(json.dumps(d3_dict, indent=2))
    return d3_dict


class TopoFetcher():
    def __init__(self, args):
        self.servers = args.servers
        self.debug = args.verbose
        HTTPHandler.topo = self.getTopo
        self.cv = threading.Condition()
        self.fetch_topology() 
        self.httpd = TCPServer((args.httphost, args.httpport), HTTPHandler)
        try:
            debug("Firing up HTTP server, now serving forever on host %s and port %s" \
                                        % (args.httphost,args.httpport) )
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            debug("Shutdown http server") 
    
    def getTopo(self):
        debug("Pointing webserver topo to Topo class")
        return self


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
            self.d3_dict = d3ize(sws, topo)
            self.cv.notify()
            self.cv.release()
    
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
