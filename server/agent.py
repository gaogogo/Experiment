import threading
import torch
import os
from mptcp_trans import Env
from ounoise import OUNoise
from naf_cnn import NAF_CNN
from replay_memory import ReplayMemory, Transition
import mpsched


class Agent_On_Policy(threading.Thread):

    def __init__(self, fd, cfg, memory, explore=True):
        threading.Thread.__init__(self)
        self.fd = fd
        self.cfg = cfg
        self.memory = memory
        self.explore = explore
        self.agent = torch.load(cfg.get('nafcnn', 'agent'))
        self.ounoise = OUNoise(action_dimension=1)
        mpsched.persist_state(fd)

        self.env = Env(
                        fd=self.fd,
                        time=self.cfg.getfloat('env', 'time'),
                        k=self.cfg.getint('env', 'k'),
                        alpha=self.cfg.getfloat('env', 'alpha'),
                        b=self.cfg.getfloat('env', 'b'),
                        c=self.cfg.getfloat('env', 'c')
                        )

    def run(self):
        state = self.env.reset()
        while True:
            state = torch.FloatTensor(state)
            if self.explore:
                action = self.agent.select_action(state, self.ounoise)
            else:
                action = self.agent.select_action(state)
            # action = [1,1]
            next_state, reward, done = self.env.step(action)

            action = torch.FloatTensor(action)
            mask = torch.Tensor([not done])
            next_state = torch.FloatTensor(next_state)
            reward = torch.FloatTensor([float(reward)])
            self.memory.push(state, action, mask, next_state, reward)
            if done:
                break
            state = next_state


class Agent_Off_Policy:

    """training """

    def __init__(self, nn, memory, episode, batch_size):
        self.memory = memory
        self.nn = nn
        self.episode = episode
        self.batch_size = batch_size

    def train(self):
        agent = torch.load(self.nn)
        for _ in range(self.episode):
            if len(self.memory) > self.batch_size * 5:
                for __ in range(5):
                    transitions = self.memory.sample(self.batch_size)
                    batch = Transition(*zip(*transitions))
                    agent.update_parameters(batch)

        torch.save(agent, self.nn)
