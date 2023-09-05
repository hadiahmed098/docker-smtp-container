#!/bin/bash

set -eE -u -o pipefail

# First run the template replace script
python3 /docker_entrypoint/tmpl_replace.py

# Now copy the files to the right spot
mv /config/opendkim/opendkim.conf /etc/opendkim.conf
mv /config/opendmarc/opendmarc.conf /etc/opendmarc.conf
mv /config/postfix/main.cf /etc/postfix/main.cf
mv /config/spamassassin/local.cf /etc/spamassassin/local.cf

# Start all the services
service opendkim start
service opendmarc start
service clamav-daemon start
service clamav-milter start
service clamav-freshclam start
service spamass-milter start

# Update alias files
cat /config/postfix/aliases > /etc/aliases
newaliases && echo "Updated alias definitions"

# Start postfix and stay there
#postfix start-fg
