#!/usr/bin/python3

# server.py - Test server for web services.
# Monitor a TCP port for messages to be displayed on the pimoroni scroll phat hd.

import socket
import scrollphathd
import configparser
import logging
import signal
import sys
import os
import datetime

sock = 0

# expand_file_name - If file_name is not an absolute path, prepend the root 
#                    path of the executing file.
def expand_file_name(file_name):
    if os.path.isabs(file_name):
        return file_name
    else:
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name)

# get_server_address - get the host and port values from an .ini file
def get_server_address(file_name):
    file_name = expand_file_name(file_name)
    parser = configparser.ConfigParser()
    parser.read(file_name)
    host = parser.get('server_address', 'host')
    port = parser.getint('server_address', 'port')
    return host, port

# cleanup - Close any open resource
def cleanup():
    logging.debug(str(datetime.datetime.now()) + " Server terminated")
    sock.close()
    logging.shutdown()

# sig_term_handler - Handle SIGTERM (e.g. kill) signal
def sig_term_handler(signal, frame):
    cleanup()
    sys.exit(0)

# Main - recive and print messages.
def Main():
    # Setup signal handler so we can run in background.
    signal.signal(signal.SIGTERM, sig_term_handler)

    # Enable basic logging
    file_name = expand_file_name('server.log')
    logging.basicConfig(filename=file_name,
                        filemode='w',
                        level=logging.DEBUG)

    # Get socket infomration.
    server_address = get_server_address('socket.ini')

    # Create and intilize a TCP/IP socket.
    global sock
    sock = socket.socket()
    sock.bind(server_address)
    sock.settimeout(0.05)
    
    # Set defaults for scrolling display.
    scrollphathd.set_brightness(0.25)
    isFliped = False
    
    # Let the user know the server has started.
    logging.debug(str(datetime.datetime.now()) + " Server started")
    if os.getpgrp() == os.tcgetpgrp(sys.stdout.fileno()):
        print("Server started, ctrl-c to exit")
    else:
        print("Server started, 'kill {}' to exit".format(os.getpid()))

    # Listen for incomming connections.
    sock.listen(1)
    try:
        while True:
            # Wait for a connection.
            try:
                conn, addr = sock.accept()
                logging.debug(str(datetime.datetime.now()) +" Connection from: " + str(addr))
                while True:
                    data = conn.recv(1024).decode()
                    if not data:
                            conn.close()
                            break
                    command, junk, data = data.partition(':')
                    # Parse the command.
                    if command == "0":   # message
                        scrollphathd.clear()
                        scrollphathd.write_string(data, x=17) # 17 for scroll
                                                              # 0 for static
                    elif command == "1": # set brightness
                        scrollphathd.set_brightness(float(data))
                    elif command == "2": # invert display
                        if isFliped:
                            scrollphathd.flip(x=False, y=False)
                            isFliped = False
                        else:
                            scrollphathd.flip(x=True, y=True)
                            isFliped = True
            except socket.timeout:
                # On socket timeout, scroll the displayed message.
                scrollphathd.show()
                scrollphathd.scroll(1) # comment this out for static
    except KeyboardInterrupt:
        cleanup()
     
if __name__ == '__main__':
    Main()