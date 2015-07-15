#!/usr/bin/env python
import os, sys, re, socket, time, random
import httplib2, threading
from urllib.parse import urlencode
from loremipsum import get_sentences
####################################################################
# This script requires the fortune-mod package to be installed     #
# on the local system:                                             #
#    sudo apt-get install fortune-mod                              #
# To use Lorem ipsum sentence generator:                           #
#    Install setuptools:                                           #
#       (For Python 2) sudo apt-get install python-setuptools      #
#       (For Python 3) sudo apt-get install python3-setuptools     #
#    Go to: https://pypi.python.org/pypi/loremipsum/               #
#       Download the tar ball                                      #
#       Extract and cd into new directory                          #
#       Run setup program:                                         #
#          (For Python 2) sudo python setup.py install             #
#          (For Python 3) sudo python3 setup.py install            #
####################################################################

class SQMail(threading.Thread):
    'A class that interacts with a Squirrelmail email app server'
    send_prob = 0.1
    minDelay = 10
    maxDelay = 30
    def __init__(self, host, user, password, run=False):
        'Constructor creates an Squirrelmail user'
        super().__init__()
        self.host = host
        self.user = user
        self.whoami = user + '@' + host
        self.password = password
        self.http = httplib2.Http()
        self.url = 'http://' + host + '/squirrelmail/src/'
        self.loggedin = False
        self.roster = self._build_roster()
        self.new_msgs = []
        self.all_msgs = []
        self.sent_msgs = []

    def run(self):
        delay = random.randint(SQMail.minDelay, SQMail.maxDelay)
        while not shutdown_event.is_set():
            try:
                self.login()
                if len(self.all_msgs) > 0:
                    if len(self.all_msgs) > 10:
                        self.del_all_msgs()
                    else:
                        self.read_msg()
                time.sleep(delay)
                r = random.randint(1,101)
                p = int(1 / SQMail.send_prob)
                if r % p == 0:
                    self.read_new_msgs()
                    to = random.choice(self.roster)
                    self.send_msg(to)
                    print(time.strftime("%H:%M:%S") + ': ' + self.whoami + ' sent email to', to)
            except Exception as e:
                print('Whoops!: %s' % e)
        print(self.whoami + ' logging out...', end='')
        self.logout()
        print('bye!')

    def read_new_msgs(self):
        '"Reads" all unread messages in the user\'s INBOX'
        if len(self.new_msgs) == 0 or self.loggedin == False:
            return
        print(time.strftime("%H:%M:%S") + ': ' + self.whoami + ' is reading new messages.')
        for msg in self.new_msgs:
            myurl = self.url + msg
            response, content = self.http.request(myurl, 'GET', headers=self.headers)
            time.sleep(random.randint(10,30))
        self.new_msgs = []

    def read_msg(self):
        '"Reads" one randomly-selected message from INBOX'
        if len(self.all_msgs) == 0 or self.loggedin == False:
            return        
        msg = random.choice(self.all_msgs)
        myurl = self.url + msg
        response, content = self.http.request(myurl, 'GET', headers=self.headers)
        if msg in self.new_msgs:
            self.new_msgs.remove(msg)        

    def _build_roster(self):
        allUsers = list(agentList.keys())
        roster = []
        max = random.randint(4,9)
        count = 0
        while count <= max:
            test = random.choice(allUsers)
            if test != self.whoami and test not in roster:
                roster.append(test)
                count += 1
        return roster
        
    def _get_inbox_links(self, inboxlinks):
        'A private method to extract message links from INBOX'
        if self.loggedin == False:
            return None, None
        inbox = inboxlinks.decode()
        all_msgs = []
        new_msgs = []
        p1 = re.compile('<b><a href=\"read_body.php\?mailbox=INBOX&amp;passed_id\=[0-9]+&amp;startMessage=1', re.IGNORECASE)
        p2 = re.compile('read_body.php\?mailbox=INBOX&amp;passed_id\=[0-9]+&amp;startMessage=1', re.IGNORECASE)
        newlist = p1.findall(inbox)
        alllist = p2.findall(inbox)
        for msg in newlist:
            msg = msg.replace('&amp;', '&')
            new_msgs.append(msg.replace('<b><a href="', ''))
        for msg in alllist:
            all_msgs.append(msg.replace('&amp;', '&'))
        return new_msgs, all_msgs

    def _get_sent_links(self, mailboxlinks):
        'A private method to extract message links from INBOX.Sent'
        if self.loggedin == False:
            return None
        mailbox = mailboxlinks.decode()
        sent_msgs = []
        p = re.compile('read_body.php\?mailbox=INBOX.Sent&amp;passed_id\=[0-9]+&amp;startMessage=1', re.IGNORECASE)
        sentlist = p.findall(mailbox)
        for msg in sentlist:
            sent_msgs.append(msg.replace('&amp;', '&'))
        return sent_msgs
    
    def _build_headers(self, cookie=None, login=False):
        'Private method to build client\'s HTTP headers'
        headers = {}
        if cookie:
            headers['Referer']= self.url + 'login.php'
            headers['Cookie'] = cookie
        headers['Connection'] = 'keep-alive'
        # urlencode is just for POST
        if login:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        return headers
    
    def _build_cookie(self, response = None):
        'Private method to create the cookie to maintain login session'
        if response == None:
            return None
        cookies = response['set-cookie'].split(', ')
        cookie_entries = {}
        for entry in cookies:
            if entry.find(';') < entry.find('='):
                continue
            ckey = entry.split('=')[0]
            cookie_entries[ckey] = entry.split(';')[0]
            cookie = ''
            for entry in cookie_entries:
                cookie += cookie_entries[entry] + '; '
        return cookie[0:-2]

    def _build_login_body(self):
        'Private method to populate POST variables for login page'
        body = {}
        body["login_username"] = self.user
        body["secretkey"] = self.password
        # Pretend we have javacript
        body["js_autodetect_results"] = "1"
        body["just_logged_in"] = "1"
        return body
    
    def _get_src_files(self, contentpage = None):
        'Private method to find internal links'
        if self.loggedin == False:
            return None
        if contentpage == None:
            return None
        content = contentpage.decode()
        p1 = re.compile('src=[^ ]* ', re.IGNORECASE)
        imageList = []
        images = p1.findall(content)
        for image in images:
            image = image.lower().replace('src=', '').strip(' \'"')
            imageList.append(image)
        return imageList

    def logout(self):
        'Logs out the user'
        if self.loggedin:
            location = 'signout.php'
            myurl = self.url + location
            response, content = self.http.request(myurl, 'GET', headers=self.headers)
            self.loggedin = False
        else:
            print('Error: Not logged in!')

    def del_all_msgs(self):
        '''Deletes all messages in the user\'s in and sent mailboxes--
        but just from the page, a maximum of 15 messages each. The
        default is to call this method when either mailbox contains
        10 or more messages, so this shouldn't be a problem.
        '''
        # Put all our eggs in one basket
        self.all_msgs += self.sent_msgs
        if len(self.all_msgs) == 0 or self.loggedin == False:
            return
        try:
            print(time.strftime("%H:%M:%S") + ': ' + self.whoami + ' is clearing inbox.')
            for msg in self.all_msgs:
                myurl = self.url + msg
                response, contentpage = self.http.request(myurl, 'GET', headers=self.headers)
                content = contentpage.decode()
                p1 = re.compile('delete_message.php[^"\r\n]+startMessage=1', re.IGNORECASE)
                hit = p1.findall(content)
                if hit != None:
                    delurl = self.url + hit[0]
                    smtoken = hit[0].split(';')[2]
                    smtoken = smtoken.replace('&amp', '')
                    delurl = delurl.replace('&amp;', '&')
                    response, content = self.http.request(delurl, 'GET', headers=self.headers)
            self.all_msgs = []
            purgeurl = self.url + 'empty_trash.php?' + smtoken
            response, content = self.http.request(purgeurl, 'GET', headers=self.headers)
        except Exception as e:
            print('Error clearing inbox:', e)

    def send_msg(self,sendTo,subject=None,msgBody=None):
        'Sends an email message to sendTo addressee' 
        if self.loggedin == False:
            return
        # Get the compose form, which provides required smtoken value
        myurl = self.url + 'compose.php?mailbox=INBOX&startMessage=1'
        response, contentpage = self.http.request(myurl, 'GET', headers=self.headers)
        # Build the request body by extracting the needed
        # form fields and values. A few included squirrelmail
        # features aren't handled here, including the delivered
        # and read confirmations
        content = contentpage.decode()
        p1 = re.compile('type.+value="[^"]*"', re.IGNORECASE)
        fields = p1.findall(content)
        body = {}
        # These three are weird, so handle separately
        body['send'] = 'Send'
        body['mailprio'] = '3'
        # This quick-and-dirty way of handling the form
        # data won't support files. If really needed, this
        # can be added later
        body['"attachfile"; filename=""'] = ''
        for field in fields:
            parts = field.split('"')
            if parts[1] in ('checkbox','submit'):
                continue
            body[parts[3]] = parts[5]
        # Get default message body and subject line
        # from fortune utility
        f = os.popen('/usr/games/fortune')
        msg = f.read().strip()
        f.close()
        # The three important fields
        if msgBody == None:
            body['body'] = msg
        else:
            body['body'] = msgBody
        if sendTo == None:
            body['send_to'] = random.choice(self.roster)
        else:
            body['send_to'] = sendTo
        if subject == None:
            subjLine = str(get_sentences(1)[0])
            body['subject'] = subjLine
        else:
            body['subject'] = subject
        # Get the pre-built headers
        headers = self.headers
        # Add the content type for form data
        # NOTE: This is just a quick workaround. It's not going
        # to handle file uploads
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        response, content = self.http.request(myurl, 'POST', headers=self.headers, body=urlencode(body))
        # A successful send will get us a 302, to send us back to the INBOX
        try:
            location = response['location']
        except KeyError:
            print ("Error: Message send failed.")
            return
        myurl = location
        response, content = self.http.request(myurl, 'GET', headers=self.headers)
        
    def login(self):
        'Logs in the given user'
        try:
            response, content = self.http.request(self.url, 'GET')
        except socket.error:
            print('Error: No response from Web server at ' + self.host + '.')
            return
        if response['status'] != '200':
            print('Error: Squirrelmail not found at ' + self.host + '.')
            return
        # Get cookies from server response
        cookie = self._build_cookie(response)
        # Get the HTTP headers for logging in 
        self.headers = self._build_headers(cookie, True)
        myurl = self.url + 'redirect.php'
        # Build the body for login form processing (redirect.php)
        # using the various POST variables
        body = self._build_login_body()
        # Submit the login form
        response, content = self.http.request(myurl, 'POST', headers=self.headers, body=urlencode(body))
        # A successful login returns a 302, so follow it
        # if that's what we get back
        try:
            location = response['location']
            self.loggedin = True
        except KeyError:
            print("Error: Login attempt failed.")
            return
        # On successful login, need to get new cookie, with key,
        # from the server response and replace in the HTTP headers
        cookie = self._build_cookie(response)
        self.headers['Cookie'] = cookie
        myurl = self.url + location
        response, content = self.http.request(myurl, 'GET', headers=self.headers)
        # Grab any imbedded images, frame pages, etc. and GET those too
        srcList = self._get_src_files(content)
        # GET the two main frames and put the message links in the right frame, holding
        # the INBOX contents, into the instance variables new_msgs and all_msgs
        for src in srcList:
            myurl = self.url + src
            response, content = self.http.request(myurl, 'GET', headers=self.headers)
            if src == 'right_main.php':
                inbox = content
        self.new_msgs, self.all_msgs = self._get_inbox_links(inbox)
        # Now do the same for the SENT mailbox
        myurl = self.url + 'right_main.php?PG_SHOWALL=0&sort=0&startMessage=1&mailbox=INBOX.Sent'
        response, content = self.http.request(myurl, 'GET', headers=self.headers)
        self.sent_msgs = self._get_sent_links(content)


if __name__ == '__main__':
    server1 = 'elko.26maidenlane.net'
    server2 = 'redding.26maidenlane.net'
    agentList = {'hannah@'+server1: 'bagjms6a', 'ella@'+server1: 'afwtl7j4', 'joseph@'+server1: 'xutxehdd', 'ava@'+server1: 'ftgadqvl', 'victoria@'+server1: 'pttktw42', 'sophia@'+server1: 'famwzxe2', 'zoey@'+server2: 'qndjgbt3', 'liam@'+server1: '7nfun5em', 'charlotte@'+server1: '6bgkmjfn', 'natalie@'+server1: 'uc4r5ck8', 'michael@'+server2: 'abpwlsud', 'isabella@'+server2: 'ruftsefb', 'david@'+server1: 'a22q6drp', 'olivia@'+server1: 'ryex5cw2', 'chloe@'+server2: 'ht9czbxz', 'joshua@'+server2: 'nse9jg4k', 'logan@'+server2: 'd8hlynaq', 'lucas@'+server2: '2hpa92zw', 'emma@'+server2: 'kbsemhzg', 'daniel@'+server1: 'uutg3zbt', 'abigail@'+server2: 'rlez4xd8', 'andrew@'+server1: 'uakmbr33', 'william@'+server2: '3hkkp8xt', 'elijah@'+server2: 'drtkybpu', 'sofia@'+server1: 'eyvwbunb', 'james@'+server2: 'buahehfk', 'alexander@'+server1: '6tvmhfu6', 'anthony@'+server2: 'ntwqhace', 'grace@'+server2: 'zsxhwdhj', 'ethan@'+server1: 'wnz7s7gr', 'aiden@'+server1: 'ngcy4zvy', 'emily@'+server1: 'zha7utjl', 'jackson@'+server1: 's79jvucp', 'addison@'+server1: 'yytezmrb', 'aubrey@'+server2: 'u36fnreq', 'jayden@'+server2: 'veynzak6', 'madison@'+server1: 'kkgez8uy', 'mia@'+server2: 'uysjzwdr', 'harper@'+server2: 'vyx4uaz7', 'mason@'+server1: 'kmmfvqva', 'benjamin@'+server1: '2ekvwjp7', 'gabriel@'+server1: 'rdqp9qsq', 'amelia@'+server1: '2d9hvmkp', 'jacob@'+server2: 'sgwnd9km', 'evelyn@'+server2: '88ctr5py', 'elizabeth@'+server2: 'asdjswcv', 'avery@'+server2: 'pzljljjh', 'samuel@'+server2: '6bfdzq76', 'noah@'+server2: 'f7eclstk', 'matthew@'+server2: 'vdcukvuk'}

    # Loop control variable; turns True
    # when Ctrl-c is pressed
    done = False
    # Here's the signal to threads
    # that it's time to log out and exit
    shutdown_event = threading.Event()
    # Create some agent threads
    for agent in agentList:
        user, host = agent.split('@')
        passwd = agentList[agent]
        try:
            print('Spawning thread for ' + agent + '...', end='')
            agent = SQMail(host, user, passwd, True)
            print('success!')
            agent.start()
        except Exception as e:
            print ('Error: unable to start thread for ' + agent + ':', e)
            sys.exit(1)
    while not done:
        try:
            time.sleep(30)
        except (KeyboardInterrupt, SystemExit):
            shutdown_event.set()
            done = True
