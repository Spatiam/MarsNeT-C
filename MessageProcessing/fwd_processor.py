import os
import sys
from time import sleep
import os.path
from os import path
import socket
import threading
import subprocess
from datetime import datetime, timedelta

msg = '@@msg@#@20:20@#@123.123.123.123@#@321.321.321.321@#@this is my message hello.'

def pwf_processor():

    queue_file = open('queue_p.txt', 'w')

    ephemeris_file = open('queue.txt', 'r') 
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
            msg_timesatmp = info[3]
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
                    fwd_msg = '@@msg@#@'+msg_timesatmp+'@#@'+target+'@#@'+source+'@#@'+content+'@#@0'
                    print(fwd_msg)
                    fwd_queue = open('fwd_queue.txt', 'a')
                    fwd_queue.write()
                    fwd_queue.close()

                elif msg_type == 'file':

                    if(path.exists('../FileQueue/'+content)):
                        # send 'content' to 'sender' from 'receiver'
                        fwd_msg = '@@file@#@'+content+'@#@'+msg_timestamp+'@#@'+target+'@#@'+source+'@#@0'
                        print(fwd_msg)
                        fwd_queue = open('fwd_queue.txt', 'a')
                        fwd_queue.write()
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

    os.system('cp queue_p.txt queue.txt')
    os.system('rm queue_p.txt')

pwf_processor()
