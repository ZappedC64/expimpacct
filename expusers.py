#! /usr/bin/env python
# Script to export users from an existing system
import os, os.path
import sys
import tarfile


# Must be run as root.
if not os.geteuid() == 0:
    sys.exit('This script must be run as root (or sudo)!')


def info_message(txtmessage):
    print(txtmessage, end='')


def ok_message():
    print(" [ OK ]")


# Open the password, group, and shadow files
# and store their contents in lists
info_message("Reading passwd file...")
with open('/etc/passwd') as fpwd:
    fpwdfile = fpwd.readlines()
    ok_message()
info_message("Reading group file...")
with open('/etc/group') as fgrp:
    fgrpfile = fgrp.readlines()
    ok_message()
info_message("Reading shadow file...")
with open('/etc/shadow') as fsha:
    fshafile = fsha.readlines()
    ok_message()

# Strip out newlines
fpwdfile = [x.strip() for x in fpwdfile]
fgrpfile = [x.strip() for x in fgrpfile]
fshafile = [x.strip() for x in fshafile]

# Parse the password file. Grab only UIDs between 500 and 65534
info_message("Parsing passwd file. Looking for accounts with UID's >= 500...")
countl = 0
pwdlist = []
for line in fpwdfile:
    countl += 1
    fpwdsplit = (line.split(':'))
    uidval = int(fpwdsplit[3])
    if 1000 <= uidval < 65534:
        pwdlist.append(line)
        # Write the output to a new file
        with open('passwd_mig.txt', "a") as fpwd_write:
            for item in pwdlist:
                fpwd_write.write(item + "\n")
ok_message()

# Parse the group file. Grab only GIDs between 1000 and 65534
info_message("Parsing group file. Looking for accounts with GID's >= 500...")
countl = 0
grplist = []
for line in fgrpfile:
    countl += 1
    fgrpsplit = (line.split(':'))
    uidval = int(fgrpsplit[2])
    userstr = str(fgrpsplit[0])
    if 1000 <= uidval < 65534:
        grplist.append(line)
        # Write the output to a new file
        with open('group_mig.txt', "a") as fgrp_write:
            for item in grplist:
                fgrp_write.write(item + "\n")
                ok_message()
                # Create and write new shadow file
                info_message("Parsing shadow file. Looking for accounts that match the UIDs...")
                with open('shadow_mig.txt', 'a') as fsha_write:
                    # Match only the line in the shadow file that matches the user
                    filter_object = filter(lambda a: userstr in a, fshafile)
                    strshad = ''.join(filter_object)
                    fsha_write.write(strshad + '\n')
                    ok_message()

# Tar it all up
with tarfile.open("user_export.tgz", "w:gz") as tar:
    info_message('Creating tar archive...')
    for file in ["passwd_mig.txt", "group_mig.txt", "shadow_mig.txt"]:
        tar.add(os.path.basename(file))
ok_message()

# Cleanup
info_message('Cleaning up temp files...')
if os.path.exists("passwd_mig.txt"):
    os.remove("passwd_mig.txt")
if os.path.exists("group_mig.txt"):
    os.remove("group_mig.txt")
if os.path.exists("shadow_mig.txt"):
    os.remove("shadow_mig.txt")
ok_message()
