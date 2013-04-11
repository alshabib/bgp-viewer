#! /usr/bin/python

import os
import sys
import subprocess
import json
import argparse
import io
import time

from flask import Flask

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
    return "Hello, this is link.py!"

@app.route("/init")
def initialize():
    return "init command done\n"

@app.route("/link/1/down")
def topology_update1down():
    command = "sudo ifconfig tap0 down"
    log_debug (command)
    result = os.popen(command).read()
    log_debug (result)

    command = "curl -X GET http://sdn1vpc.onlab.us:8000/downlink/1"
    log_debug (command)
    result = os.popen(command).read()
    log_debug (result)

    time.sleep(2)
    command = "curl -X GET http://localhost:5001/topo_change"
    log_debug (command)
    result = os.popen(command).read()
    log_debug (result)
    return ""
@app.route("/link/1/up")
def topology_update1up():
    command = "sudo ifconfig tap0 up"
    log_debug (command)
    result = os.popen(command).read()
    log_debug (result)

    command = "curl -X GET http://sdn1vpc.onlab.us:8000/uplink/1"
    log_debug (command)
    result = os.popen(command).read()
    log_debug (result)

    time.sleep(2)
    command = "curl -X GET http://localhost:5001/topo_change"
    log_debug (command)
    result = os.popen(command).read()
    log_debug (result)
    return ""

@app.route("/link/2/down")
def topology_update2down():
    command = "sudo ifconfig tap2 down"
    log_debug (command)
    result = os.popen(command).read()
    log_debug (result)

    command = "curl -X GET http://sdn1vpc.onlab.us:8000/downlink/3"
    log_debug (command)
    result = os.popen(command).read()
    log_debug (result)

    time.sleep(2)
    command = "curl -X GET http://localhost:5001/topo_change"
    log_debug (command)
    result = os.popen(command).read()
    log_debug (result)
    return ""
@app.route("/link/2/up")
def topology_update2up():
    command = "sudo ifconfig tap2 up"
    log_debug (command)
    result = os.popen(command).read()
    log_debug (result)

    command = "curl -X GET http://sdn1vpc.onlab.us:8000/uplink/3"
    log_debug (command)
    result = os.popen(command).read()
    log_debug (result)

    time.sleep(2)
    command = "curl -X GET http://localhost:5001/topo_change"
    log_debug (command)
    result = os.popen(command).read()
    log_debug (result)
    return ""
@app.route("/link/3/down")
def topology_update3down():
    command = "sudo ifconfig sw5-eth2 down"
    log_debug (command)
    result = os.popen(command).read()
    log_debug (result)
    
    time.sleep(2)
    command = "curl -X GET http://localhost:5001/topo_change"
    log_debug (command)
    result = os.popen(command).read()
    log_debug (result)
    return ""
@app.route("/link/3/up")
def topology_update3up():
    command = "sudo ifconfig sw5-eth2 up"
    log_debug (command)
    result = os.popen(command).read()
    log_debug (result)

    time.sleep(2)
    command = "curl -X GET http://localhost:5001/topo_change"
    log_debug (command)
    result = os.popen(command).read()
    log_debug (result)
    return ""
#    return "bgp_update done\n"


if __name__ == "__main__":
    initialize()
    app.run(host="0.0.0.0", port=5000)
