#!/bin/bash
IP_OTHER_END=10.0.1.20  ;# Tunnel endpoint: Zebos VPC eth1

#sudo pkill controller
#nohup ~/openflow/controller/controller ptcp: &

sudo ./stop-network.sh

sudo mn -c

tpid=`ps -eadlf |grep bgp-topo-viewer.py | grep python | grep -v grep | awk '{print $4}'`
if [ x${tpid} != "x" ]; then
   echo "killing bgp-topo-viewer"
   sudo kill -KILL $tpid
fi

tpid=`ps -eadlf |grep transit-route-pusher.py| grep python | grep -v grep | awk '{print $4}'`
if [ x${tpid} != "x" ]; then
   sudo kill -KILL $tpid
   echo "killing transit-route-pusher"
fi

ssh -o StrictHostKeyChecking=no ubuntu@10.0.0.116 'killall ping' > /dev/null 2>&1 &

sudo pkill bgpd
sudo pkill zebra
sudo pkill java 
sudo pkill tcpdump
sudo sysctl -w net.ipv4.conf.all.send_redirects=0

sudo rm -f Floodlight.log
#java -Dlogback.configurationFile=~/logback.xml -jar ~/floodlight.jar -cf ~/interdomain.properties  > /dev/null 2>&1 &
#java -Dlogback.configurationFile=~/logback.xml -jar ~/my-floodlight.jar -cf ~/interdomain.properties  > /dev/null 2>&1 &

sudo /usr/sbin/tcpdump -n -i lo -s0 -w /home/ubuntu/sdn/sdn1vpc.lo.pcap 'tcp port 6633' &


#add by linpp
sudo ~/start-cassandra.sh start
sleep 5
#end by linpp

echo "** Running ONOS **"


java -jar ~/lppfloodlight.jar -cf ~/interdomain-lpp.properties > Floodlight.log 2>&1 &
sleep 5
# masa:
#echo "** Running umfloodlight **"
#sleep 14
#java -jar ~/umfloodlight.jar -cf ~/interdomain.properties > Floodlight.log 2>&1 &
#java -jar ~/ukfloodlight.jar -cf ~/interdomain.properties > Floodlight.log 2>&1 &
#java -jar ~/my-umfloodlight.jar -cf ~/interdomain.properties > Floodlight.log 2>&1 &

sleep 6
echo "mininet to start"
sudo ./onlab.py 
#read value


echo "[ { 'networkDestination' : '172.16.20.0' }, { 'networkDestination' : '172.16.30.0' }]"

sleep 8 

cd ~/bgp-viewer

#echo
#start add by linpp

#echo "Start the bgp-viewer?"
#read value
#end add by linpp
 
/home/ubuntu/bgp-viewer/bgp-topo-viewer.py -v --simple -t sdn1vpc.onlab.us sdn1vpc.onlab.us:8090 > viewer.log 2>&1 &
cd ~/sdn

#start comment by linpp

curl -s -d '{"switch": "00:00:00:00:00:00:00:a1", "name":"demo1-step1-a1-ping", "src-mac":"00:00:00:00:00:02", "ether-type":"0x800", "dst-ip":"172.16.20.0/25", "cookie":"0x20000000000000", "priority":"0", "ingress-port":"2","active":"true", "actions":"set-dst-mac=06:b3:f3:97:07:22,output=4"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json

curl -s -d '{"switch": "00:00:00:00:00:00:00:a1","name":"demo1-step1-a1-echo","src-mac":"06:b3:f3:97:07:22", "dst-mac":"00:00:00:00:00:02", "ether-type":"0x800", "cookie":"0x20000000000000", "priority":"0", "ingress-port":"4","active":"true", "actions":"output=2"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json

curl -s -d '{"switch": "00:00:00:00:00:00:00:a3","name":"demo1-step1-a3-ping","src-mac":"00:00:00:00:00:02", "dst-mac":"06:b3:f3:97:07:22", "ether-type":"0x800", "cookie":"0x20000000000000", "priority":"0", "ingress-port":"1","active":"true", "actions":"output=4"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json

curl -s -d '{"switch": "00:00:00:00:00:00:00:a3", "name":"demo1-step1-a3-echo", "src-mac":"06:b3:f3:97:07:22", "ether-type":"0x800", "dst-ip":"172.16.10.0/24", "cookie":"0x20000000000000", "priority":"0", "ingress-port":"4", "active":"true", "actions":"set-dst-mac=00:00:00:00:00:02,output=1"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json

ssh -o StrictHostKeyChecking=no ubuntu@host2 'ping 172.16.20.1' > /dev/null 2>&1 &
ssh_pid=$!
echo ""
echo "SSH: $ssh_pid"
echo ""
echo "Press any key to del link btwn SLC and CHI"
read value
sudo ifconfig sw3-eth1 down

sleep 1
curl -s -d '{"switch": "00:00:00:00:00:00:00:a1", "name":"demo1-step2-a1-ping", "src-mac":"00:00:00:00:00:02", "ether-type":"0x800", "dst-ip":"172.16.20.0/25", "cookie":"0x20000000000000", "priority":"0", "ingress-port":"2","active":"true", "actions":"set-dst-mac=06:b3:f3:97:07:22,output=3"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json

curl -s -d '{"switch": "00:00:00:00:00:00:00:a1","name":"demo1-step2-a1-echo","src-mac":"06:b3:f3:97:07:22", "dst-mac":"00:00:00:00:00:02", "ether-type":"0x800", "cookie":"0x20000000000000", "priority":"0", "ingress-port":"3","active":"true", "actions":"output=2"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json

curl -s -d '{"switch": "00:00:00:00:00:00:00:a2","name":"demo1-step2-a2-ping","src-mac":"00:00:00:00:00:02", "dst-mac":"06:b3:f3:97:07:22", "ether-type":"0x800", "cookie":"0x20000000000000", "priority":"0", "ingress-port":"1","active":"true", "actions":"output=2"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json

curl -s -d '{"switch": "00:00:00:00:00:00:00:a2","name":"demo1-step2-a2-echo","src-mac":"06:b3:f3:97:07:22", "dst-mac":"00:00:00:00:00:02", "ether-type":"0x800", "cookie":"0x20000000000000", "priority":"0", "ingress-port":"2","active":"true", "actions":"output=1"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json

curl -s -d '{"switch": "00:00:00:00:00:00:00:a4","name":"demo1-step2-a4-ping","src-mac":"00:00:00:00:00:02", "dst-mac":"06:b3:f3:97:07:22", "ether-type":"0x800", "cookie":"0x20000000000000", "priority":"0", "ingress-port":"1","active":"true", "actions":"output=2"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json

curl -s -d '{"switch": "00:00:00:00:00:00:00:a4","name":"demo1-step2-a4-echo","src-mac":"06:b3:f3:97:07:22", "dst-mac":"00:00:00:00:00:02", "ether-type":"0x800", "cookie":"0x20000000000000", "priority":"0", "ingress-port":"2","active":"true", "actions":"output=1"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json

curl -s -d '{"switch": "00:00:00:00:00:00:00:a3","name":"demo1-step2-a3-ping","src-mac":"00:00:00:00:00:02", "dst-mac":"06:b3:f3:97:07:22", "ether-type":"0x800", "cookie":"0x20000000000000", "priority":"0", "ingress-port":"2","active":"true", "actions":"output=4"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json

curl -s -d '{"switch": "00:00:00:00:00:00:00:a3", "name":"demo1-step2-a3-echo", "src-mac":"06:b3:f3:97:07:22", "ether-type":"0x800", "dst-ip":"172.16.10.0/24", "cookie":"0x20000000000000", "priority":"0", "ingress-port":"4", "active":"true", "actions":"set-dst-mac=00:00:00:00:00:02,output=2"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json

echo ""
echo "Press any key to del link SLC and AS1"
read value
sudo ifconfig tap0 down
curl -X GET http://sdn1vpc.onlab.us:8000/downlink/1
curl -s -d '{"switch": "00:00:00:00:00:00:00:a4","name":"demo1-step3-a4-ping","src-mac":"00:00:00:00:00:02", "dst-mac":"06:b3:f3:97:07:22", "ether-type":"0x800", "cookie":"0x20000000000000", "priority":"0", "ingress-port":"1","active":"true", "actions":"output=2"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json

curl -s -d '{"switch": "00:00:00:00:00:00:00:a4","name":"demo1-step3-a4-echo","src-mac":"06:b3:f3:97:07:22", "dst-mac":"00:00:00:00:00:02", "ether-type":"0x800", "cookie":"0x20000000000000", "priority":"0", "ingress-port":"2","active":"true", "actions":"output=1"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json

curl -s -d '{"switch": "00:00:00:00:00:00:00:a3","name":"demo1-step3-a3-ping","src-mac":"00:00:00:00:00:02", "dst-mac":"06:b3:f3:97:07:22", "ether-type":"0x800", "cookie":"0x20000000000000", "priority":"0", "ingress-port":"2","active":"true", "actions":"output=3"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json

curl -s -d '{"switch": "00:00:00:00:00:00:00:a3","name":"demo1-step3-a3-echo","src-mac":"06:b3:f3:97:07:22", "dst-mac":"00:00:00:00:00:02", "ether-type":"0x800", "cookie":"0x20000000000000", "priority":"0", "ingress-port":"3","active":"true", "actions":"output=2"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json
    
curl -s -d '{"switch": "00:00:00:00:00:00:00:a5","name":"demo1-step3-a5-ping","src-mac":"00:00:00:00:00:02", "dst-mac":"06:b3:f3:97:07:22", "ether-type":"0x800", "cookie":"0x20000000000000", "priority":"0", "ingress-port":"1","active":"true", "actions":"output=3"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json
    
    
curl -s -d '{"switch": "00:00:00:00:00:00:00:a5", "name":"demo1-step2-a5-echo", "src-mac":"06:b3:f3:97:07:22", "ether-type":"0x800", "dst-ip":"172.16.10.0/24", "cookie":"0x20000000000000", "priority":"0", "ingress-port":"3", "active":"true", "actions":"set-dst-mac=00:00:00:00:00:02,output=1"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json


#sleep 2
#sudo ovs-ofctl del-flows sw1 dl_dst=12:34:56:78:90:12
echo ""
echo "Press any key to Start Demo2"
cd ~/sdn
./link.py > linkpy.log 2>&1 &
#comment by linpp for test
./transit-route-pusher.py > transit-route-pusher.log 2>&1 &
#end comment by linpp for test
read value

#comment by linpp
kill -KILL $ssh_pid

#ssh -o StrictHostKeyChecking=no ubuntu@host2 'killall ping' > /dev/null 2>&1 &
#end commnet by linpp

#sleep 5
ssh -o StrictHostKeyChecking=no ubuntu@10.0.0.116 'ping -I 172.16.30.1 172.16.20.1' > /dev/null 2>&1 &
sudo ovs-ofctl del-flows sw1 nw_dst=172.16.20.0/25
#add by linpp
#sudo ovs-ofctl del-flows sw3 dl_src=06:b3:f3:97:07:22
#end add by linpp
#add by linpp
#echo "bgp reroute?"
#read value 
curl -s -d '{"switch": "00:00:00:00:00:00:00:a3","name":"sw3-bgp-go", "dst-mac":"ce:33:f4:f1:de:0f","src-mac":"00:00:00:00:00:20", "ether-type":"0x800", "cookie":"0x20000000000000", "priority":"32767", "ingress-port":"2","active":"true", "actions":"output=3"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json

curl -s -d '{"switch": "00:00:00:00:00:00:00:a3","name":"sw3-bgp-echo","dst-mac":"00:00:00:00:00:20","src-mac":"ce:33:f4:f1:de:0f", "ether-type":"0x800", "cookie":"0x20000000000000", "priority":"32767", "ingress-port":"3","active":"true", "actions":"output=2"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json

curl -s -d '{"switch": "00:00:00:00:00:00:00:a4","name":"sw4-bgp-go", "dst-mac":"ce:33:f4:f1:de:0f","src-mac":"00:00:00:00:00:20", "ether-type":"0x800", "cookie":"0x20000000000000", "priority":"32767", "ingress-port":"1","active":"true", "actions":"output=2"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json

curl -s -d '{"switch": "00:00:00:00:00:00:00:a4","name":"sw4-bgp-echo","dst-mac":"00:00:00:00:00:20","src-mac":"ce:33:f4:f1:de:0f", "ether-type":"0x800", "cookie":"0x20000000000000", "priority":"32767", "ingress-port":"2","active":"true", "actions":"output=1"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json

curl -s -d '{"switch": "00:00:00:00:00:00:00:a5","name":"sw5-bpg-go", "dst-mac":"ce:33:f4:f1:de:0f", "src-mac":"00:00:00:00:00:20","ether-type":"0x800", "cookie":"0x20000000000000", "priority":"32767", "ingress-port":"1","active":"true", "actions":"output=3"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json

curl -s -d '{"switch": "00:00:00:00:00:00:00:a5","name":"sw5-bgp-echo","dst-mac":"00:00:00:00:00:20","src-mac":"ce:33:f4:f1:de:0f", "ether-type":"0x800", "cookie":"0x20000000000000", "priority":"32767", "ingress-port":"3", "active":"true", "actions":"output=1"}' http://127.0.0.1:8090/wm/staticflowentrypusher/json


while true; do
	echo ""
	echo "Link DOWN ---- [1]:CHI-IAH;  [2]:CHI-AS2;  [3]:LAX-AS3;  [4]:NYC-ATL;"
	echo "Link UP ---- [5]:AS3-LAX;  [6]:CHI-IAH;  [7]:CHI-AS2;  [8]ATL-NYC."
	echo "Please enter the number:"
	read link_number
	if  [ "$link_number" = "1" ]; then
	sudo ifconfig sw4-eth2 down
	
	elif [ "$link_number" = "2" ]; then
	sudo ifconfig tap0 down
	curl -X GET http://sdn1vpc.onlab.us:8000/downlink/1

	elif [ "$link_number" = "3" ]; then
	sudo ifconfig tap2 down
        curl -X GET http://sdn1vpc.onlab.us:8000/downlink/3

        elif [ "$link_number" = "4" ]; then
	sudo ifconfig sw5-eth2 down
	
	
	elif [ "$link_number" = "5" ]; then
	sudo ifconfig tap2 up
	curl -X GET http://sdn1vpc.onlab.us:8000/uplink/3
	
	elif [ "$link_number" = "6" ]; then
	sudo ifconfig sw4-eth2 up
	
	elif [ "$link_number" = "7" ]; then
	sudo ifconfig tap0 up 
	curl -X GET http://sdn1vpc.onlab.us:8000/uplink/1
	
	elif [ "$link_number" = "8" ]; then
	sudo ifconfig sw5-eth2 up
	
	fi

	sleep 2
        curl -X GET http://localhost:5001/topo_change
done



#end add by linpp
echo "Press any key to Del Link between CHI and IAH"
read value
#start replace by linpp
#sudo ifconfig sw5-eth2 down
sudo ifconfig sw4-eth2 down
#end replace by linpp
#now=`date`
#echo "$now LINK NYC-ATL down" >> /home/ubuntu/sdn/transit-route-pusher.log
sleep 2
curl -X GET http://localhost:5001/topo_change
# sudo ovs-ofctl del-flows sw2 nw_dst=192.168.20.1

#while [ 1 ]; do
#   bytes=`sudo ovs-ofctl dump-flows sw6 |grep 'nw_dst=172.16.20.0/25' | awk -F"," '{print $4}' | sed 's/.*\=//g'`
#   echo "bytes: $bytes"
#   len=`echo $bytes | wc -m`
#   if [ $len -gt 0 ]; then
#     if [  x$bytes != "x0"  ]; then
#       sudo ovs-ofctl del-flows sw6 'nw_dst=172.16.20.0/25'
#       echo "flow removed"
#     fi
#   fi
#   echo "----Fwd Path--"
#   echo "sw2 table"
#   sudo ovs-ofctl dump-flows sw2 |grep 'nw_dst=172.16.20.0/25'
#   sudo ovs-ofctl dump-flows sw4 |grep 'dl_src=ce:33:f4:f1:de:0f,dl_dst=02:55:cf:ff:b1:29'
#   echo "sw4 table"
#   sudo ovs-ofctl dump-flows sw4 |grep 'dl_src=02:55:cf:ff:b1:29,dl_dst=ce:33:f4:f1:de:0f'
#   echo "sw3 table"
#   sudo ovs-ofctl dump-flows sw3 |grep 'dl_src=02:55:cf:ff:b1:29,dl_dst=ce:33:f4:f1:de:0f'
#   echo "sw5 table"
#   sudo ovs-ofctl dump-flows sw5 |grep 'dl_src=02:55:cf:ff:b1:29,dl_dst=ce:33:f4:f1:de:0f'
#   echo "----------------"
#   echo "----Rev Path--"
#   echo "sw5 table"
#   sudo ovs-ofctl dump-flows sw5 |grep 'nw_dst=172.16.30.0/24'
#   echo "sw3 table"
#   sudo ovs-ofctl dump-flows sw3 |grep 'dl_src=ce:33:f4:f1:de:0f,dl_dst=02:55:cf:ff:b1:29'
#   echo "sw4 table"
#   sudo ovs-ofctl dump-flows sw4 |grep 'dl_src=ce:33:f4:f1:de:0f,dl_dst=02:55:cf:ff:b1:29'
#   echo "sw2 table"
#   sudo ovs-ofctl dump-flows sw4 |grep 'dl_src=ce:33:f4:f1:de:0f,dl_dst=02:55:cf:ff:b1:29'
#   echo "----------------"

#   echo "waiting loop: do you want to exit [y/n]?"
#   read -t 2 value 
#   if [ x$value == "xy" ]; then 
#     break;
#   fi
#     sudo ovs-ofctl del-flows sw6 'nw_dst=172.16.20.0/25'
#   elif [ x$value == "xn" ]; then 
#  fi 
#done

echo "Press any key to Del Link between LAX and AS3"
read value
sudo ifconfig tap2 down
curl -X GET http://sdn1vpc.onlab.us:8000/downlink/3

sleep 2
#edit by linpp
curl -X GET http://localhost:5001/topo_change
#curl -X GET http://localhost:5001/topo_change_lpp
#curl -X GET http://localhost:5001/bgp_update
now=`date`
#echo "$now LINK LAX-AS3 down" >> /home/ubuntu/sdn/transit-route-pusher.log

	#to add link on the gui
