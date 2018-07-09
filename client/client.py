#!/usr/bin/python3
import socket
import sys
import getopt
from configparser import ConfigParser


def helpInfo():
    print('./client.py -h \t for help')
    print('./client.py -i remote_ip \t set remote ip')
    print('./client.py -p remote_port \t set remote port')
    print('./client.py -f filename \t download file from remote host')


def main(argv):
    cfg = ConfigParser()
    cfg.read('conf.ini')

    IP = cfg.get('server', 'ip')
    PORT = cfg.getint('server', 'port')
    FILE = cfg.get('file', 'file')

    try:
        opts, args = getopt.getopt(argv, 'hi:p:f:')
    except getopt.GetoptError:
        helpInfo()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            helpInfo()
        elif opt == '-i':
            IP = arg
        elif opt == '-p':
            PORT = int(arg)
        elif opt == '-f':
            FILE = arg

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((IP, PORT))

    sock.send(bytes(FILE, encoding='utf8'))

    info = sock.recv(2)
    print(info)
    if str(info, encoding='utf8') == 'ok':
        fp = open(FILE, 'wb')
        if not fp:
            print("open file error.\n")
        else:
            while(True):
                buff = sock.recv(2048)
                if not buff:
                    break
                else:
                    fp.write(buff)
            print("download file {} from server {} finished.".format(FILE, IP))
            fp.close()
    else:
        print('no file {} in server : {}'.format(FILE, IP))
    sock.close()


if __name__ == '__main__':
    main(sys.argv[1:])
