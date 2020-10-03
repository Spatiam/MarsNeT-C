import os
import sys
from time import sleep
import os.path
from os import path
import socket
import threading
import subprocess
from datetime import datetime, timedelta


id2ip = {'1': '', '2': ''}
ip2id = {'1': '', '2': ''}

#message = '@@msg@#@{timestamp}@#@{targetIP}@#@{currentIP}@#@{message}'
#message2 = '@@file@#@{filename}@#@{timestamp}@#@{targetIP}@#@{currentIP}'

message = '@@msg@#@20:20@#@123.123.123.123@#@321.321.321.321@#@this is my message hello.'
message2 = '@@file@#@hello.txt@#@18:18@#@123.123.123.123@#@321.321.321.321'

def process_msg(in_msg):

    os.system('cd ../Ephemeris/;python3 ephemerisMars.py;cd ../MessageProcessing')
   
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

    queue = '#beg#' + msg_sender_ip + ' ' + msg_target_ip + ' ' + msg_type +'\n'
    queue += msg_content + '\n'
    queue += '#end#' + send_str + '\n'
            
    f = open('queue.txt', 'a')
    f.write(queue + '\n')
    f.close()

process_msg(message)
process_msg(message2)