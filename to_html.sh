#!/bin/bash
#####################################
#                                   #
# to_html.sh                        #
#                                   #
# This tiny script will change the  #
# default view in all SquirrelMail  #
# user accounts on this system to   #
# html vs plaintext.                #
#                                   #
#                                   #
#####################################

for l in `ls /var/lib/squirrelmail/data/*.pref`
do sed -i s/show_html_default=0/show_html_default=1/g $l
done
