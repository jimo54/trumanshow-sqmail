# trumanshow-sqmail/spam
A tool to randomly generate spam email messages targeted at student participants in cyber security simulations. 

## Files
**README.md:** This file

**settings.ini:** Sample configuration file containing default settings to control the behavior of the spam_factory.py script.

**spam_factory.py:** A script that generates random spam emails targeted at student participants, whose email addresses are contained in a Python list, on a random bassis.

**spam_samples.txt:** Sample spam messages used by the spam_factory.py script.

## Installation
This script uses only Python 3 standard libraries. No additional installation steps are required.

## Configuration and Use
The spam_factory.py script requires three forms of configuration to function: 

1) A list of target email addresses, in the form of a Python list, which must be assigned to the variable victim in the first lines of the spam_factory.py script. 

2) A configuration file containing settings for a variety of parameters that control the behavior of the spam_factory script. A sample configuration file names settings.ini, which is the default, is included. A different file name may also be used; however, it must be specified on the command line using the -f option when the script is started. For example, to use a file named options.ini:

```python3 spam_factory.py -f options.ini```

3) A file containing sample spam emails that will be sent to student participants. By default, this file should be called spam_samples.txt; however, a different name may be specified in the configuration file. Each spam sample must be formatted as shown below. Several samples are provided in the included spam_samples.txt file.

  Line 1: From: <emailaddress>
  Line 2: Subject: <subject line>
  Line 3: <blank>
Line 4-?: <email body>
Line ?+1: '+++++++++++++++++++++' <At least four '+'>
