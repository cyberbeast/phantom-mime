import pdb
from itertools import count

import logging
logger = logging.getLogger(__name__)

#  local imports 
from agents.dqn_agent import DQNAgent
from games.game_env import GameEnv

class LearningEngine:
    def __init__(self, learner_type):
        self.agent = DQNAgent(100, 2, 0.3, 0.4)
        self.env = None

        #  set the model for the learning engine depending on
        #  learning type
        if learner_type == 'the_rival':
            self.agent.init_model('qnet')
        else:
            #  placeholder: replace with proper model name for mime
            self.agent.init_model('qnet')


    def init_game(self, width, height, obstacles):
        self.env = GameEnv(width, height, obstacles)
        self.env.reset()

    def train_agent(self, opponent, nb_episodes, play_self):
        for episode_idx in range(nb_episodes):
            # logger.info(episode_idx, extra={ 'tags': ['dev_mssg: episode_idx'] })
            self.env.reset()
            state, reward, done, _ = self.env.step(0, 1)

            max_plies = 30
            #  play the game
            for step_idx in count(1):

                # break out of game if too many turns and no one has won
                if step_idx > max_plies: break

                # logger.info(step_idx, extra={ 'tags': ['dev_mssg: step_idx'] })
                #  set current player based on turn
                current_agent = self.agent if step_idx % 2 == 0 else opponent

                #  select an action and then perform it
                action = current_agent.select_action(state)
                next_state, reward, done, _ = self.env.step(action[0,0], (step_idx % 2) + 1)

                # Store the transition in memory
                current_agent.memory.remember(state, action, next_state, reward)

                # Move to the next state
                state = next_state

                # Perform one step of the optimization (on the target network)
                if play_self or step_idx % 2 == 0:
                    current_agent.optimize()
                
                if done: break
