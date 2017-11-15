import torch
from copy import deepcopy

from games.utils import is_game_finished, calc_reward, process_action

class GameEnv:
    def __init__(self, height, width, obstacles):
        self.height = height
        self.width = width
        self.obstacles = obstacles
        self.grid = None
        self.dtype = torch.FloatTensor

    def reset(self):
        grid = torch.zeros((1, 1, self.height, self.width)).type(self.dtype)
        #  mark the player starting positions
        grid[:, :, self.height - 1, 0] = 1
        grid[:, :, 0, self.width - 1] = 2
        for obstacle_pos in self.obstacles:
            i, j = obstacle_pos
            grid[:, :, i, j] = -1
        self.grid = grid

    def step(self, action, turn):
        new_state = process_action(deepcopy(self.grid), action, turn)
        reward = self.dtype([ calc_reward(new_state) ])
        done = is_game_finished(new_state)
        return new_state, reward, done, None
