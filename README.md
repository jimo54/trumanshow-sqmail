# trumanshow-sqmail

A tool to generate Web traffic in the form of emails exchanged among virtual agent threads with accounts on email servers using the SquirrelMail Web client.

##Files##
**accounts:** A folder containing Python scripts and other files used to create user accounts for virtual agents. See README.md in the accounts folder for more information.

**spam:** A folder containing a Python script and a file with sample spam messages that can be used to generate spam email messages targeted at student participants.

**README.md:** This file.

**dubiners.txt:** The text of James Joyce's *Dubliners*, taken from Project Gutenberg, and used by sentence_generator.py. The usual copyright headers had to be removed so that the contents could serve as useful sample input, but naturally all the rights and restrictions of a Gutenberg book still apply.

**send_mail.py:** A script that uses a version of the SQMail class (from sqmail.py) to allow a user to send an email message from an existing email agent account to any valid SquirrelMail user. Run the script with the -h or --help option for usage details.

**sentence_generator.py:** A script that generates random, locally-correct sentences using textual input and a Markov model. Adapted from https://github.com/hrs/markov-sentence-generato, with some slight modifications, from a Python 2 standalone program. Used by the SQMail class (from sqmail.py) to generate random sentences used as subject lines for email messages sent by virtual agents threads.

**sqmail.py:** This script defines SQMail, a class that interacts with a Squirrelmail email client to log in/out, send email to other SquirrleMail users, "read" email messages and to occasionally clear the inbox and other mailboxes. The user agents' activities are logged, by default, to the display.

**testsqmail.py:** The driver script for the SQMail class; it creates a thread for each user agent account listed in the accounts/accounts.p pickle file. The script runs until Ctrl-c is pressed, at which point all user agent threads receive a stop message and the threads joined to end the program.

**to_html.sh:** A three-line bash script that changes the default view for all SquirrelMail user accounts on an email server to HTML vs plaintext. It must be run on the email server where accounts are to be so configured.

##Installation##

##Configuration and Use##
