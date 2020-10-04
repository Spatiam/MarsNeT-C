import os
import sys
from time import sleep
import os.path
from os import path
import socket
import threading
import subprocess
from datetime import datetime

# Constants
MARS = '3'
EARTH = '1'

# Intial dict
ephemeris = {1: {3: 0.0}, 3: {1: 0.0}}

# Open and read file
ephemeris_file = open('Ephemeris/mars-earth-ephemeris.txt', 'r') 
lines = ephemeris_file.readlines() 

today = datetime.today()
#today = datetime.strptime('2020-Oct-09-06:00', '%Y-%b-%d-%H:%M')

body_1 = 0
body_2 = 0

count = 0
values = []
for line in lines: 
    if count == 0:
        bodies = line.split('-')
        body_1 = int(bodies[0])
        body_2 = int(bodies[1])
    else:
        line_values = line.rstrip('\n').split(' ')
        clean_data = []
        for value in line_values:
            if not (value == ''):
                clean_data.append(value)
        values.append(clean_data)
    count += 1
ephemeris_file.close()

added = False
final_delay = 0
delay = 0
for value in values:
    if(not added):
        date_str = value[0] + '-' + value[1]
        date = datetime.strptime(date_str, '%Y-%b-%d-%H:%M')

        if(date > today):
            added = True
            ephemeris[body_1][body_2] = float(delay)
            ephemeris[body_2][body_1] = float(delay)
            final_delay = delay
        else:
            delay = value[2]


f = open('Ephemeris/mars-earth-delay.txt', 'w')
f.write(final_delay)
f.close()
