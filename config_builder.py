import os
import sys
from time import sleep
import os.path
from os import path
import threading
from datetime import datetime,timedelta
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
FWD_QUEUE = 'ion-open-source-3.7.1/dtn/msg_queue.dat' 
DELAY_QUEUE = 'delay_queue.txt'

USERS_DIR = 'Users/'
UPLOAD_DIR = 'Uploads/'
MSG_FILE_NAME = 'msg_log.txt'
if instance == 'earth':
  THIS_USER = 'Houston'
if instance == 'rover':
  THIS_USER = 'Rover'
if instance == 'delay':
  THIS_USER = 'Delay'
if instance == 'mars':
  THIS_USER = 'Mars'
FWD_DIR='ion-open-source-3.7.1/dtn/incoming/'
FWD_QUEUE='ion-open-source-3.7.1/dtn/msg_queue.dat'
user_dict={'Houston':'earth_user','Rover':'rover_user', 'Delay':'delay_user', 'Mars':'mars_user' }
user_names={'earth_user':'Houston Control Center','rover_user':'Mars Rover', 'delay_user':'Relay Node', 'mars_user':'Mars User'}
filedict = {}
msg_dict = {}
users = os.listdir('Users/')
for user in users:
    if user[0:1] == '.':
        users.remove(user)
for user in users:
    msg_dict[user] = os.path.getmtime(USERS_DIR + user + '/' + MSG_FILE_NAME)
    filedict[user] = dict ([(f, None) for f in os.listdir(USERS_DIR + user + '/' + UPLOAD_DIR)])

if not os.path.exists(incoming_message_directory_path):
  os.system('mkdir '+incoming_message_directory_path)

if os.path.exists(incoming_message_directory_path+'/msg.txt'):
  os.system('rm '+incoming_message_directory_path+'/msg.txt')#remove the msg.txt file

if not os.path.exists(DELAY_QUEUE):
  with open(DELAY_QUEUE, "w") as fl:
    fl.write(" ")

def lst_file(user, file):
    #print('Added: ' + str(file))
    file_path = USERS_DIR + user + '/' + UPLOAD_DIR + file
    os.system('mv ' + file_path + ' ' + FWD_DIR)
    #print('mv ' + file_path + ' ' + FWD_DIR)
    now = datetime.now()
    date_str = now.strftime("%d-%b-%Y(%H:%M:%S)")
    str_queue = '@@file@#@'+date_str+'@#@'+user_dict[user]+'@#@'+ user_dict[THIS_USER] +'@#@'+file+'@#@0'
    queue_file = open(FWD_QUEUE,'a')
    queue_file.write(str_queue)
    #print('queued:' + str_queue)
    queue_file.close()
    filedict[user] = os.path.getmtime(USERS_DIR + user + '/' + MSG_FILE_NAME)

def lst_msg(user):
    #print('Modified: ' + user + '\'s message log')
    msg_file = open(USERS_DIR + user + '/' + MSG_FILE_NAME, 'r')
    lines = msg_file.readlines() 
    count = 0
    for line in lines:
        if count == 0:
            content = line.strip('\n')
            count += 1
        else:
            content += ' ' + line.strip('\n')
    msg_file.close()
    now = datetime.now()
    date_str = now.strftime("%d-%b-%Y(%H:%M:%S)")
    str_queue = '@@msg@#@'+date_str+'@#@'+user_dict[user]+'@#@'+ user_dict[THIS_USER] +'@#@'+content+'@#@0'
    queue_file = open(FWD_QUEUE,'a')
    queue_file.write(str_queue)
    #print('queued:' + str_queue)
    queue_file.close()
    filedict[user] = os.path.getmtime(USERS_DIR + user + '/' + MSG_FILE_NAME)

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
        msg_timestamp = split_msg[1]
        msg_target_ip = split_msg[2]
        msg_sender_ip = split_msg[3]
        msg_content = split_msg[4]
    ephemeris_file = open('Ephemeris/mars-earth-delay.txt', 'r') 
    lines = ephemeris_file.readlines() 
    for line in lines: 
        delay = round(float(line) * 60)
    now = datetime.now()
    send = now + timedelta(seconds=delay)

    send_str = send.strftime("%d/%b/%Y %H:%M:%S (UTC)")
    print('Message Forwarding delayed until: ' + send_str )

    send_str = send.strftime("%d-%b-%Y(%H:%M:%S.%f)")
    queue = '#beg#' + msg_sender_ip + ' ' + msg_target_ip + ' ' + msg_type + ' ' + msg_timestamp + '\n'
    queue += msg_content + '\n'
    queue += '#end#' + send_str + '\n'       
    f = open('delay_queue.txt', 'a')
    f.write(queue + '\n')
    f.close()

def print_g(str_msg):
  print(style.RESET + style.GREEN + str_msg + style.RESET)

def print_c(str_msg):
  print(style.RESET + style.CYAN + str_msg + style.RESET)

def print_rcv(str_msg):

  split_msg = str_msg[2:].split('@#@')

  msg_type = split_msg[0]
  msg_timestamp = split_msg[1]
  timestamp_date = datetime.strptime(msg_timestamp,'%d-%b-%Y(%H:%M:%S)')
  msg_timestamp = timestamp_date.strftime("%d/%b/%Y %H:%M:%S (UTC)")

  target = user_names[split_msg[2]]
  sender = user_names[split_msg[3]]
  msg_content = split_msg[4]

  now = datetime.now()
  now_str = now.strftime("%d/%b/%Y %H:%M:%S (UTC)")

  if msg_type == 'msg':
    print_g('\nMessage Received')

    print('Message content: ' + msg_content + '\n')
  
  else:
    print_g('\nFile Received')
    print('File name: ' + msg_content)

  print('Time Received: ' + now_str + '\n')

  print('Original sender: ' + sender + '\n')
  print('Time sent from origin: ' + msg_timestamp)

  print('Final Destination: ' + target + '\n')

def print_snd(str_msg):

  split_msg = str_msg[2:].split('@#@')

  msg_type = split_msg[0]
  msg_timestamp = split_msg[1]
  timestamp_date = datetime.strptime(msg_timestamp,'%d-%b-%Y(%H:%M:%S)')
  msg_timestamp = timestamp_date.strftime("%d/%b/%Y %H:%M:%S (UTC)")
  target = user_names[split_msg[2]]
  sender = user_names[split_msg[3]]
  msg_content = split_msg[4]

  now = datetime.now()
  now_str = now.strftime("%d/%b/%Y %H:%M:%S (UTC)")

  if msg_type == 'msg':
    print_g('\nSending Message')

    print('Message content: ' + msg_content + '\n')
  
  else:
    print_g('\nSending File')
    print('File name: ' + msg_content + '\n')

  print('Time Sending: ' + now_str + '\n')

  print('Original sender: ' + sender + '\n')
  print('Time sent from origin: ' + msg_timestamp)

  print('Final Destination: ' + target + '\n')

#when change in directory is detected
def on_modified(event):
  global instance
  global duplicate_check
  global instance
  if os.path.exists(incoming_message_directory_path+'/msg.txt'): #see if the msg.txt file is there
    with open(incoming_message_directory_path+'/msg.txt', "r") as f:
      last = f.readline()
    if "@@msg" in last:
      #print("MESSAGE RECEIVED:"+last.strip("\n"))#this is the message we received
      os.system('rm '+incoming_message_directory_path+'/msg.txt')#remove the msg.txt file

      print_rcv(last.strip('\n'))

      tt = last.strip("\n").split("@#@")[2].split("_")[0]
      if tt == instance:#we keep this message
        print_c("Message is at its final destination")
      else: #this message needs to be forwarded
        if instance == 'delay':
          #print("Sending to process_msg for forwarding")i
          process_msg(last)
        else:
          with open(msg_queue_path, "a") as ft:
            ft.write("\n"+last)
    if "@@file" in last:

      print_rcv(last.strip('\n'))
      #print("FILE RECEIVED:"+last.strip("\n"))
      if os.path.exists(incoming_message_directory_path+'/msg.txt'):
        os.system('rm '+incoming_message_directory_path+'/msg.txt')#remove the msg.txt file
      tt = last.strip("\n").split("@#@")[2].split("_")[0]
      if tt == instance:#we keep this file
        print_c("File is at its final destination")
      else: #this message needs to be forwarded
        if instance == 'delay':
          #print("Sending to process_msg for forwarding")
          process_msg(last)
        else:
          with open(msg_queue_path, "a") as ft:
            ft.write("\n"+last)
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
    #print("SAME NODE") 
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
  #print("CONNECTING PATH DOES NOT EXIST")
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
  f.write("e 0\n")
  f.write("w 0\n")
  f.write("a entity "+current_eid+" bp ipn:"+current_eid+".0 7 0 0\n")
  f.write("m discard\n")
  f.write("m segsize 100000\n")
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
sleep(2)
os.system('clear')



print("                                   __    _         ___")
print("       /\/\\   __ _ _ __ ___   /\\  / /___| |_      / __\\")
print("      /    \\ / _` | '__/ __| /  \\/ / _ \\ __|____ / /")
print("     / /\\/\\ \\ (_| | |  \\__ \\/ /\\  /  __/ ||_____/ /___")
print("    /_/    \\_\\__,_|_|  |___/_/  \\/ \\___|\__|    \\____/\n")

print("    Welcome to the MarsNet-C Platform - By Team Spatiam \n\n")

print("Communications Begin Here \n")



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
    for i in range(len(path_list)):
      if path_list[i] == instance:
        sendTo=nodes_eid[nodes.index(path_list[i+1])]
        with open('msg.txt', "w") as fw:
          fw.write("@@file@#@"+ts+"@#@"+tgt+"@#@"+frm+"@#@"+filename+"@#@0\n")
        #print("bpcp "+incoming_message_directory_path+"/"+filename+" "+sendTo+":"+incoming_message_directory_path+"/"+filename)
        
        print_snd("@@file@#@"+ts+"@#@"+tgt+"@#@"+frm+"@#@"+filename+"@#@")
        os.system("bpcp "+incoming_message_directory_path+"/"+filename+" "+sendTo+":"+incoming_message_directory_path+"/"+filename)
        os.system('rm '+incoming_message_directory_path+"/"+filename)
        #print("bpcp msg.txt "+sendTo+":"+incoming_message_directory_path+"/msg.txt")
        os.system("bpcp msg.txt "+sendTo+":"+incoming_message_directory_path+"/msg.txt")
        if os.path.exists(incoming_message_directory_path+'/msg.txt'):
          os.system('rm '+incoming_message_directory_path+'/msg.txt')#remove the msg.txt file
    print(style.RESET+style.CYAN+"Forwarding Path -> "+str(path_list)+style.RESET)
        
def send_message(message, ts, tgt, frm, entire):
  global graph
  global instance
  global nodes
  global nodes_eid
  global incoming_message_directory_path
  tgt_eid = tgt.split("_")[0]
  path_list = BFS_SP(graph, instance, tgt_eid)
  if len(path_list) != 0:
    for i in range(len(path_list)):
      if path_list[i] == instance:
        sendTo=nodes_eid[nodes.index(path_list[i+1])]
        with open('msg.txt', "w") as fw:
          fw.write("@@msg@#@"+ts+"@#@"+tgt+"@#@"+frm+"@#@"+message+"@#@0\n")
        #print("bpcp msg.txt "+sendTo+":"+incoming_message_directory_path+"/msg.txt")
        print_snd("@@msg@#@"+ts+"@#@"+tgt+"@#@"+frm+"@#@"+message+"@#@")
        os.system("bpcp msg.txt "+sendTo+":"+incoming_message_directory_path+"/msg.txt")
    print(style.RESET+style.CYAN+"Forwarding Path -> "+str(path_list)+style.RESET+"\n\n")

  else:
    print(style.RESET+style.RED+"Path not found"+style.RESET)

def pwf_processor():
    global FWD_QUEUE
    global incoming_message_directory_path
    queue_file = open('queue_p.txt', 'w')
    ephemeris_file = open('delay_queue.txt', 'r') 
    lines = ephemeris_file.readlines() 
    processing_msg = False
    queueLines = ''
    for line in lines: 
        if line.startswith('#beg#'):
            processedLines = line
            processing_msg = True
            info = line.rstrip('\n')[5:].split(' ')
            source = info[0]
            target = info[1]
            msg_type = info[2]
            msg_timestamp = info[3]
            line_num = 0
        elif line.startswith('#end#'):
            processedLines += line
            processing_msg = False
            line_num = 0
            send_date_str = info = line.rstrip('\n')[5:]
            send_date = datetime.strptime(send_date_str,'%d-%b-%Y(%H:%M:%S.%f)')
            now = datetime.now()
            if now > send_date:
                if msg_type == 'msg':
                    # send 'content' to 'sender' from 'receiver'
                    fwd_msg = '@@msg@#@'+msg_timestamp+'@#@'+target+'@#@'+source+'@#@'+content+'@#@0'
                    #TODO
                    #print(fwd_msg)
                    fwd_queue = open(FWD_QUEUE, 'a')
                    fwd_queue.write(fwd_msg)
                    fwd_queue.close()
                elif msg_type == 'file':
                    if(path.exists(incoming_message_directory_path+"/"+content)):
                        # send 'content' to 'sender' from 'receiver'
                        fwd_msg = '@@file@#@'+msg_timestamp+'@#@'+target+'@#@'+source+'@#@'+content+'@#@0'
                        #TODO
                        #print(fwd_msg)
                        fwd_queue = open(FWD_QUEUE, 'a')
                        fwd_queue.write(fwd_msg)
                        fwd_queue.close()
                    else:
                        queueLines += processedLines
            else:
                queueLines += processedLines
        elif processing_msg:
            processedLines += line
            if line_num == 0:
                content = line.rstrip('\n')
                line_num = 1
            else:
                content += '\n' + line.rstrip('\n')
    queue_file.write(queueLines)
    queue_file.close()
    ephemeris_file.close()
    os.system('cp queue_p.txt delay_queue.txt')
    os.system('rm queue_p.txt')

def menu_thread():
  while 1:
    sleep(2)
    for user in users:
      after_files = dict ([(f, None) for f in os.listdir(USERS_DIR + user + '/' + UPLOAD_DIR)])
      added_files = [f for f in after_files if not f in filedict[user]]

      if added_files: 
        for file in added_files:
          lst_file(user, file)

      after_files = dict ([(f, None) for f in os.listdir(USERS_DIR + user + '/' + UPLOAD_DIR)])

      old_mod = msg_dict[user]
      new_mod = os.path.getmtime(USERS_DIR + user + '/' + MSG_FILE_NAME)

      if new_mod > old_mod:
        msg_dict[user] = new_mod
        lst_msg(user)
      filedict[user] = after_files

def fwd_processor():
  while(True):
    sleep(1)
    pwf_processor()

messageQueue=threading.Thread(target=message_queue_listener)
fwdProcessor=threading.Thread(target=fwd_processor)
menuThread=threading.Thread(target=menu_thread)
messageQueue.start()
fwdProcessor.start()
menuThread.start()
