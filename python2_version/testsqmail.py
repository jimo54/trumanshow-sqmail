#!/usr/bin/python
import thread, time
from sqmail import SQMail

server1 = 'webmail.glasshammersinc.com'
server2 = 'webmail.pha.com'
server3 = 'webmail.carbonfiberanvils.com'

agentList = {'hannah@'+server1: 'bagjms6a', 'ella@'+server1: 'afwtl7j4', 'joseph@'+server1: 'xutxehdd', 'ava@'+server1: 'ftgadqvl', 'victoria@'+server1: 'pttktw42', 'sophia@'+server1: 'famwzxe2', 'zoey@'+server2: 'qndjgbt3', 'liam@'+server1: '7nfun5em', 'charlotte@'+server1: '6bgkmjfn', 'natalie@'+server1: 'uc4r5ck8', 'michael@'+server2: 'abpwlsud', 'isabella@'+server2: 'ruftsefb', 'david@'+server1: 'a22q6drp', 'olivia@'+server1: 'ryex5cw2', 'chloe@'+server2: 'ht9czbxz', 'joshua@'+server2: 'nse9jg4k', 'logan@'+server2: 'd8hlynaq', 'lucas@'+server2: '2hpa92zw', 'emma@'+server2: 'kbsemhzg', 'daniel@'+server1: 'uutg3zbt', 'abigail@'+server2: 'rlez4xd8', 'andrew@'+server1: 'uakmbr33', 'william@'+server2: '3hkkp8xt', 'elijah@'+server2: 'drtkybpu', 'sofia@'+server1: 'eyvwbunb', 'james@'+server2: 'buahehfk', 'alexander@'+server1: '6tvmhfu6', 'anthony@'+server2: 'ntwqhace', 'grace@'+server2: 'zsxhwdhj', 'ethan@'+server1: 'wnz7s7gr', 'aiden@'+server1: 'ngcy4zvy', 'emily@'+server1: 'zha7utjl', 'jackson@'+server1: 's79jvucp', 'addison@'+server1: 'yytezmrb', 'aubrey@'+server2: 'u36fnreq', 'jayden@'+server2: 'veynzak6', 'madison@'+server1: 'kkgez8uy', 'mia@'+server2: 'uysjzwdr', 'harper@'+server2: 'vyx4uaz7', 'mason@'+server1: 'kmmfvqva', 'benjamin@'+server1: '2ekvwjp7', 'gabriel@'+server1: 'rdqp9qsq', 'amelia@'+server1: '2d9hvmkp', 'jacob@'+server2: 'sgwnd9km', 'evelyn@'+server2: '88ctr5py', 'elizabeth@'+server2: 'asdjswcv', 'avery@'+server2: 'pzljljjh', 'samuel@'+server2: '6bfdzq76', 'noah@'+server2: 'f7eclstk', 'matthew@'+server2: 'vdcukvuk','ryan@'+server3: 'yNQcpKtu', 'john@'+server3: '3G5tkS5n', 'brooklyn@'+server3: 't2rXPKK8', 'allison@'+server3: 'xRKCgaGt', 'landan@'+server3: 'ZtLqA7QK', 'carter@'+server3: '6fcscNXZ', 'savannah@'+server3: 'zzaTafzT', 'gabriella@'+server3: 'sXMTJUux', 'samantha@'+server3: 'VXsFp9SG', 'hunter@'+server3: 'B248JY3K', 'anna@'+server3: 'Wh9u2Y26', 'zoe@'+server3: 'MrDUqKxk', 'isaac@'+server3: 'tkZGfGZQ', 'nathan@'+server3: 'LPTV6EeT', 'audrey@'+server3: 'mdSKnDkg', 'layla@'+server3: 'ZRM4tZma', 'caleb@'+server3: 'TAgjbgfK', 'camilla@'+server3: 'NJq2vZsF', 'aaliyah@'+server3: 'QcSZ8djM', 'lily@'+server3: 'TtLnBcRR', 'luke@'+server3: 'G4eUK4tD', 'christian@'+server3: 'GK7pfvRP', 'owen@'+server3: 'qBxpNcpr', 'leah@'+server3: 'LMWCWRGQ', 'henry@'+server3: 'Eg8JWWRJ', 'christopher@'+server3: 'ucsYpNbd', 'dylan@'+server3: 'fUkdTx5X'}

# Create some agent threads
for agent in agentList:
    user, host = agent.split('@')
    passwd = agentList[agent]
    try:
        print 'Spawning thread for ' + agent + '...',
        thread.start_new_thread( SQMail, (host,user,passwd, ) )
        print 'Success!'
    except:
        print 'Error: unable to start thread for ' + agent
while True:
    time.sleep(30)

