#!/usr/bin/env python3
# spam_factory.py
#####################################################################
# spam_factory.py                                                   #
#                                                                   #
# This script requires a text file called spam_samples.txt          #
# in the current working directory. The file should include         #
# some realistic spam email samples, formatted thusly:              #
#                                                                   #
#     Line 1: From: <emailaddress>                                  #
#     Line 2: Subject: <subject line>                               #
#     Line 3: <blank>                                               #
# Line 4 - ?: <email body>                                          #
#   Line ?+1: '+++++++++++++++++++++' <At least four '+'>           #
#                                                                   #
# Lather, rinse, repeat...                                          #
#                                                                   #
#####################################################################
import sys, smtplib, random, time, logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from configparser import ConfigParser
from argparse import ArgumentParser

# Define a list of spam recipient email addresses...
victims = ['elmer@elko.26maidenlane.net', 'brooklyn@redding.26maidenlane.net', 'kelsey@elko.26maidenlane.net', 'raymond@redding.26maidenlane.net', 'rick@redding.26maidenlane.net', 'zachary@elko.26maidenlane.net', 'eva@elko.26maidenlane.net', 'antonio@elko.26maidenlane.net', 'kathleen@elko.26maidenlane.net', 'samuel@elko.26maidenlane.net', 'connor@elko.26maidenlane.net', 'vicki@elko.26maidenlane.net', 'walter@redding.26maidenlane.net', 'shawn@redding.26maidenlane.net']
    
def get_spam_list(spam_file):
    '''Create a list of canned spam emails, complete
    with sender addresses and subject lines.
    '''
    spam = []
    try: 
        f = open(spam_file)
        line = f.readline()
        count = 0
        sender = subj = body = ''
        html = ''
        while line:
            count += 1
            if line[:4] == '++++':
                if count <= 1:
                    continue
                else:
                    html += '''</p>
                    </body>
                    </html>'''
                    spam.append([sender, subj, html, body])
                body = ''
                html = '''<html>
                <head></head>
                <body>
                <p>'''
            elif line[:4] == 'From':
                sender = line[6:]
            elif line[:4] == 'Subj':
                subj = line[9:]
            else:
                body += line
                html += line.strip() + '<br />'
            line = f.readline()
        html += '''</p>
        </body>
        </html>'''
        spam.append([sender, subj, html, body])
        f.close()
    except Exception as e:
        print('Error: Unable to open spam_samples file: {}. Exiting...'.format(repr(e)))
        sys.exit(1)
    return spam

def pick_victims(victims, min, max):
    victims = list(set(victims))
    count = random.randrange(min, max + 1)
    if count > len(victims):
        count = len(victims)
    suckers = []
    while len(suckers) < count:
        maybe = random.choice(victims)
        if maybe in suckers:
            continue
        suckers.append(maybe)
    return suckers

def read_config(file_name):
    # Create a parser and read the given config file
    try:
        parser = ConfigParser()
        parser.read(file_name)
        return parser['settings']
    except:
        return None

def main(config_file):
    # Read the config file and set options
    # First, set the default values
    defaults = {'spam_prob': .25, 'min_delay': 45,'max_delay': 90,'min_recipients':2, 'max_recipients': 5,'spam_file': 'spam_samples.txt'}
    options = read_config(config_file)
    if options == None:
        print('ERROR: Can\'t read my configuration file!')
        sys.exit(1)
    spam_prob = options.getfloat('spam_prob', defaults['spam_prob'])
    min_delay = options.getint('min_delay', defaults['min_delay'])
    max_delay = options.getint('max_delay', defaults['max_delay'])
    min_recipients = options.getint('min_recipients', defaults['min_recipients'])
    max_recipients = options.getint('max_recipients', defaults['max_recipients'])
    spam_file = options.get('spam_file', defaults['spam_file'])
    spam_file = spam_file[1:-1]
    # Load up some spam content
    spam = get_spam_list(spam_file)
    ## Set up logging
    # Create logger
    logger = logging.getLogger('spam_factory.py')
    logger.setLevel(logging.INFO)
    # Create a logging handler. Take your choice
    # of a console (stream) for file handler
    ch = logging.StreamHandler()
    #ch = logging.FileHandler('testsqmail.log')
    # Add logging formatter
    formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s', '%b %e %H:%M:%S')
    # Add formatter to logging handler
    ch.setFormatter(formatter)
    # Add logging handler to logger object
    logger.addHandler(ch)

    logger.info('The Spam Factory is up and running!')
    while True:
        # Whew!!! Let's take a break!
        loop_delay = random.randrange(min_delay, max_delay + 1)
        logger.info('Whew! Taking a well-deserved ' + str(loop_delay) + ' second break...')
        try:
            time.sleep(loop_delay)
            # Spammers!!! May the odds be ever in your favor...
            r = random.randint(1,101)
            p = int(1 / spam_prob)
            if r % p != 0:
                logger.info('The odds were not in our favor. Maybe next time...')
                continue
            recips = pick_victims(victims, min_recipients, max_recipients)
            logger.info('Oh, goody! We win!!!')
            item = random.choice(spam)
            sender = item[0].strip()
            subject = item[1]
            for to in recips:
                server = to.split('@')[1]
                # Create message container - the correct MIME type is multipart/alternative.
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = sender
                msg['To'] = to
                # Create the body of the message (a plain-text and an HTML version).
                html = item[2]
                text = item[3]
                # Record the MIME types of both parts - text/plain and text/html.
                part2 = MIMEText(text, 'plain')
                part1 = MIMEText(html, 'html')
                # Attach parts into message container.
                # According to RFC 2046, the last part of a multipart message, in this case
                # the HTML message, is best and preferred.
                msg.attach(part1)
                msg.attach(part2)
                # Send the message via the destination SMTP server.
                try:
                    s = smtplib.SMTP(server)
                    # sendmail function takes 3 arguments: sender's address, recipient's address
                    # and message to send - here it is sent as one string.
                    s.sendmail(sender, to, msg.as_string())
                    logger.info('Spam away from ' + sender + ' to ' + to + '!')
                    s.quit()
                except OSError as e:
                    logger.critical('Something bad happened (OSError): {}'.format(repr(e)))
                    continue
        except KeyboardInterrupt:
                logger.info('Our work is done here, Tonto. Hiyo, Silver...away!')
                sys.exit(0)
        except Exception as e:
                logger.critical('Something bad happened (Exception): {}'.format(e))
                sys.exit(1)
                
if __name__=='__main__':
    parser = ArgumentParser(description='Generate spam emails targeted at cybersecurity simulation participants.')
    parser.add_argument('-f', '--config_file', default='settings.ini', nargs='?',
                        help='Configuration file (default: %(default)s)')
    args = parser.parse_args()
    main(args.config_file)
