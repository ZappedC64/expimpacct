# Import users on linux from exported files
import grp
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
    if user in pwd_slst:
        flag = 1
        return flag
    else:
        flag = 0
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


# Load existing passwd file into memory
spwdfile_lst = []
spwd_slst = []
with open('/etc/passwd', 'r') as fpwd_orig:
    for line in fpwd_orig:
        line = line.strip()
        spwdfile_lst.append(line)
for line in spwdfile_lst:
    spwd_lst = line.split(':')
    spwd_slst.append(spwd_lst)

# Check for and create groups with more than one member.
# This has to be done ahead of time of the useradd will fail.
igrpfile_lst = []
with open('group_mig.txt', 'r') as fgrp_imp:
    for line in fgrp_imp:
        line = line.strip()
        line = line.split(':')
        igrpfile_lst.append(line)
for group in igrpfile_lst:
    if group[3]:
        group_name = group[0]
        group_memcount = group[3]
        group_memcount = str(len(group_memcount.split(',')))
        print '[ ' + group_name + ' ]' + ' has ' + group_memcount + ' members.'
        # Read local server's existing groups
        try:
            gr_data = grp.getgrnam(group[0])
        except KeyError:
            print "[ {} ] Group does not exist.  Creating...".format(group[0])
            command = ['groupadd', str(group[0])]
            process = subprocess.Popen(command, stdout=subprocess.PIPE)
            output, error = process.communicate()

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
        if not pwd_lst[0] in spwd_slst:
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
