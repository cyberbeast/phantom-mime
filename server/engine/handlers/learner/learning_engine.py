import pdb
from itertools import count

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

    def train_agent(self, opponent, nb_episodes):
        for episode_idx in range(nb_episodes):
            self.env.reset()
            state, reward, done, _ = self.env.step(0, 0)

            #  play the game
            for step_idx in count():
                #  set current player based on turn
                current_agent = self.agent if step_idx % 2 == 0 else opponent

                #  select an action and then perform it
                action = current_agent.select_action(state)
                next_state, reward, done, _ = self.env.step(action[0,0], step_idx % 2)

                # Store the transition in memory
                current_agent.memory.remember(state, action, next_state, reward)

                # Move to the next state
                state = next_state

                # Perform one step of the optimization (on the target network)
                current_agent.optimize()
                
                if done: break
