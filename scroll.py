#!/usr/bin/python3

# scroll.py - Pass commands from a web UI to the scroll pHat server

import cgi
import socket
import configparser
import os

# get_server_address - get the host and port values from an .ini file
def get_server_address(file_name):
    # if file_name is not an absolute path, use the root path of the executing file.
    if not os.path.isabs(file_name):
        file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name)
    parser = configparser.ConfigParser()
    parser.read(file_name)
    host = parser.get('server_address', 'host')
    port = parser.getint('server_address', 'port')
    return host, port

# Main - parse CGI paramaters and pass message to server
def Main():
    # Get the server address
    server_address = get_server_address('socket.ini')
  
    # Create the message per the passed CGI paramaters
    form = cgi.FieldStorage()
    if "w" in form:     # set text
        text = form.getvalue("w")
        message = "0:" + text
    if "b" in form:     # set brightness
        bright = form.getvalue("b")
        message = "1:" + bright
    if "i" in form:     # invert
         message = "2:"
        
    # Create a TCP/IP socket, and connect to the port where the server is listening.
    sock = socket.socket()
    try:
        sock.connect(server_address)
    
        # Send the message to the server.
        sock.send(message.encode())
        sock.close()
    except ConnectionRefusedError:
        print("Scrolling display server not running")
    except:
        print("Bad or missing paramater")
    
if __name__ == '__main__':
    Main()
