# expimpacct
Scripts to export Linux user accounts from one server and import on another

I wrote these Python scripts to export the user accounts from a Red Hat 7 Linux server and import on another.  I had to write these scripts for Python 2.7
because Red Hat 7 still uses the old Python 2.7 and I am not allowed to install or update software on production servers.

I'm a Python noob so please excuse any bad programming techniques. I'm learning as I find programs that I need.

To do:
- Encrypt/Password protect the exported tar file
- Backup destination server's existing /etc/{passwd/group/shadow} files
- Add more text to the program as it runs

