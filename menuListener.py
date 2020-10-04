import os, time
from datetime import datetime

USERS_DIR = 'Users/'
UPLOAD_DIR = 'Uploads/'
MSG_FILE_NAME = 'msg_log.txt'
THIS_USER = 'Houston'
FWD_DIR='ion-open-source-3.7.1/dtn/incoming/'
FWD_QUEUE='ion-open-source-3.7.1/dtn/msg_queue.dat'
user_dict={'Houston':'earth_user','Rover':'rover_user', 'Delay':'delay_user', 'Mars':'mars_user' }
filedict = {}
msg_dict = {}
users = os.listdir('Users/')
for user in users:
    if user[0:1] == '.':
        users.remove(user)
print(users)
for user in users:
    msg_dict[user] = os.path.getmtime(USERS_DIR + user + '/' + MSG_FILE_NAME)
    filedict[user] = dict ([(f, None) for f in os.listdir(USERS_DIR + user + '/' + UPLOAD_DIR)])

def lst_file(user, file):
    print('Added: ' + str(file))
    file_path = USERS_DIR + user + '/' + UPLOAD_DIR + file
    os.system('mv ' + file_path + ' ' + FWD_DIR)
    print('mv ' + file_path + ' ' + FWD_DIR)
    now = datetime.now()
    date_str = now.strftime("%d-%b-%Y(%H:%M)")
    str_queue = '@@file@#@'+date_str+'@#@'+user_dict[user]+'@#@'+ user_dict[THIS_USER] +'@#@'+file+'@#@0'
    queue_file = open(FWD_QUEUE,'a')
    queue_file.write(str_queue)
    print('queued:' + str_queue)
    queue_file.close()
    filedict[user] = os.path.getmtime(USERS_DIR + user + '/' + MSG_FILE_NAME)

def lst_msg(user):
    print('Modified: ' + user + '\'s message log')
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
    date_str = now.strftime("%d-%b-%Y(%H:%M)")
    str_queue = '@@msg@#@'+date_str+'@#@'+user_dict[user]+'@#@'+ user_dict[THIS_USER] +'@#@'+content+'@#@0'
    queue_file = open(FWD_QUEUE,'a')
    queue_file.write(str_queue)
    print('queued:' + str_queue)
    queue_file.close()
    filedict[user] = os.path.getmtime(USERS_DIR + user + '/' + MSG_FILE_NAME)

while 1:
    time.sleep(2)
    for user in users:
        after_files = dict ([(f, None) for f in os.listdir(USERS_DIR + user + '/' + UPLOAD_DIR)])
        added_files = [f for f in after_files if not f in filedict[user]]

        if added_files: 
            for file in added_files:
                send_file(user, file)

        after_files = dict ([(f, None) for f in os.listdir(USERS_DIR + user + '/' + UPLOAD_DIR)])

        old_mod = msg_dict[user]
        new_mod = os.path.getmtime(USERS_DIR + user + '/' + MSG_FILE_NAME)

        if new_mod > old_mod:
            msg_dict[user] = new_mod
            process_msg(user)
        filedict[user] = after_files
