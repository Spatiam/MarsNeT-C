import os, time

USERS_DIR = 'Users/'
UPLOAD_DIR = 'UploadFiles/'
MSG_FILE_NAME = 'msg_log.txt'

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

def send_file(user, file):
    print('Added: ' + str(file))
    #os.system('mv ' + user + '/' + UPLOAD_DIR + file +' SentFiles')

def process_msg(user):
    print('Modified: ' + user + '\'s message log')
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