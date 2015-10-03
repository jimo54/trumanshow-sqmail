#!/bin/bash
for l in `ls /var/lib/squirrelmail/data/*.pref`; 
do sed -i s/show_html_default=0/show_html_default=1/g $l; 
done
