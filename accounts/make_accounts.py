## This script uses Pickle to import a
# dictionary of xmpp accounts/passwords
# from a file named sqmail_accounts.p
# in the local directory. Using the data
# in this dictionary, the script writes
# (to stdout) a series of shell
# statements to register the included users
# on their respective email servers.

import pickle
import sys

try:
    accounts = pickle.load( open( "sqmail_accounts.p", "rb" ) )
except:
    print("ERROR: Unable to load accounts dictionary from ./sqmail_accounts.p")
    sys.exit(1)
servers = set()
for account in accounts.keys():
    servers.add(str(account).split('@')[1])
    #print(list(servers))
    
for server in servers:
    print('\nAccounts for ' + server + ':')
    for account in accounts.keys():
        user = str(account).split('@')[0]
        domain = str(account).split('@')[1]
        if domain == server:
            print('sudo adduser --disabled-password ' + user + "; echo '" + user + ":" + accounts[account] + "' | sudo chpasswd")
