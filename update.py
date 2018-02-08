#!/usr/bin/env python

# Tiny nsupdate.info client.
#
# Usage: ./update.py /path/to/config.conf
#
# Configuration file format:
#
#   <hostname>:<host_secret>
#
# For example:
#
#   foo.nsupdate.info:asdf123


from __future__ import absolute_import, division, print_function, unicode_literals

import requests
import sys
import dns.resolver


resolver = dns.resolver.Resolver()
resolver.nameservers = ['8.8.8.8', '8.8.4.4']


def get_ipv4_of_host(domain):
    result = resolver.query(domain, 'a')
    return result.response.answer[0].items[0].to_text()


def get_ipv4_of_client():
    result = requests.get('https://ipv4.nsupdate.info/myip')
    return result.text


def update_ipv4(domain, host_secret, client_ipv4):
    result = requests.get(
        'https://{domain}:{host_secret}@ipv4.nsupdate.info/nic/update?myip={client_ipv4}'.format(
            domain=domain,
            host_secret=host_secret,
            client_ipv4=client_ipv4
        )
    )
    return result


def update(config_string):    
    domain, host_secret = config_string.split(':')

    current_domain_ipv4 = get_ipv4_of_host(domain)
    client_ipv4 = get_ipv4_of_client()

    if current_domain_ipv4 != client_ipv4:
        result = update_ipv4(domain, host_secret, client_ipv4)
        if result.status_code == 200:
            print(result.text)
        else:
            print("Error: '{}'".format(result.text))

    else:
        print(
            "Nothing to update, '{domain}' is already set to '{client_ipv4}' address".format(
                domain=domain,
                client_ipv4=client_ipv4
            )
        )


def main():
    if len(sys.argv) == 2:
        with open(sys.argv[1], 'r') as config:
            for config_string in config:
                update(config_string.strip())
    else:
        print('Usage: update.py /path/to/config.conf')
        sys.exit(1)


if __name__ == "__main__":
    main()
