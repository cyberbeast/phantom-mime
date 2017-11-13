from __future__ import print_function

import torch.nn as nn, torch, torch.optim as optim, torch.nn.functional as F 
from torch.autograd import Variable
import random

from src.models.basic_model import QNet
from src.agents.memory_replay import MemoryReplay

class DQNAgent:
    def __init__(self, model, memory_size, batch_size, epsilon, gamma):
        self.epsilon = epsilon
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.RMSprop(model.parameters())
        self.memory = MemoryReplay(memory_size)
        self.batch_size = batch_size

    def select_action(self, state):
        dtype = torch.FloatTensor
        sample = random.random()
        if sample > self.epsilon:
            state_var = Variable(state, volatile=True).type(dtype)
            q_values = self.model(state_var).data

            #  torch's max fn gives a tuple of max value and position
            #  so we index it at position 1 to get the argmax
            _, action = q_values.max(1)

            return action.view(1,1)
        else:
            return torch.LongTensor([[ random.randrange(2) ]])

    def optimize(self):
        #  only optimize the model if there batch_size number of memories
        if len(self.memory) < self.batch_size:
            return
        transition_batch = self.memory.sample_batch(self.batch_size)

        state_batch = Variable(torch.cat(transition_batch.state))
        next_state_batch = Variable(torch.cat(transition_batch.next_state), volatile=True)
        action_batch = Variable(torch.cat(transition_batch.action))
        reward_batch = Variable(torch.cat(transition_batch.reward))

        # Compute Q(s_t, a) - the model computes Q(s_t), then we select the
        # columns of actions taken
        state_action_values = self.model(state_batch).gather(1, action_batch)

        # Compute V(s_{t+1}) for all next states.
        next_state_values = self.model(next_state_batch).max(1)[0]

        # Now, we don't want to mess up the loss with a volatile flag, so let's
        # clear it. After this, we'll just end up with a Variable that has
        # requires_grad=False
        next_state_values.volatile = False

        # Compute the expected Q values
        expected_state_action_values = (next_state_values * self.gamma) + reward_batch

        # Compute Huber loss
        loss = F.smooth_l1_loss(state_action_values, expected_state_action_values)

        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()

        self.optimizer.step()
