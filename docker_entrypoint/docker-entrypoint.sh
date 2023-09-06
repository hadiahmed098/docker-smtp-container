#!/bin/bash

set -eE -u -o pipefail

# First run the template replace script
python3 /docker_entrypoint/tmpl_replace.py

# Now copy the files to the right spot
mv /config/opendkim/opendkim.conf /etc/opendkim.conf
mv /config/opendmarc/opendmarc.conf /etc/opendmarc.conf
mv /config/postfix/main.cf /etc/postfix/main.cf
mv /config/spamassassin/local.cf /etc/spamassassin/local.cf

# Update alias files
cat /config/postfix/aliases > /etc/aliases
newaliases && echo "Updated alias definitions"

# Update relay SASL password
cat /config/postfix/sasl_passwd > /etc/postfix/sasl_passwd
postmap /etc/postfix/sasl_passwd && echo "Updated relay SASL passwords"

# Start all the services
service syslog-ng start
service opendkim start
service opendmarc start
service clamav-daemon start
service clamav-milter start
service clamav-freshclam start
service spamd start
service spamass-milter start
service postfix start

# Monitor the log and stay there
tail -f /var/log/mail.log
