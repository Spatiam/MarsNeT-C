import os
import sys
from time import sleep
import os.path
from os import path
import threading
from datetime import datetime,timedelta
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import RPi.GPIO as GPIO
import json
import requests

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
led_pin=14
GPIO.setup(led_pin,GPIO.OUT)
GPIO.output(led_pin,GPIO.LOW)
instance='rover'
network_map_path = 'ion-open-source-3.7.1/dtn/network.map'
ip_map_path = 'ion-open-source-3.7.1/dtn/ip.map'
msg_queue_path = 'ion-open-source-3.7.1/dtn/msg_queue.dat'
host_rc_path = 'ion-open-source-3.7.1/dtn/host.rc'
cfdp_rc_path = 'ion-open-source-3.7.1/dtn/host.cfdprc'
incoming_message_directory_path = 'ion-open-source-3.7.1/dtn/incoming'
my_event_handler=PatternMatchingEventHandler("*","",False,True)
FWD_QUEUE = 'ion-open-source-3.7.1/dtn/msg_queue.dat' 
DELAY_QUEUE = 'delay_queue.txt'

if not os.path.exists(incoming_message_directory_path):
  os.system('mkdir '+incoming_message_directory_path)

if os.path.exists(incoming_message_directory_path+'/msg.txt'):
  os.system('rm '+incoming_message_directory_path+'/msg.txt')#remove the msg.txt file

if not os.path.exists(DELAY_QUEUE):
  with open(DELAY_QUEUE, "w") as fl:
    fl.write(" ")

def marsweather():
    f = r"https://api.nasa.gov/insight_weather/?api_key=DEMO_KEY&feedtype=json&ver=1.0"
    data = requests.get(f)
    tt = json.loads(data.text)
    for i in tt:
        return tt[i]["AT"], tt[i]["HWS"]

#when change in directory is detected
def on_modified(event):
  global led_pin
  global instance
  if os.path.exists(incoming_message_directory_path+'/msg.txt'): #see if the msg.txt file is there
    print("File msg.txt exists")
    with open(incoming_message_directory_path+'/msg.txt', "r") as f:
      last = f.readline()
      print("read last line")
    if "@@msg" in last:
      print("MESSAGE RECEIVED:"+last.strip("\n"))#this is the message we received
      if os.path.exists(incoming_message_directory_path+'/msg.txt'):
        os.system('rm '+incoming_message_directory_path+'/msg.txt')#remove the msg.txt file
      if 'command' in last:
        tt = last.strip("\n").split("@#@")[4].split(":")
        return_address = last.strip("\n").split("@#@")[3]
        ts = last.strip("\n").split("@#@")[1]
        echo_msg = last.strip("\n").split("@#@")[4]
        rov_addr = instance+"_user"
        if tt[0] == 'command':
          if tt[1] == 'echo':
            print("ECHO COMMAND RECEIVED - RETURNING TO SENDER")
            with open(msg_queue_path, "a") as ec:
              ec.write("@@msg@#@"+ts+"@#@"+return_address+"@#@"+rov_addr+"@#@"+echo_msg+"@#@0")
          elif tt[1] == 'capture':
            print("CAPTURE COMMAND RECEIVED - SENDING IMAGE")
            os.system('fswebcam -r 1920x1080 --no-banner -q '+incoming_message_directory_path+"/latest.jpg")
            print("Picture taken")
            with open(msg_queue_path, "a") as ec:
              ec.write("\n@@file@#@"+ts+"@#@"+return_address+"@#@"+rov_addr+"@#@latest.jpg@#@0")
          elif tt[1] == 'ledon':
            print("LED ON COMMAND RECEIVED")
            GPIO.output(led_pin, GPIO.HIGH)
          elif tt[1] == 'ledoff':
            print("LED OFF COMMAND RECEIVED")
            GPIO.output(led_pin, GPIO.LOW)
          elif tt[1] == 'status':
            print("STATUS COMMAND RECEIVED")
            stts = str(marsweather()).replace("'","").replace("(","").replace(")","")
            with open(msg_queue_path, "a") as ec:
              print(return_address)
              ec.write("@@msg@#@"+ts+"@#@"+return_address+"@#@"+rov_addr+"@#@"+stts+"@#@0")

#watchdog
my_event_handler.on_modified = on_modified
my_observer = Observer()
my_observer.schedule(my_event_handler,incoming_message_directory_path,recursive=True)
my_observer.start()

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
f=open(host_rc_path, "w")
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
print(style.CYAN+"Configuring .cfdprc file..."+style.YELLOW)
with open(cfdp_rc_path, "w") as f:
  f.write("1\n")
  f.write("e 1\n")
  f.write("w 1\n")
  f.write("a entity "+current_eid+" bp ipn:"+current_eid+".0 7 0 0\n")
  f.write("m discard\n")
  f.write("m segsize 65000\n")
  f.write("s \'bputa\'\n")
print(style.GREEN+"DONE")
print("")
print(style.CYAN+"Starting ION..."+style.YELLOW, end='', flush=True)
os.system('ionstart -I '+host_rc_path)
print(style.GREEN+"DONE"+style.RESET)
print("")
print(style.CYAN+"Testing local server..."+style.YELLOW)
os.system('ss -panu')
os.system('ipcs')
print(style.GREEN+"DONE"+style.RESET)
print(style.CYAN+"Starting CFDPADMIN..."+style.YELLOW)
os.system('cfdpadmin '+cfdp_rc_path)
print(style.GREEN+"DONE"+style.RESET)

def message_queue_listener():
  while True:
    #check file every 1 second
    sleep(1)
    global graph
    #message queue updated
    #read queue
    with open(msg_queue_path, "r") as f:
      content=f.readlines()
    #send any messages that are in the queue
    for i in range(len(content)):
      content[i]=content[i].strip("\n")
      if "@@msg" in content[i]:
        status = content[i].split("@#@")[-1]
        if status == "0":
          ts = content[i].split("@#@")[1]
          tgt = content[i].split("@#@")[2]
          frm = content[i].split("@#@")[3]
          message = content[i].split("@#@")[4]
          send_message(message, ts, tgt, frm, content[i])
          content[i] = "@@msg@#@"+ts+"@#@"+tgt+"@#@"+frm+"@#@"+message+"@#@"+"1"
          #rewrite the file with a status update
          with open(msg_queue_path, "w") as f:
            for i in range(len(content)):
              f.write(content[i]+"\n")
      if "@@file" in content[i]:
        status = content[i].split("@#@")[-1]
        if status == "0":
          ts = content[i].split("@#@")[1]
          tgt = content[i].split("@#@")[2]
          frm = content[i].split("@#@")[3]
          message = content[i].split("@#@")[4]
          send_file(message, ts, tgt, frm, content[i])
          content[i] = "@@file@#@"+ts+"@#@"+tgt+"@#@"+frm+"@#@"+message+"@#@"+"1"
          #rewrite the file with a status update
          with open(msg_queue_path, "w") as f:
            for i in range(len(content)):
              f.write(content[i]+"\n")

def send_file(filename, ts, tgt, frm, entire):
  global graph
  global instance
  global nodes
  global nodes_eid
  global incoming_message_directory_path
  tgt_eid = tgt.split("_")[0]
  path_list = BFS_SP(graph, instance, tgt_eid)
  if len(path_list) != 0:
    print(style.RESET+style.GREEN+"Path found -> "+str(path_list)+style.RESET+"\n\n")
    for i in range(len(path_list)):
      if path_list[i] == instance:
        sendTo=nodes_eid[nodes.index(path_list[i+1])]
        with open('msg.txt', "w") as fw:
          fw.write("@@file@#@"+ts+"@#@"+tgt+"@#@"+frm+"@#@"+filename+"@#@0\n")
        print("#1")
        print("bpcp "+incoming_message_directory_path+"/"+filename+" "+sendTo+":"+incoming_message_directory_path+"/"+filename)
        os.system("bpcp "+incoming_message_directory_path+"/"+filename+" "+sendTo+":"+incoming_message_directory_path+"/"+filename)
        os.system('rm '+filename)
        print("#2")
        print("bpcp msg.txt "+sendTo+":"+incoming_message_directory_path+"/msg.txt")
        os.system("bpcp msg.txt "+sendTo+":"+incoming_message_directory_path+"/msg.txt")
        if os.path.exists(incoming_message_directory_path+'/msg.txt'):
          os.system('rm '+incoming_message_directory_path+'/msg.txt')#remove the msg.txt file
    
def send_message(message, ts, tgt, frm, entire):
  global graph
  global instance
  global nodes
  global nodes_eid
  global incoming_message_directory_path
  tgt_eid = tgt.split("_")[0]
  path_list = BFS_SP(graph, instance, tgt_eid)
  if len(path_list) != 0:
    print(style.RESET+style.GREEN+"Path found -> "+str(path_list)+style.RESET+"\n\n")
    for i in range(len(path_list)):
      if path_list[i] == instance:
        sendTo=nodes_eid[nodes.index(path_list[i+1])]
        with open('msg.txt', "w") as fw:
          fw.write("@@msg@#@"+ts+"@#@"+tgt+"@#@"+frm+"@#@"+message+"@#@0\n")
        print("#3")
        print("bpcp msg.txt "+sendTo+":"+incoming_message_directory_path+"/msg.txt")
        os.system("bpcp msg.txt "+sendTo+":"+incoming_message_directory_path+"/msg.txt")
        print("HERE")
        if os.path.exists('msg.txt'):
          os.system('rm msg.txt')#remove the msg.txt file
  else:
    print(style.RESET+style.RED+"Path not found"+style.RESET)

messageQueue=threading.Thread(target=message_queue_listener)
messageQueue.start()
