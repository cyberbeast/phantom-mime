import torch
from copy import deepcopy

from games.basic_game import BasicGame 

class GameEnv:
    def __init__(self, height, width, obstacles):
        self.height = height
        self.width = width
        self.obstacles = obstacles
        self.grid = None
        self.dtype = torch.FloatTensor
        self.game_logic = BasicGame()

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
        new_state = self.game_logic.process_action(deepcopy(self.grid), 
                                                    action, turn)
        reward = self.dtype([ self.game_logic.calc_reward(new_state) ])
        done = self.game_logic.is_game_finished(new_state)
        return new_state, reward, done, None
