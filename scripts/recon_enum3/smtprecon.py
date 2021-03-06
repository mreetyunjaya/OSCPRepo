#!/usr/bin/python
import socket
import sys
import os
import subprocess
import argparse
import pathlib

# Depends on metasploit and seclists wordlists
# Depends on smtp-user-enum

# mkdir_p function updated for >= python 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

#NSE Documentation
#Running
#smtp-commands: attempts to use EHLO and HELP to gather Extended commands supported by a server [--script-args smtp-commands.domain=<domain>]
#smtp-enum-users: attempt to enumerate users by using VRFY, EXPN, or RCPT TO commands. Will stop if auth is enforced.
#smtp-ntlm-info: enumerate servers that allow NTLM auth. Sending NULL NTLM will cause a response of NetBIOS, DNS, and OS build version
#smtp-vuln-cve2011-1764: check for format string vuln in Exim 4.70-4.75 with DKIM support (CVE-2011-1764). RCE with EXIM priv levels
#pop3-capabilities: Retrieves POP3 email server capabilities
#pop3-ntlm-info: Enum info from POP3 with NTLM auth enabled

#Not running
#smtp-brute: Brute force login/plain/cram-md5/digest-md5/NTLM
#smtp-open-relay: attempt to relay mail by issuing combination of SMTP commands.
#smtp-strageport: check if SMTP is running on non-standard port.
#smtp-vuln-cve2010-4344: check for Heap overflow within versions of EXIM prior to 4.69 (CVE-2010-4344) and priv exc in EXIM prior to 4.72 (CVE-2010-4345)
 #Warning ^ potential to crash if failed (heap corruption)
#smtp-vuln-cve2011-1720: check for memory corruption in Postfix server when using Cyrus SASL library auth (CVE-2011-1720).
 #Warning ^ potential denial of service and possibly RCE
def doNmap():
    print("INFO: Performing nmap SMTP script scan for %s:25,110,143,465,587,993,995" % (ip_address))
    subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-p','25,110,143,465,587,993,995','--script','banner,smtp-commands,smtp-enum-users,smtp-ntlm-info,smtp-vuln-cve2011-1764,pop3-capabilities,pop3-ntlm-info,vulners','-oA',nmap_outfile,ip_address],encoding='utf8')

#nmap --script=smtp-enum-users sometimes errors (unhandled status codes) even
#if information is obtainable. Adding second method for user-enum
# Usage: smtp-user-enum [-OPTIONS [-MORE_OPTIONS]] [--] [PROGRAM_ARG1 ...]
# The following single-character options are accepted:
# 	With arguments: -m -u -U -s -S -r -t -M -f -D -p
# 	Boolean (without arguments): -d -v -h
# Options may be merged together.  -- stops processing of options.
# Space is not required between options and their arguments.
#   [Now continuing due to backward compatibility and excessive paranoia.
#    See 'perldoc Getopt::Std' about $Getopt::Std::STANDARD_HELP_VERSION.]
# smtp-user-enum v1.2 ( http://pentestmonkey.net/tools/smtp-user-enum )
# Usage: smtp-user-enum [options] ( -u username | -U file-of-usernames ) ( -t host | -T file-of-targets )
# options are:
#   -m n     Maximum number of processes (default: 5)
# 	-M mode  Method to use for username guessing EXPN, VRFY or RCPT (default: VRFY)
# 	-u user  Check if user exists on remote system
# 	-f addr  MAIL FROM email address.  Used only in "RCPT TO" mode (default: user@example.com)
#     -D dom   Domain to append to supplied user list to make email addresses (Default: none)
#              Use this option when you want to guess valid email addresses instead of just usernames
#              e.g. "-D example.com" would guess foo@example.com, bar@example.com, etc.  Instead of
#                 simply the usernames foo and bar.
# 	-U file  File of usernames to check via smtp service
# 	-t host  Server host running smtp service
# 	-T file  File of hostnames running the smtp service
# 	-p port  TCP port on which smtp service runs (default: 25)
# 	-d       Debugging output
# 	-t n     Wait a maximum of n seconds for reply (default: 5)
# 	-v       Verbose
# 	-h       This help message
def doSmtpUserEnum():
    if os.path.isfile('/usr/bin/smtp-user-enum'):
        try:
            results = subprocess.check_output(['smtp-user-enum','-U',userlist,'-t',ip_address],encoding='utf8')
            f = open(smtpuserenum_outfile, "w")
            if results:
                f.write(results)
            f.close()
        except Exception as e:
            print(type(e))
            print("Unexpected issue in doSmtpUserEnum in smtprecon")

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Rough script to handle checking smtp endpoints. Usage: smtprecon.py <ip address> <port>')
    parser.add_argument('ip_address', help="Ip address of target windows machine")
    parser.add_argument('port', help="Specific port to enumerate")
    args = parser.parse_args()

    ip_address = args.ip_address
    port = args.port

    userlistAlt = "/root/lists/secLists/Usernames/Honeypot-Captures/multiplesources-users-fabian-fingerle.de.txt"
    userlist = "/usr/share/wordlists/metasploit/unix_users.txt"

    BASE = "/root/scripts/recon_enum/results/exam/smtp"
    mkdir_p(BASE)

    nmap_outfile = "%s/%s_%s_smtp" % (BASE,ip_address,port)
    smtpuserenum_outfile = "%s/%s_%s_smtp_user_enum" % (BASE,ip_address,port)

