#!/usr/bin/env python
import re, sys, socket, argparse
import httplib2
from urllib.parse import urlencode

class SQMail(httplib2.Http):
    'A class that interacts with a Squirrelmail email app server'
    def __init__(self, host, user, password):
        'Constructor creates an Squirrelmail user' 
        self.host = host
        self.user = user
        self.whoami = user + '@' + host
        self.password = password
        self.http = httplib2.Http()
        self.url = 'http://' + host + '/squirrelmail/src/'
        self.loggedin = False
        self.new_msgs = []
        self.all_msgs = []
        self.sent_msgs = []

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
            try:
                response, content = self.http.request(myurl, 'GET', headers=self.headers)
            except:
                return False
            self.loggedin = False
        else:
            return False
        return True
    
    def send_msg(self,sendTo=None,subject=None,msgBody=None):
        'Sends an email message to sendTo addressee'
        # This method fails if agent is not logged in or
        # any of the arguments is left blank
        if self.loggedin == False or sendTo == None or subject == None or msgBody == None:
            return False
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
        # The three important fields,
        # which all come in as parms
        body['body'] = msgBody
        body['send_to'] = sendTo
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
            return false
        myurl = location
        response, content = self.http.request(myurl, 'GET', headers=self.headers)
        return True
    
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
        return True

if __name__=='__main__':
    # Set up the argparser
    parser = argparse.ArgumentParser(description='Send an email as an SQMail agent.')
    parser.add_argument('-f', '--from_addr', help='The email address of the sending agent', required=True)
    parser.add_argument('-p', '--passwd', help='The sending agent\'s password.', required=True)
    parser.add_argument('-s', '--subj', help='The subject line for the email', required=True)
    parser.add_argument('-t', '--to', help='The destination email address', required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-b', '--body', help='The email body')
    group.add_argument('-F', '--file', help='A text file containing the email body')   
    args = parser.parse_args()

    # Find and set up the message body
    if args.file == None:
        body = args.body
    else:
        try:
            f = open(args.file)
            body = f.read()
            f.close()
        except:
            print('ERROR: Unable to open/read text file containing email body:', e)
            sys.exit(1)
    # Create the agent 
    sender = args.from_addr.split('@')[0]
    sender_domain = args.from_addr.split('@')[1]
    recipient = args.to.split('@')[0]
    recipient_domain = args.to.split('@')[1]
    try:
        agent = SQMail(sender_domain, sender, args.passwd)
    except Exception as e:
        print('ERROR: Unable to instantiate that email agent:', e)
        sys.exit(1)
    # Log in the agent
    if not agent.login():
        print('ERROR: Login failure for that email agent. Please confirm the account and credentials and that the email server is running.')
        sys.exit(1)
    # Send the message
    if not agent.send_msg(args.to, args.subj, body):
        print('ERROR: Unable to send that email message.')
        sys.exit(1)
    # Log out the agent
    agent.logout()
    print('Message sent from ' + args.from_addr + ' to ' + args.to + '.')
