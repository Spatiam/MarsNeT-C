import os
import sys
from time import sleep
import os.path
from os import path
import threading
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

instance=input("instance (earth, delay, mars, rover):")
network_map_path = 'ion-open-source-3.7.1/dtn/network.map'
ip_map_path = 'ion-open-source-3.7.1/dtn/ip.map'
msg_queue_path = 'ion-open-source-3.7.1/dtn/msg_queue.dat'
host_rc_path = 'ion-open-source-3.7.1/dtn/host.rc'
cfdp_rc_path = 'ion-open-source-3.7.1/dtn/host.cfdprc'
incoming_message_directory_path = 'ion-open-source-3.7.1/dtn/incoming'
my_event_handler=PatternMatchingEventHandler("*","",False,True)
def readlastline(f):
    try:
        f.seek(-2, 2)
        while f.read(1) != b"\n":
            f.seek(-2, 1)
        return str(f.read().decode('utf-8'))
    except:
        return ' '

#when change in directory is detected
def on_modified(event):
  global duplicate_check
  global instance
  if os.path_exists(incoming_message_directory_path+'/msg.txt'): #see if the msg.txt file is there
    with open(event.src_path+'/msg.txt', "rb") as f:
      last = readlastline(f)
    if "@@msg" in last:
      print("MESSAGE RECEIVED:"+last.strip("\n"))#this is the message we received
      os.system('rm '+incoming_message_directory_path+'/msg.txt')#remove the msg.txt file
      tt = line.strip("\n").split("@#@")[2].split("_")[0]
      if tt == instance:#we keep this message
        print("Message is at it's final location")
      else: #this message needs to be forwarded
        with open(msg_queue_path, "a") as app: #append the message to the message queue
          app.write(last)

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
  f.write("w 0\n")
  f.write("a entity "+current_eid+" bp ipn:"+current_eid+".0 7 0 0\n")
  f.write("m discard\n")
  f.write("m segsize 1000\n")
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
print(style.CYAN+"Starting CFDPADMIN..."+style.YELLOW, end='', flush=True)
os.system('cfdpadmin '+cfdp_rc_path)
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
          send_message(message, ts, tgt, frm, content[i])
          content[i] = "@@msg@#@"+ts+"@#@"+tgt+"@#@"+frm+"@#@"+message+"@#@"+"1"
          #rewrite the file with a status update
          with open(msg_queue_path, "w") as f:
            for i in range(len(content)):
              f.write(content[i]+"\n")

def process_msg(in_msg):
    os.system('python3 ephemerisMars.py')
    split_msg = in_msg[2:].split('@#@')
    msg_type = split_msg[0]
    if msg_type == 'msg':
        msg_timestamp = split_msg[1]
        msg_target_ip = split_msg[2]
        msg_sender_ip = split_msg[3]
        msg_content = split_msg[4]
    else:
        msg_timestamp = split_msg[2]
        msg_target_ip = split_msg[3]
        msg_sender_ip = split_msg[4]
        msg_content = split_msg[1]
    ephemeris_file = open('../Ephemeris/mars-earth-delay.txt', 'r') 
    lines = ephemeris_file.readlines() 
    for line in lines: 
        delay = round(float(line) * 60)
    now = datetime.now()
    send = now + timedelta(seconds=delay)
    send_str = send.strftime("%d-%b-%Y(%H:%M:%S.%f)")
    queue = '#beg#' + msg_sender_ip + ' ' + msg_target_ip + ' ' + msg_type + ' ' + msg_timestamp + '\n'
    queue += msg_content + '\n'
    queue += '#end#' + send_str + '\n'       
    f = open('queue.txt', 'a')
    f.write(queue + '\n')
    f.close()

def send_message(message, ts, tgt, frm, entire):
  global graph
  global instance
  global nodes
  global nodes_eid
  global incoming_message_directory_path
  if instance != 'delay':
    tgt_eid = tgt.split("_")[0]
    path_list = BFS_SP(graph, instance, tgt_eid)
    if len(path_list) != 0:
      print(style.RESET+style.GREEN+"Path found -> "+str(path_list)+style.RESET+"\n\n")
      for i in range(len(path_list)):
        if path_list[i] == instance:
          sendTo=nodes_eid[nodes.index(path_list[i+1])]
          with open('msg.txt', "w") as fw:
            fw.write("@@msg@#@"+ts+"@#@"+tgt+"@#@"+frm+"@#@"+message+"@#@0\n")
          print("bpcp msg.txt "+sendTo+":"+incoming_message_directory_path+"/msg.txt")
          os.system("bpcp msg.txt "+sendTo+":"+incoming_message_directory_path+"/msg.txt")
    else:
      print(style.RESET+style.RED+"Path not found"+style.RESET)
  else:
    #delay instance to we forward to the delay message queue
    process_msg(entire)

messageQueue=threading.Thread(target=message_queue_listener)
messageQueue.start()
