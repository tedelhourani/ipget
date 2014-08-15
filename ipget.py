#!/usr/bin/env python

#   ip_get daemon
#   dependencies: python-daemon
#
#   Copyright (C) 2014  Theodore Elhourani
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
try:
    import subprocess
    import imaplib
    import ConfigParser
    import os
    import smtplib
    import time
    from daemon import runner
    from email.mime.text import MIMEText
except ImportError as error:
    print 'module {0} not installed'.format(error.message[16:])
    exit(1)

class IpGet():
    def __init__(self, address, password):
        self.check_frequency = 60
        self.getipcommand = 'curl -s http://checkip.dyndns.org/ | cut -d \' \' -f 6 | sed s/\"body\|html\|<\|>\|\/\"//g'
        self.IMAP = 'imap.gmail.com'
        self.SMTP = 'smtp.gmail.com'
        # using email address
        self.username = address
        self.password = password
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path = '/tmp/ipget.pid'
        self.pidfile_timeout = 5

    def open_imap_connection(self, verbose=False):
        if verbose: print 'Connecting to', self.IMAP
        connection = imaplib.IMAP4_SSL(self.IMAP)
        if verbose: print 'Logging in as', self.username
        connection.login(self.USERNAME, self.password)
        return connection

    def respond(self, verbose=False):
        p = subprocess.Popen(self.getipcommand, shell=True, stdout=subprocess.PIPE)
        ipaddress = p.communicate()[0].split()[0]
        msg = MIMEText( ipaddress )
        msg['Subject'] = 'ipaddress'
        msg['From'] = self.USERNAME
        msg['To'] = self.USERNAME
        s = smtplib.SMTP(self.SMTP, 587)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login( self.USERNAME, self.PASSWORD)
        s.sendmail(self.USERNAME, [self.USERNAME], msg.as_string() )
        s.quit()
        if verbose: print '\nresponded to request '+ipaddress+'\n'

    def run(self):
        while True:
            c = self.open_imap_connection(verbose=False)
            try:
                c.select('INBOX', readonly=False)
                criterion = '(FROM \"'+self.USERNAME+'\") (SUBJECT \"iprequest")'
                typ, [msg_ids] = c.search(None, criterion)
                if msg_ids:
                    self.respond(verbose=False)
                    for msg_id in msg_ids.split():
                        typ, response = c.store(msg_id, '+FLAGS', '\\Deleted')
                    typ, response = c.expunge()
            finally:
                c.logout()
            time.sleep( self.check_frequency )

if __name__ == '__main__':
    address = raw_input('email address:')
    password = raw_input('password:')
    ipget = IpGet(address, password)
    daemon_runner = runner.DaemonRunner(ipget)
    daemon_runner.do_action()
