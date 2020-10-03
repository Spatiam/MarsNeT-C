import os
import sys
from time import sleep
import os.path
from os import path
import socket
import threading
import subprocess
from datetime import datetime
import signal
import readchar
import pyion
import pyinotify

instance=input('instance [earth, mars, delay, rover]:')
network_map_path = 'ion-open-source-3.7.1/dtn/network.map'
ip_map_path = 'ion-open-source-3.7.1/dtn/ip.map'
msg_queue_path = 'ion-open-source-3.7.1/dtn/msg_queue.dat'

class style():
  BLACK='\033[30m'
  RED='\033[31m'
  GREEN='\033[32m'
  YELLOW='\033[33m'
  BLUE='\033[34m'
  MAGENTA='\033[35m'
  CYAN='\033[36m'
  WHITE='\033[37m'
  UNDERLINE='\033[4m'
  RESET='\033[0m'
  WHITEBLACK='\033[0;30;47m'

def BFS_SP(graph, start, goal): 
  explored = [] 
  queue = [[start]] 
  if start == goal: 
    print("SAME NODE") 
    return
  while queue: 
    path = queue.pop(0) 
    node = path[-1] 
    if node not in explored: 
      neighbours = graph[node] 
      for neighbour in neighbours: 
        new_path = list(path) 
        new_path.append(neighbour) 
        queue.append(new_path) 
        if neighbour == goal: 
          return new_path
      explored.append(node) 
  print("CONNECTING PATH DOES NOT EXIST")
  return []

#parse network.map
os.system('clear')
connections = []
nodes = []
nodes_connectors = []
if path.exists(network_map_path):
  with open(network_map_path,'r') as f:
    network=f.readlines()
  for i in range(len(network)):
    network[i]=network[i].strip("\n")
    if network[i].split("->")[0] == instance:
      connections = network[i].split("->")[1].split(",")
    if network[i].split("->")[0] not in nodes:
      nodes.append(network[i].split("->")[0])
      nodes_connectors.append(network[i].split("->")[1])
  graph={}
  for i in range(len(nodes)):
     graph[nodes[i]]=nodes_connectors[i].split(",")
else:
  print("network.map not found")
  quit()

#parse ip.map
nodes_local_ip = []
nodes_public_ip = []
nodes_eid = []
if path.exists(ip_map_path):
  with open(ip_map_path,'r') as f:
    definitions=f.readlines()
  for x in range(len(nodes)):
    for y in range(len(definitions)):
      definitions[y]=definitions[y].strip("\n")
      if nodes[x] == definitions[y].split("_")[2]:
        nodes_local_ip.append(definitions[y].split("_")[0])
        nodes_public_ip.append(definitions[y].split("_")[1])
        nodes_eid.append(definitions[y].split("_")[3])
  for i in range(len(nodes)):
    if nodes[i] == instance:
      current_eid = nodes_eid[i]
      current_local_ip = nodes_local_ip[i]
else:
  print("ip.map not found")
  print(ip_map_path)
  quit()

#startup procedures
print(style.RESET+style.CYAN+"Stopping ION..."+style.YELLOW)
os.system('killm')
print(style.GREEN+"DONE")
print("")
print(style.CYAN+"Configuring .rc file..."+style.YELLOW)
f=open("ion-3.6.2/dtn/host.rc", "w")
f.write("## begin ionadmin\n")
f.write("1 "+current_eid+" \'\'\n")
f.write("s\n")
f.write("\n")
f.write("m horizon +0\n")
f.write("\n")
for i in range(len(nodes_eid)):
  if nodes_eid[i] != current_eid and nodes[i] in connections:
    f.write("a contact +1 +3600 "+current_eid+" "+current_eid+" 100000\n")
    f.write("a contact +1 +3600 "+current_eid+" "+nodes_eid[i]+" 100000\n")
    f.write("a contact +1 +3600 "+nodes_eid[i]+" "+current_eid+" 100000\n")
    f.write("a contact +1 +3600 "+nodes_eid[i]+" "+nodes_eid[i]+" 100000\n")
for i in range(len(nodes_eid)):
  if nodes_eid[i] != current_eid and nodes[i] in connections:
    f.write("a range +1 +3600 "+current_eid+" "+current_eid+" 1\n")
    f.write("a range +1 +3600 "+current_eid+" "+nodes_eid[i]+" 1\n")
    f.write("a range +1 +3600 "+nodes_eid[i]+" "+current_eid+" 1\n")
    f.write("a range +1 +3600 "+nodes_eid[i]+" "+nodes_eid[i]+" 1\n")
f.write("m production 1000000\n")
f.write("m consumption 1000000\n")
f.write("## end ionadmin\n")
f.write("\n")
f.write("## begin ionsecadmin\n")
f.write("1\n")
f.write("## end ionsecadmin\n")
f.write("\n")
f.write("## begin ltpadmin\n")
f.write("1 32\n")
f.write("\n")
f.write("a span "+current_eid+" 32 32 1400 10000 1 \'udplso "+current_local_ip+":4556\' 300\n")
for i in range(len(nodes_eid)):
  if nodes_eid[i] != current_eid and nodes[i] in connections:
    f.write("a span "+nodes_eid[i]+" 32 32 1400 10000 1 \'udplso "+nodes_public_ip[i]+":4556\' 300\n")
f.write("\n")
f.write("s \'udplsi "+current_local_ip+":4556\'\n")
f.write("## end ltpadmin\n")
f.write("\n")
f.write("## begin bpadmin\n")
f.write("1\n")
f.write("a scheme ipn \'ipnfw\' \'ipnadminep\'\n")
f.write("a endpoint ipn:"+current_eid+".0 q\n")
f.write("a endpoint ipn:"+current_eid+".1 q\n")
f.write("a endpoint ipn:"+current_eid+".2 q\n")
f.write("a endpoint ipn:"+current_eid+".64 q\n")
f.write("a endpoint ipn:"+current_eid+".65 q\n")
f.write("\n")
f.write("a protocol ltp 1400 100\n")
f.write("a induct ltp "+current_eid+" ltpcli\n")
f.write("\n")
f.write("a outduct ltp "+current_eid+" ltpclo\n")
for i in range(len(nodes_eid)):
  if nodes_eid[i] != current_eid and nodes[i] in connections:
    f.write("a outduct ltp "+nodes_eid[i]+" ltpclo\n")
f.write("\n")
f.write("s\n")
f.write("## end bpadmin\n")
f.write("\n")
f.write("## begin ipnadmin\n")
f.write("a plan "+current_eid+" ltp/"+current_eid+"\n")
for i in range(len(nodes_eid)):
  if nodes_eid[i] != current_eid and nodes[i] in connections:
    f.write("a plan "+nodes_eid[i]+" ltp/"+nodes_eid[i]+"\n")
f.write("\n")
f.write("## end ipnadmin\n")
f.close()
print(style.GREEN+"DONE")
print("")
print(style.CYAN+"Starting ION..."+style.YELLOW, end='', flush=True)
os.system('ionstart -I ion-3.6.2/dtn/host.rc')
print(style.GREEN+"DONE"+style.RESET)
print("")
print(style.CYAN+"Testing local server..."+style.YELLOW)
os.system('ss -panu')
os.system('ipcs')
print(style.GREEN+"DONE"+style.RESET)
      

def message_queue_listener():
  while True:
    #check file every 10 seconds
    sleep(10)
    global graph
    #message queue updated
    print("CHECKING")
    #read queue
    with open(msg_queue_path, "r") as f:
      content=f.readlines()
    #send any messages that are in the queue
    for i in range(len(content)):
      content[i]=content[i].strip("\n")
      if "@#@" in content[i]:
        status = content[i].split("@#@")[-1]
        if status == "0":
          #send message at appropriate time
          ts = content[i].split("@#@")[1]
          tgt = content[i].split("@#@")[2]
          frm = content[i].split("@#@")[3]
          message = content[i].split("@#@")[4]
          send_message(message, ts, tgt, frm)
          content[i] = "@@msg@#@"+ts+"@#@"+tgt+"@#@"+frm+"@#@"+message+"@#@"+"1"
      #rewrite the file with a status update
    with open(msg_queue_path, "w") as f:
      for i in range(len(content)):
        f.write(content[i]+"\n")

def send_message(message, ts, tgt, frm):
  global graph
  global instance
  tgt_eid = tgt.split("_")[0]
  path_list = BFS_SP(graph, instance, tgt_eid)
  if len(path_list) != 0:
    print(style.RESET+style.GREEN+"Path found -> "+str(path_list)+style.RESET+"\n\n")
    for i in range(len(path_list)):
      if path_list[i] == instance:
        print("echo \"@@msg@#@"+ts+"@#@"+tgt+"@#@"+frm+"@#@"+message+"@#@0\" | bpsource ipn:"+path_list[i+1]+".1")
        os.system("echo \"@@msg@#@"+ts+"@#@"+tgt+"@#@"+frm+"@#@"+message+"@#@0\" | bpsource ipn:"+path_list[i+1]+".1")
  else:
    print(style.RESET+style.RED+"Path not found"+style.RESET)

messageQueue=threading.Thread(target=message_queue_listener)
#messageListener=threading.Thread(target=message_listener)
messageQueue.start()
#messageListener.start()