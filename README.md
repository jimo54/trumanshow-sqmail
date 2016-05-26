# trumanshow-sqmail

A tool to generate Web traffic in the form of emails exchanged among virtual agent threads with user accounts on email servers running SquirrelMail.

##Files##
**accounts:** A folder containing Python scripts and other files used to create user accounts for virtual agents on each participating email server running SquirrelMail. See README.md in the accounts folder for more information.

**spam:** A folder containing a Python script and a file with sample spam messages that can be used to generate spam email messages targeted at student participants. See README.md in the spam folder for more information.

**README.md:** This file.

**dubiners.txt:** The text of James Joyce's *Dubliners*, taken from Project Gutenberg, and used by sentence_generator.py. The usual copyright headers had to be removed so that the contents could serve as useful sample input, but naturally all the rights and restrictions of a Gutenberg book still apply.

**send_mail.py:** A script that uses a version of the SQMail class (from sqmail.py) to allow a user to send an email message from an existing email agent account to any valid SquirrelMail user. Run the script with the -h or --help option for usage details.

**sentence_generator.py:** A script that generates random, locally-correct sentences using textual input and a Markov model. Adapted from https://github.com/hrs/markov-sentence-generator, with some slight modifications, from a Python 2 standalone program. Used by the SQMail class (from sqmail.py) to generate random sentences used as subject lines for email messages sent by virtual agents threads.

**settings.ini:** Sample configuration file containing default settings to control the behavior of the SQMail agents.

**sqmail.py:** This script defines SQMail, a class that interacts with Squirrelmail email clients to log in/out virtual user agents, send email to other SquirrleMail users, "read" email messages and to occasionally clear the inbox and other mailboxes. The user agents' activities are logged, by default, to the display.

**testsqmail.py:** The driver script for the SQMail class; it creates a thread for each user agent account listed in the accounts/accounts.p pickle file. The script runs until Ctrl-c is pressed, at which point all user agent threads receive a stop message and the threads joined to end the program.

**to_html.sh:** A three-line bash script that changes the default view for all SquirrelMail user accounts on an email server to HTML vs plaintext. It must be run on the email server where accounts are to be so configured.

##Installation##
The SQMail class (defined in sqmail.py) requires the fortune-mod package to be installed on the local system. In Ubuntu 14.04, the following command line can be used:

```sudo apt-get install fortune-mod```

Otherwise, it is only necessary to copy the files and directories in this repository to a convenient location on the machine(s) that will serve as platform for generating the email exchanges.

##Configuration and Use##
Prior to running this application, user accounts for virtual user agents must be created on the SquirrelMail servers among which email traffic is to be exchanged. Scripts and other files needed to generate randomly-selected usernames and passwords, as well as creating accounts, are included in the accounts directory in this repository. See the README.md file in the accounts directory for details.

Once the virtual user accounts have been created, run the testsqmail.py script to generate random email traffic among the virtual user agents:

```python3 testsqmail.py```

The configuration settings in the file settings.ini control the behavior of the user agents, specifically the probability of sending emails and the range of sleep times between rounds of activity.
