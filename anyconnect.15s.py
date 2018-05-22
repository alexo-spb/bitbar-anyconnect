#!/usr/local/bin/python2

# <bitbar.title>AnyConnect VPN</bitbar.title>
# <bitbar.author>Aleksei Osin (alexo.spb@gmail.com)</bitbar.author>
# <bitbar.desc>Connect to VPN from the menu bar.
# <bitbar.version>1.0</bitbar.version>
# Set credentials to ~/.bitbar_anyconnect/profiles.ini
# </bitbar.desc>

import argparse
import os
import pexpect
import pyotp
import subprocess
import time
import ConfigParser

SCRIPT=os.path.realpath(__file__)
VPN = '/opt/cisco/anyconnect/bin/vpn'
CONFIG_DIR = os.path.expanduser('~/.bitbar_anyconnect')
LOGFILE = None # CONFIG_DIR + '/log.txt'
if LOGFILE: LOGFILE = open(LOGFILE, 'wb')
PROFILES = CONFIG_DIR + '/profiles.ini'

IMAGE_ON  = 'image=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'
IMAGE_OFF = 'image=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'
IMAGE_ERR = 'image=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'

CONNECTED = 0
DISCONNECTED = 1
ERROR = 3

def parse_args():
    parser = argparse.ArgumentParser(description='Control VPN connection')
    parser.add_argument('--action', choices=['state', 'connect', 'disconnect'], default='state')
    parser.add_argument('--profile')
    return parser.parse_args()

def notify(message):
    args = ['osascript', '-e', 'display notification "{0}" with title "Cisco Anyconnect VPN"'.format(message)]
    subprocess.check_call(args)

def get_state():
    try:
        args = ['state']
        proc = pexpect.spawn(VPN, args, logfile=LOGFILE)
        idx = proc.expect(['state: Connected', 'state: Disconnected'])
        proc.wait()
        if idx == 0:
            return CONNECTED
        return DISCONNECTED
    except:
        return ERROR

def connect(profile):
    try:
        config = ConfigParser.ConfigParser()
        config.read(PROFILES)
        try:
            notify('Connecting ...')
            args = ['connect', config.get(profile, 'server')]
            proc = pexpect.spawn(VPN, args, logfile=LOGFILE)
            group = config.get(profile, 'group')
            if group:
                proc.expect('Group:')
                proc.sendline(group)
                username = config.get(profile, 'username')
                proc.expect('Username:')
                proc.sendline(username)
                password = config.get(profile, 'password')
                proc.expect('Password:')
                proc.sendline(password)
                password2 = config.get(profile, 'password2')
                if password2 == 'totp':
                    secret = config.get(profile, 'secret')
                    totp = pyotp.TOTP(secret)
                    password = pyotp.TOTP(secret).now()
                    proc.expect('Second Password:')
                    proc.sendline(password)
                idx = proc.expect(['state: Connected', 'Login failed'])
                if idx == 0:
                    proc.wait()
                    time.sleep(5)
                    notify('Successfully connected')
                    return CONNECTED
                proc.terminate(True)
                notify('Login failed')
                return ERROR
        except:
            notify('Failed to connect to VPN')
    except:
        notify('Failed to read profiles')
    return ERROR

def disconnect():
    try:
        notify('Disconnecting ...')
        args = ['disconnect']
        proc = pexpect.spawn(VPN, args, logfile=LOGFILE)
        proc.wait()
        notify('Successfully disconnected')
        return DISCONNECTED
    except:
        notify('Failed to disconnect from VPN')
        return ERROR

def render_connected():
    print '|' + IMAGE_ON
    print '---'
    print 'state: Connected'
    template = 'Refresh State| bash={0} terminal=false'
    print template.format(SCRIPT)
    template = 'Disconnect| bash={0} param1=--action=disconnect terminal=false'
    print template.format(SCRIPT)


def render_disconnected():
    print '|' + IMAGE_OFF
    print '---'
    print 'state: Disconnected'
    template = 'Refresh State| bash={0} terminal=false'
    print template.format(SCRIPT)
    config = ConfigParser.ConfigParser()
    config.read(PROFILES)
    for section in config.sections():
        template = '{0}| bash={1} param1="--action=connect" param2=--profile={0} terminal=false'
        print template.format(section, SCRIPT)

def render_error():
    print '|' + IMAGE_ERR
    print '---'
    print 'state: Error'
    template = 'Refresh State| bash={0} terminal=false'
    print template.format(SCRIPT)

def main():
    try:
        args = parse_args()
        if args.action == 'state':
            state = get_state()
            if state == CONNECTED:
                render_connected()
            if state == DISCONNECTED:
                render_disconnected()
            if state == ERROR:
                render_error()
        if args.action == 'connect':
            if connect(args.profile) == CONNECTED:
                render_connected()
        if args.action == 'disconnect':
            if disconnect() == DISCONNECTED:
                render_disconnected()
    except:
        render_error()

if __name__ == "__main__":
    main()
