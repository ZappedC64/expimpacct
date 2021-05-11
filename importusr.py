# Import users on linux from exported files
import os
import subprocess
import sys
import shutil
from datetime import datetime

# Must be run as root or sudo.
if not os.geteuid() == 0:
    sys.exit('This script must be run as root (or sudo)!')

# Backup existing files
print 'Backing up existing files... ',
try:
    backup_date = datetime.now().strftime('%Y%m%d%H%M%S')
    str_passwd = '/etc/passwd'
    str_group = '/etc/group'
    str_shadow = '/etc/shadow'
    shutil.copy2(str_passwd, str_passwd + '.' + backup_date + '.bak' )
    shutil.copy2(str_group, str_group + '.' + backup_date + '.bak' )
    shutil.copy2(str_shadow, str_shadow + '.' + backup_date + '.bak' )
    print '[ OK ]'
except Exception, e:
    print '[ ERROR ]'
    sys.exit(1)


# Check if the user already exists in the /etc/passwd file
def pwd_check(user):
    with open('/etc/passwd', 'r') as fpwd_orig:
        fpwdfile = fpwd.readlines()
        flag = 0
        index = 0
        for pline in fpwd_orig:
            index += 1
            if str(user) in pline:
                flag = 1
                break
        return flag


# Replace the blank password with the hashed password from the source server
def upd_pwd(user, shdpw):
    replace_str = user + ':!'
    new_str = user + ':' + shdpw
    # Read the shadow password fie
    with open('/etc/shadow', 'r') as fshd_origup:
        fshdfile = fshd_origup.read()
    # Replace the old blank password
    fshdfile = fshdfile.replace(replace_str, new_str)
    # Write the shadow file back out
    with open('/etc/shadow', 'w') as fshd_origup:
        fshd_origup.write(fshdfile)


# Open exported passwd file and read the users
with open('passwd_mig.txt', 'r') as fpwd:
    for cnt, line in enumerate(fpwd):
        pwd_lst = line.split(':')
        # Open the exported shadow file - Need the hashed password
        with open('shadow_mig.txt', 'r') as fshd:
            flag = 0
            index = 0
            for sline in fshd:
                index += 1
                if str(pwd_lst[0]) in sline:
                    flag = 1
                    break
            if flag == 0:
                print "[ ERROR ]: Password for user {}, not found.".format(pwd_lst[0])
                exit(1)
            else:
                shd_lst = sline.split(':')
                # print "Password for user {}, is: {}.".format(pwd_lst[0], shd_lst[1])
        # Open the exported group file - Need the users groups
        with open('group_mig.txt', 'r') as fgrp:
            flag = 0
            index = 0
            for gline in fgrp:
                index += 1
                grp_lst = gline.split(':')
                if str(pwd_lst[0]) in grp_lst[0]:
                    flag = 1
                    break
            if flag == 0:
                print "[ ERROR ]: Group for user {}, not found.".format(pwd_lst[0])
                exit(1)
            else:
                shd_lst = sline.split(':')
                # print "Group for user {}, is: {}.".format(pwd_lst[0], grp_lst[2])
        # Make sure user doesn't already exist
        if pwd_check(pwd_lst[0]) == 0:
            print "Creating user... {}".format(pwd_lst[0])
            command = ['useradd',
                       '-d', pwd_lst[5],
                       '-u', pwd_lst[2],
                       '-s', pwd_lst[6],
                       '-G', pwd_lst[7].rstrip(),
                       '-m',
                       pwd_lst[0]]
            process = subprocess.Popen(command, stdout=subprocess.PIPE)
            output, error = process.communicate()
            upd_pwd(pwd_lst[0], shd_lst[1])
        else:
            print "User exists... Skipping."
