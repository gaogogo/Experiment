#!/usr/bin/python3

import threading
import socketserver
import pickle
import os
import time
from configparser import ConfigParser
import torch
import numpy as np
from replay_memory import ReplayMemory
from naf_cnn import NAF_CNN
from agent import Agent_Off_Policy, Agent_On_Policy
from gym import spaces


class trian_thread(threading.Thread):

    def __init__(self, nn, memory, episode, batch_size, interval):
        threading.Thread.__init__(self)
        self.nn = nn
        self.memory = memory
        self.episode = episode
        self.batch_size = batch_size
        self.interval = interval

    def run(self):
        agent = Agent_Off_Policy(
                                    nn=self.nn,
                                    memory=self.memory,
                                    episode=self.episode,
                                    batch_size=self.batch_size
                                )
        while True:
            agent.train()
            time.sleep(self.interval)


class ThreadTCPRequestHandler(socketserver.BaseRequestHandler):

    def setup(self):
        self.cfg = self.server.cfg
        self.replaymemory = self.server.replaymemory
        self.buff_size = self.cfg.getint('env', 'buffer_size')

    def handle(self):

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
            agent = Agent_On_Policy(fd=sock.fileno(), cfg=self.cfg, memory=self.replaymemory)
            agent.start()
            while(True):
                buff = fp.read(self.buff_size)
                if not buff:
                    break
                else:
                    sock.send(buff)
            # print("send file {} to {} finished.".format(filename, sock.getpeername()))
            fp.close()
            sock.close()
            agent.join()


class ThreadTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

    def __init__(self, server_address, RequestHandlerClass, cfg, replaymemory):
        socketserver.TCPServer.__init__(self, server_address, RequestHandlerClass)
        self.cfg = cfg
        self.replaymemory = replaymemory


def main():
    cfg = ConfigParser()
    cfg.read('conf.ini')
    IP = cfg.get('server', 'ip')
    PORT = cfg.getint('server', 'port')
    AGENT_FILE = cfg.get('nafcnn', 'agent')
    MEMORY_FILE = cfg.get('replaymemory', 'memory')
    INTERVAL = cfg.getint('train', 'interval')
    EPISODE = cfg.getint('train', 'episode')
    BATCH_SIZE = cfg.getint('train', 'batch_size')

    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            memory = pickle.load(f)
            f.close()
    else:
        memory = ReplayMemory(cfg.getint('replaymemory', 'capacity'))

    if not os.path.exists(AGENT_FILE):
        agent = NAF_CNN(
                            gamma=cfg.getfloat('nafcnn', 'gamma'),
                            tau=cfg.getfloat('nafcnn', 'tau'),
                            hidden_size=cfg.getint('nafcnn', 'hidden_size'),
                            num_inputs=cfg.getint('env', 'k')*3 + 2,
                            action_space=spaces.Box(np.array([1]), np.array([4])),
                        )
        torch.save(agent, AGENT_FILE)

    server = ThreadTCPServer(
                               server_address=(IP, PORT),
                               RequestHandlerClass=ThreadTCPRequestHandler,
                               cfg=cfg,
                               replaymemory=memory
                            )
    server_thread = threading.Thread(target=server.serve_forever)
    # t = trian_thread(AGENT_FILE, memory, EPISODE, BATCH_SIZE, INTERVAL)
    try:
        server_thread.start()
        # t.start()
    except KeyboardInterrupt:
        with open(MEMORY_FILE, 'w') as f:
            pickle.dump(memory, f)
            f.close()


if __name__ == '__main__':
    main()
