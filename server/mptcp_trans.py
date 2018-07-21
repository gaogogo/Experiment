import time
import mpsched


class Env():
    def __init__(self, fd, time, k, alpha, b, c):
        self.fd = fd
        self.time = time
        self.k = k
        self.alpha = alpha
        self.b = b
        self.c = c

        self.last = []
        self.tp = [[], []]
        self.rtt = [[], []]
        self.dRtt = [[], []]
        self.cwnd = [[], []]
        self.rr = []
        self.in_flight = []

    def adjust(self, state):
        for j in range(len(state)):
            self.tp[j].pop(0)
            self.tp[j].append(state[j][0]-self.last[j][0])
            self.rtt[j].pop(0)
            self.rtt[j].append(state[j][1])
            self.dRtt[j].pop(0)
            self.dRtt[j].append(state[j][1]-self.last[j][1])
            self.cwnd[j].pop(0)
            self.cwnd[j].append(state[j][2])
            self.rr[j] = state[j][3]
            self.in_flight[j] = state[j][4]
        self.last = state
        return [self.tp[0]+self.rtt[0]+self.cwnd[0]+[self.rr[0], self.in_flight[0]], self.tp[1]+self.rtt[1]+self.cwnd[1]+[self.rr[1], self.in_flight[1]]]

    def reward(self):
        rewards = self.alpha * (sum(self.tp[0]) + sum(self.tp[1]))
        rewards = rewards - self.b * (sum(self.dRtt[0]) + sum(self.dRtt[1]));
        rewards = rewards - self.c * (self.rr[0] + self.rr[1])
        return rewards

    def reset(self):
        mpsched.persist_state(self.fd)
        """time.sleep()"""
        self.last = mpsched.get_sub_info(self.fd)
        self.rr.append(self.last[0][3])
        self.rr.append(self.last[1][3])
        self.in_flight.append(self.last[0][4])
        self.in_flight.append(self.last[1][4])

        for i in range(self.k):
            subs = mpsched.get_sub_info(self.fd)
            for j in range(len(subs)):
                self.tp[j].append(subs[j][0] - self.last[j][0])
                self.rtt[j].append(subs[j][1])
                self.dRtt[j].append(subs[j][1] - self.last[j][1])
                self.cwnd[j].append(subs[j][2])
                self.rr[j] = subs[j][3]
                self.in_flight[j] = subs[j][4]
            self.last = subs
            time.sleep(self.time)

        return [self.tp[0]+self.rtt[0]+self.cwnd[0]+[self.rr[0], self.in_flight[0]], self.tp[1]+self.rtt[1]+self.cwnd[1]+[self.rr[1], self.in_flight[1]]]

    def step(self, action):
        A = [self.fd, action[0], action[1]]
        mpsched.set_seg(A)
        time.sleep(self.time)
        state_nxt = mpsched.get_sub_info(self.fd)
        done = False
        if len(state_nxt) == 0:
            done = True

        return  done
