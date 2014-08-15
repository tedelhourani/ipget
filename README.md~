ipget
=====

Retrieves a server's public-facing IP address using email. This script is useful if you need to remote login into a NAT-hidden server, and the public-facing IP address changes frequently or after every router reset. For instance, you are away from home and you need to remote login to a machine connected to the Internet through your ISP. It is safe to assume that the public-facing IP of your router has changed and therefore you need to obtain a valid one. Once you obtain a valid IP address you can remote login to one of your devices behind the NAT. For that to work you should first enable port forwarding for SSH, or even better VPN, on the "router".

The script is run as a daemon on any machine sitting behind the NAT. It periodically checks for public-facing IP address request messages. Once such message is found in the inbox, the script retrieves the public-facing IP address of the server, and sends it along in the subject of a response message.

To use this script simply copy it to your server and run it using "./ipget.py start", or add it to the list of daemons that are automatically started at boot time.

Send a message to yourself with subject line "iprequest" and empty body. A respone must arrive shortly afterwards with the requested IP address in the subject line.
