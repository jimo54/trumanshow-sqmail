# trumanshow-sqmail/accounts
Python scripts and other files used to create user accounts for virtual user agents.

## Files
**README.md:** This file

**make_accounts.py:** This script uses the Python Pickle library to import a dictionary of usernames/passwords from a file named sqmail_accounts.p in the local directory. (The pickle file can be created with the sqmail_accounts.py script also contained in this directory.) Using the data in this dictionary, the script writes (to stdout) a series of shell statements that can be used to create accounts on the respective email servers.

**names.txt:** A file containing +/- 600 popular first names. This file is used by the included sqmail_accounts.py script as a source for randomly-selected usernames.

**sqmail_accounts.p:** A Python pickle file written by the sqmail_accounts.py scripts, containing a dictionary of usernames/passwords.

**sqmail_accounts.py:** This script creates a Python dictionary containing a specified number of usernames and randomly-generated passwords, with usernames randomly selected from a file of names provided in a file 'names.txt' in the present working directory (pwd). The dictionary is then written to a Pickle file named sqmail_accounts.p in the pwd.

## Installation
These scripts use only Python 3 standard libraries. No additional installation steps are required.

## Configuration and Use
Use the sqmail_accounts.py script to generate any number of user accounts for the email servers. Beforehand, the fully-qualified domain name for each email server, the numbers of accounts to be generated for each server, and the desired length of the randomly generated passwords must be set. These parameters should be entered in the first few lines of the sqmail_accounts.py script. When the script is run, the user account information will be written to a Python pickle file named sqmail_accounts.p in the present working directory.

After the sqmail_accounts.p has been written to disk, the make_accounts.py script can be used to generate the shell statements necessary to create the user accounts on their respective servers. By default, these statements are written to the display. For convenience's sake, the statements are grouped by server host name.


