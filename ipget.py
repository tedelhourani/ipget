#!/usr/bin/env python
#
# ip_get daemon
# prerequisites: python-daemon
#
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
        self.CHECK_FREQUENCY = 60
        self.getipcommand = 'curl -s http://checkip.dyndns.org/ | cut -d \' \' -f 6 | sed s/\"body\|html\|<\|>\|\/\"//g'
        self.IMAP = 'imap.gmail.com'
        self.SMTP = 'smtp.gmail.com'
        # using email address
        self.USERNAME = address
        self.PASSWORD = password
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path = '/tmp/ipget.pid'
        self.pidfile_timeout = 5

    def open_imap_connection(self, verbose=False):
        if verbose: print 'Connecting to', self.IMAP
        connection = imaplib.IMAP4_SSL(self.IMAP)
        if verbose: print 'Logging in as', self.USERNAME
        connection.login(self.USERNAME, self.PASSWORD)
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
            time.sleep( self.CHECK_FREQUENCY )

if __name__ == '__main__':
    address = raw_input('email address:')
    password = raw_input('password:')
    ipget = IpGet(address, password)
    daemon_runner = runner.DaemonRunner(ipget)
    daemon_runner.do_action()
