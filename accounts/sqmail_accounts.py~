################################################
# This script creates a Python dictionary      #
# containing the specified (below) number      #
# of JIDs and randomly-generated passwords,    #
# with user names randomly selected from a     #
# file of names provided in a file 'names.txt' #
# in the current directory.                    #
# The dictionary is then written to a Pickle   #
# file in the present working directory.       #
################################################
import string
import random
import pickle

# What are the names of the XMPP servers?
servers = ['davis.26maidenlane.net','reno.26maidenlane.net']
# How many accounts per server (left-to-right)?
num_accounts = [50, 50]
# How long should account passwords be?
password_length = 8

def make_passwords(n, x):
    'Create n random passwords, each containing x characters'
    letters = [x for x in string.ascii_letters]
    digits = [x for x in string.digits]
    chars = letters + digits
    passwords = []
    for _ in range(n):
        passwords.append(''.join([random.choice(chars) for i in range(x)]))
    return passwords

def get_names(n):
    'Selects n random names from file "names.txt" in current directory'
    all_names = []
    names = set()
    try:
        f = open('names.txt')
        for line in f:
            name = line.strip()
            all_names.append(name.lower())
        f.close()
    except:
        print("ERROR: Can't open and or read file ./names.txt")
        return []
    while len(names) < n:
        names.add(random.choice(all_names))
    return list(names)

def make_accounts(names, passwords, num_accounts, servers):
    'Create a dictionary of accounts:passwords from inputs'
    # First, do some sanity checks on the inputs
    if len(names) != len(passwords):
        print("Error: The number of passwords doesn't match the nunber of names.")
        return
    if len(names) != sum(num_accounts):
        print("Error: Count of names doesn't match count of accounts.")
        return
    # Build the account dictionary
    accounts = {}
    j = 0
    offset = 0
    for i in range(len(servers)):
        while j < offset + num_accounts[i]:
            accounts[names[j] + '@' + servers[i]] = passwords[j]
            j += 1
        offset += num_accounts[i]
    return accounts

if __name__=='__main__':
    names =  get_names(sum(num_accounts))
    if len(names):
        passwords = make_passwords(sum(num_accounts), password_length)
        accts = make_accounts(names, passwords, num_accounts, servers)
        pickle.dump( accts, open( "xmpp_accounts.p", "wb" ) )
        print('Created a total of', len(accts), 'accounts')
        print('Dictionary of accounts saved to file "./xmpp_accounts.p"')

