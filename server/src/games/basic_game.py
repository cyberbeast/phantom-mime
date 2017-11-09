import torch
from copy import deepcopy

from src.games.utils import is_game_finished, calc_reward, process_action

class GameEnv:
    def __init__(self, height, width, components):
        self.height = height
        self.width = width
        self.components = components
        self.grid = None
        self.dtype = torch.FloatTensor

    def reset(self):
        grid = torch.zeros((1, 1, self.height, self.width)).type(self.dtype)
        for component_type, component in list(self.components.items()):
            for pos in component:
                mark = -1 if component_type == 'obstacle' else 1 
                i, j = pos
                grid[:, :, i, j] = mark
        self.grid = grid

    def step(self, action):
        new_state = process_action(deepcopy(self.grid), action)
        reward = self.dtype([ calc_reward(new_state) ])
        done = is_game_finished(new_state)
        return new_state, reward, done, None
                
