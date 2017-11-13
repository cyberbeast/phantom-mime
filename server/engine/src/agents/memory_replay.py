from collections import namedtuple
from random import sample

Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward'))

class MemoryReplay:
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = [] 
        self.memory_idx = 0

    def _process_batch(self, batch):
        return Transition(*zip(*batch))

    def remember(self, *args):
        transition = Transition(*args)
        if len(self.memory) < self.capacity:
            self.memory.append(transition)
        else:
            self.memory[self.memory_idx] = transition
        self.memory_idx = ( self.memory_idx + 1 ) % self.capacity

    def sample_batch(self, batch_size):
        transition_sample = sample(self.memory, batch_size)

        #  separate the batch of tuples into tuple of batches
        #  [(a: 'a',b: 'b'), (a: 'c',b: 'd')] to 
        #  (a: ['a', 'c'], b: ['b', 'c'])
        return self._process_batch(transition_sample)

    def __len__(self):
        return len(self.memory)
