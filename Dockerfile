FROM docker.io/debian:12-slim

ARG DEBIAN_FRONTEND=noninteractive

COPY ./config/ /config/
COPY ./docker_entrypoint/ /docker_entrypoint/

# Setup some preconditions for package installs
RUN echo "postfix postfix/mailname string localhost" | debconf-set-selections \
    && echo "postfix postfix/main_mailer_type string 'Internet Site'" | debconf-set-selections

# Install all our packages
RUN apt update && apt upgrade -y && apt install -y --no-install-recommends \
    postfix postfix-pcre clamav clamav-daemon clamav-milter spamassassin spamass-milter postfix-policyd-spf-python opendkim opendkim-tools opendmarc libsasl2-modules sasl2-bin

# Copy over all non-template config files
RUN mv /config/clamav/clamav-milter.conf /etc/clamav/clamav-milter.conf && \
    mv /config/policyd-spf/policyd-spf.conf /etc/postfix-policyd-spf-python/policyd-spf.conf && \
    mv /config/postfix/master.cf /etc/postfix/master.cf && \
    mv /config/spamassassin/spamassassin.default /etc/default/spamassassin && \
    mv /config/spamassassin/spamass-milter.default /etc/default/spamass-milter && \
    chmod +x /docker_entrypoint/docker-entrypoint.sh

EXPOSE 25 587
#ENTRYPOINT ["/docker_entrypoint/docker-entrypoint.sh"]
