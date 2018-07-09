#!/usr/bin/python3

import threading
import socketserver
from configparser import ConfigParser


class ThreadTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        cfg = ConfigParser()
        cfg.read('conf.ini')
        self.buff_size = cfg.getint('env', 'buffer_size')

        sock = self.request
        data = sock.recv(200)
        filename = str(data, encoding='utf8')
        fp = open(filename, 'rb')
        
        if not fp:
            print("open file error.\n")
            sock.send(bytes("open file error.", encoding='utf8'))
            pass
        else:
            sock.send(bytes('ok', encoding='utf8'))
            while(True):
                buff = fp.read(self.buff_size)
                if not buff:
                    break
                else:
                    sock.send(buff)
            print("send file {} to {} finished.".format(filename, sock.getpeername()))
            fp.close()
            sock.close()


class ThreadTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def main():
    cfg = ConfigParser()
    cfg.read('conf.ini')
    IP = cfg.get('server', 'ip')
    PORT = cfg.getint('server', 'port')

    server = ThreadTCPServer((IP, PORT), ThreadTCPRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()


if __name__ == '__main__':
    main()
