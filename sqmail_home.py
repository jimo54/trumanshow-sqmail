#!/usr/bin/env python
import os, sys, re, socket, time, random
import urllib, httplib2
from loremipsum import get_sentences
###########################
# This script requires the fortune-mod package to be installed
# on the local system:
#    sudo apt-get install fortune-mod
# To use Lorem ipsum sentence generator:
#    Install setuptools:
#       (For Python 2) sudo apt-get install python-setuptools
#       (For Python 3) sudo apt-get install python3-setuptools
#    Go to: https://pypi.python.org/pypi/loremipsum/
#       Download the tar ball
#       Extract and cd into new directory
#       Run setup program:
#          (For Python 2) sudo python setup.py install
#          (For Python 3) sudo python3 setup.py install
###########################

server1 = 'elko.26maidenlane.net'
server2 = 'redding.26maidenlane.net'

class SQMail(httplib2.Http):
    'A class that interacts with a Squirrelmail email app server'
    accounts = {'ella@' + server1: 'afwtl7j4', 'daniel@' + server1: 'uutg3zbt', 'sophia@' + server1: 'famwzxe2', 'chloe@' + server2: 'ht9czbxz', 'william@' + server2: '3hkkp8xt', 'charlotte@' + server1: '6bgkmjfn', 'natalie@' + server1: 'uc4r5ck8', 'james@' + server2: 'buahehfk', 'jacob@' + server2: 'sgwnd9km', 'zoey@' + server2: 'qndjgbt3', 'andrew@' + server1: 'uakmbr33', 'joshua@' + server2: 'nse9jg4k', 'evelyn@' + server2: '88ctr5py', 'emma@' + server2: 'kbsemhzg', 'mason@' + server1: 'kmmfvqva', 'elijah@' + server2: 'drtkybpu', 'ethan@' + server1: 'wnz7s7gr', 'aiden@' + server1: 'ngcy4zvy', 'jackson@' + server1: 's79jvucp', 'ava@' + server1: 'ftgadqvl', 'madison@' + server1: 'kkgez8uy', 'samuel@' + server2: '6bfdzq76', 'jayden@' + server2: 'veynzak6', 'benjamin@' + server1: '2ekvwjp7', 'gabriel@' + server1: 'rdqp9qsq', 'avery@' + server2: 'pzljljjh', 'logan@' + server2: 'd8hlynaq', 'aubrey@' + server2: 'u36fnreq', 'grace@' + server2: 'zsxhwdhj', 'hannah@' + server1: 'bagjms6a', 'joseph@' + server1: 'xutxehdd', 'victoria@' + server1: 'pttktw42', 'mia@' + server2: 'uysjzwdr', 'anthony@' + server2: 'ntwqhace', 'harper@' + server2: 'vyx4uaz7', 'david@' + server1: 'a22q6drp', 'olivia@' + server1: 'ryex5cw2', 'sofia@' + server1: 'eyvwbunb', 'abigail@' + server2: 'rlez4xd8', 'lucas@' + server2: '2hpa92zw', 'liam@' + server1: '7nfun5em', 'alexander@' + server1: '6tvmhfu6', 'emily@' + server1: 'zha7utjl', 'matthew@' + server2: 'vdcukvuk', 'noah@' + server2: 'f7eclstk', 'isabella@' + server2: 'ruftsefb', 'michael@' + server2: 'abpwlsud', 'amelia@' + server1: '2d9hvmkp', 'elizabeth@' + server2: 'asdjswcv', 'addison@' + server1: 'yytezmrb'}
    send_prob = 0.1
    minDelay = 10
    maxDelay = 30
    def __init__(self, host, user, password):
        'Constructor creates an Squirrelmail user'
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
        try:
            self._run()
        except:
            print '******************* KABOOM!!!! *******************'
            print self.whoami + ' HAS LEFT THE BUILDING!!!!'

    def _run(self):
        #self.login()
        delay = random.randint(SQMail.minDelay, SQMail.maxDelay)
        while True:
            try:
                self.login()
                if len(self.all_msgs) > 0:
                    if len(self.all_msgs) > 5:
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
                    print time.strftime("%H:%M:%S") + ': ' + self.whoami + ' sent email to', to
            except KeyboardInterrupt:
                print self.whoami + ' logging out...'
                self.logout()
                break
            except Exception, e:
                print 'Whoops!: %s' %e

    def read_new_msgs(self):
        '"Reads" all unread messages in the user\'s INBOX'
        if len(self.new_msgs) == 0 or self.loggedin == False:
            return
        print time.strftime("%H:%M:%S") + ': ' + self.whoami + ' is reading new messages'
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
        allUsers = SQMail.accounts.keys()
        roster = []
        max = random.randint(4,9)
        count = 0
        while count <= max:
            test = random.choice(allUsers)
            if test != self.whoami and test not in roster:
                roster.append(test)
                count += 1
        return roster
        
    def _get_msg_links(self, inbox):
        'A private method to extract message links from INBOX'
        if self.loggedin == False:
            return None, None
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
    
    def _build_headers(self, cookie=None, login=False):
        'Private method to build client\'s HTTP headers'
        headers = {}
        if cookie:
            headers['Referer']= self.url + 'login.php'
            headers['Cookie'] = cookie
        headers['Connection'] = 'keep-alive'
        # urlencoded is just for POST
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
    
    def _get_src_files(self, content = None):
        'Private method to find internal links'
        if self.loggedin == False:
            return None
        if content == None:
            return None
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
            print 'Error: Not logged in!'

    def del_all_msgs(self):
        'Deletes all messages in the user\'s INBOX'
        if len(self.all_msgs) == 0 or self.loggedin == False:
            return
        try:
            print time.strftime("%H:%M:%S") + ': ' + self.whoami + ' is clearing inbox'
            for msg in self.all_msgs:
                myurl = self.url + msg
                response, content = self.http.request(myurl, 'GET', headers=self.headers)
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
        except:
            print 'Error clearing inbox!'

    def send_msg(self,sendTo,subject=None,msgBody=None):
        'Sends an email message to sendTo addressee' 
        if self.loggedin == False:
            return
        # Get the compose form, which provides required smtoken value
        myurl = self.url + 'compose.php?mailbox=INBOX&startMessage=1'
        response, content = self.http.request(myurl, 'GET', headers=self.headers)
        # Build the request body by extracting the needed
        # form fields and values. A few included squirrelmail
        # features aren't handled here, including the delivered
        # and read confirmations
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
            #body['send_to'] = 'jim@' + server1
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
        response, content = self.http.request(myurl, 'POST', headers=self.headers, body=urllib.urlencode(body))
        # A successful send will get us a 302, to send us back to the INBOX
        try:
            location = response['location']
        except KeyError:
            print "Error: Message send failed"
            return
        myurl = location
        response, content = self.http.request(myurl, 'GET', headers=self.headers)
        
    def login(self):
        'Logs in the given user'
        try:
            response, content = self.http.request(self.url, 'GET')
        except socket.error:
            print 'Error: No response from Web server at ' + self.host
            return
        if response['status'] != '200':
            print 'Error: Squirrelmail not found at ' + self.host
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
        response, content = self.http.request(myurl, 'POST', headers=self.headers, body=urllib.urlencode(body))
        # A successful login returns a 302, so follow it
        # if that's what we get back
        try:
            location = response['location']
            self.loggedin = True
        except KeyError:
            print "Error: Login attempt failed"
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
        self.new_msgs, self.all_msgs = self._get_msg_links(inbox)
        return (len(self.new_msgs), len(self.all_msgs))
