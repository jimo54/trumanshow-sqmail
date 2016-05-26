#!/usr/bin/env python3
import os, sys, re, socket, time, random, logging, threading
import httplib2, pickle
import sentence_generator as sg
from urllib.parse import urlencode
from configparser import ConfigParser

#################################################################
# This script requires the fortune-mod package to be installed  #
# on the local system:                                          #
#    sudo apt-get install fortune-mod                           #
#################################################################

class SQMail(httplib2.Http, threading.Thread):
    'A class that interacts with a Squirrelmail email app server'
    # The list of sqmail agents is created by a script in
    # the accounts directory, named sqmail_accounts.py. This
    # script then stores a Python dictionary of email addresses
    # and their associated passwords in a Python pickle
    # file, accounts/sqmail_accounts.p, which we'll use here
    # to load account information. See README.md for details.
    try:
        accounts = pickle.load(open('accounts/sqmail_accounts.p', 'rb'))
    except Exception as e:
        self.logger.critical('Error: Can\'t open and/or read accounts/sqmail_accounts.p ' + str(e))
        sys.exit(1)
    # Read configuration values from settings.ini in the present working directory.
    # On error, use these defaults.
    defaults = {"send_prob": 0.1, "min_delay": 10, "max_delay": 30}
    try:
        parser = ConfigParser()
        parser.read('settings.ini')
        options = parser['settings']
        send_prob = options.getfloat('send_prob', defaults['send_prob'])
        min_delay = options.getint('min_delay', defaults['min_delay'])
        max_delay = options.getint('max_delay', defaults['max_delay'])
    except Exception as e:
        print('SQMail unable to read configuration from settings.ini: {}. Configuration set using hard-coded defaults.'.format(repr(e)))
        send_prob = defaults['send_prob']
        min_delay = defaults['min_delay']
        max_delay = defaults['max_delay']
    
    def __init__(self, host, user, password, group=None, run=False):
        'Constructor creates an Squirrelmail user'
        # Check for a class logger variable and check out if none exists.
        # This value is set in the driver script.
        if SQMail.logger == None:
            print('ERROR: No SQMail logger exists. I can\'t work this way!')
            sys.exit(1)
        threading.Thread.__init__(self, group=None)
        self.host = host
        self.user = user
        self.whoami = user + '@' + host
        self.password = password
        self.stopEvent = threading.Event()
        self.http = httplib2.Http()
        self.url = 'http://' + host + '/squirrelmail/src/'
        self.loggedin = False
        self.roster = self._build_roster()
        self.new_msgs = []
        self.all_msgs = []
        self.sent_msgs = []
        self.lastSend = int(time.time()) - random.randint(1,3601)

    def stop(self):
        # stop is sent by caller when Ctrl-c is pressed
        self.stopEvent.set()
        self.logger.info(self.whoami + ': Stop event has been set')
        
    def run(self):
        delay = random.randint(SQMail.min_delay, SQMail.max_delay)
        # stopEvent is sent by caller when Ctrl-c is pressed
        # See the method above
        while not self.stopEvent.is_set():
            try:
                self.login()
                if len(self.all_msgs) > 0:
                    if len(self.all_msgs) > 5:
                        self.del_all_msgs()
                    else:
                        self.read_msg()
                if not self.stopEvent.is_set():
                    time.sleep(delay)
                    r = random.randint(1,101)
                    if r <= (SQMail.send_prob * 100):
                        self.read_new_msgs()
                        to = random.choice(self.roster)
                        self.send_msg(to)
                        self.logger.info(self.whoami + ' sent email to ' + to)
            except Exception as e:
                self.logger.warning('Whoops!: %s' % e)
        self.logout()
        
    def read_new_msgs(self):
        '"Reads" all unread messages in the user\'s INBOX'
        if len(self.new_msgs) == 0 or self.loggedin == False:
            return
        self.logger.info(self.whoami + ' is reading new messages.')
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
        allUsers = list(SQMail.accounts.keys())
        roster = []
        max = random.randint(4,9)
        count = 0
        while count <= max:
            test = random.choice(allUsers)
            if test != self.whoami and test not in roster:
                roster.append(test)
                count += 1
        # Before return, we need to take the 'webmail.' out of all the email addresses
        for i in range(len(roster)):
            roster[i] = roster[i].replace('webmail.','')
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
        # Some sample user-agent strings
        user_agents = ['"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0"', '"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:43.0) Gecko/20100101 Firefox/43.0"','"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36"','"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:44.0) Gecko/20100101 Firefox/44.0"','"Mozilla/5.0 (Windows NT 6.1; rv:43.0) Gecko/20100101 Firefox/43.0"']
        headers = {}
        # Pick a random user-agent from the list above
        headers['User-Agent'] = random.choice(user_agents)
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
            self.logger.info(self.whoami + ' logging out')
            location = 'signout.php'
            myurl = self.url + location
            response, content = self.http.request(myurl, 'GET', headers=self.headers)
            self.loggedin = False
        else:
            self.logger.warning('Error: Not logged in!')
    def del_all_msgs(self):
        '''Deletes all messages in the user\'s in and sent mailboxes--
        but just from the current page, a maximum of 15 messages each.
        The default is to call this method when either mailbox contains
        10 or more messages, so this shouldn't be a problem.
        '''
        # Put all our eggs in one basket
        self.all_msgs += self.sent_msgs
        if len(self.all_msgs) == 0 or self.loggedin == False:
            return
        try:
            self.logger.info(self.whoami + ' is clearing inbox')
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
            self.logger.warning('Error clearing inbox: ' + str(e))
            
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
            subj = sg.get().split()
            if len(subj) > 10:
                subj = ' '.join(subj[0:10])
            else:
                subj = ' '.join(subj)[:-1]
            subjLine = subj
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
            self.logger.warning("Error: Message send failed.")
            return
        myurl = location
        response, content = self.http.request(myurl, 'GET', headers=self.headers)
        
    def login(self):
        'Logs in the given user'
        try:
            response, content = self.http.request(self.url, 'GET')
        except socket.error:
            self.logger.critical('Error: No response from Web server at ' + self.host + '.')
            return
        if response['status'] != '200':
            self.logger.critical('Error: Squirrelmail not found at ' + self.host + '.')
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
            self.logger.warning('Error: Login attempt failed.')
            return
        # On successful login, need to get a new cookie, with key,
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
