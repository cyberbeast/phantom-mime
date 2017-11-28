import torch
from copy import deepcopy

import logging
logger = logging.getLogger(__name__)

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

    def step(self, action, turn, expected_action=None):
        new_state = self.game_logic.process_action(self.grid.clone(), action, turn)
        #  logging.exception('Copying tensors broke!')
        reward_val = self.game_logic.calc_reward(self.grid, new_state)
        if expected_action is not None:
            state_for_user = self.game_logic.process_action(self.grid.clone(), expected_action, turn)
            mime_reward = self.game_logic.calc_mime_reward(new_state, state_for_user, turn)
            reward_val += mime_reward

            #  reward mime for making same move as user
            reward_val = reward_val - 3 if action != expected_action else reward_val

        reward = self.dtype([ reward_val ])
        done = self.game_logic.is_game_finished(self.grid)
        self.grid = new_state
        return new_state, reward, done, None
