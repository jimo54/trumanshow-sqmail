#!/usr/bin/python
###########################
# To use Lorem ipsum sentence generator:
#    Install setuptools:
#       sudo apt-get install python-setuptools
#    Go to: https://pypi.python.org/pypi/loremipsum/
#       Download the tar ball
#       Extract
#       Run setup program:
#          sudo python setup.py install
###########################
import threading, time, pickle, sys, logging
from sqmail_home import SQMail

#people = ['dwhite@carbonfiberanvils.com','jroberge@glasshammersinc.com','jbrown@pha.com','rmoore@pha.com','ttekelenburg@carbonfiberanvils.com','dgoodale@glasshammersinc.com','drichard@glasshammersinc.com','asciarra@carbonfiberanvils.com','edrummond@carbonfiberanvils.com','rignaciuk@pha.com','tbeal@pha.com','cdrexel-harmon@glasshammersinc.com','dplourde@carbonfiberanvils.com','cbouchard@pha.com','jkiehn@glasshammersinc.com']

## Set up logging
# Create logger
logger = logging.getLogger('testsqmail.py')
logger.setLevel(logging.INFO)
# Create a logging handler. Take your choice
# of a console (stream) for file handler
ch = logging.StreamHandler()
#ch = logging.FileHandler('testsqmail.log')
# Add logging formatter
formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(\
message)s', '%b %e %H:%M:%S')
# Add formatter to logging handler
ch.setFormatter(formatter)
# Add logging handler to logger object
logger.addHandler(ch)

# Set class variables for the logger and list of people
SQMail.logger = logger
#SQMail.people = people

# The list of sqmail agents is created by a script in
# the accounts directory, named sqmail_accounts.py. This
# script then stores a Python dictionary of email addresses
# and their associated passwords in a Python pickle
# file: accounts/sqmail_accounts.p.
try:
    agentList = pickle.load(open('accounts/sqmail_accounts.p', 'rb'))
except Exception as e:
    logger.critical('Error: Can\'t open and/or read accounts/sqmail_accounts.p '+ e)
    sys.exit(1)

## Create some agent threads as follows
agents = []
for agent in agentList:
    user, host = agent.split('@')
    passwd = agentList[agent]
    try:
        logger.info('Spawning thread for ' + agent)
        group = None
        agents.append(SQMail(host,user,passwd,logger,group))
        agents[-1].start()
    except Exception as e:
        logger.critical('Error: unable to start thread for ' + user + '@' + host + ': ' + e)
while True:
    try:
        time.sleep(30)
    except KeyboardInterrupt:
        logger.info('Received kill signal, so exiting')
        for agent in agents:
            agent.stop()
        for agent in agents:
            agent.join()
        sys.exit(0)
