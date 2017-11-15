import pdb
from itertools import count

#  local imports 
from agents.dqn_agent import DQNAgent
from games.basic_game import GameEnv

class LearningEngine:
    def __init__(self, model_name, play_self=True):
        self.agent_a = DQNAgent(model_name, 100, 2, 0.3, 0.4)
        self.agent_b = None if play_self else DQNAgent(model_name, 100, 2, 0.3, 0.4)
        self.env = None

    def init_game(self, width, height, obstacles):
        self.env = GameEnv(width, height, obstacles)

    def train_agent(self, nb_episodes):
        for episode_idx in range(nb_episodes):
            self.env.reset()
            state, reward, done, _ = self.env.step(0, 0)

            #  play the game
            for step_idx in count():
                #  set current player based on turn
                current_agent = self.agent_a if step_idx % 2 == 0 else self.agent_b

                #  select an action and then perform it
                #  pdb.set_trace()
                action = current_agent.select_action(state)
                next_state, reward, done, _ = self.env.step(action[0,0], step_idx % 2)

                # Store the transition in memory
                current_agent.memory.remember(state, action, next_state, reward)

                # Move to the next state
                state = next_state

                # Perform one step of the optimization (on the target network)
                current_agent.optimize()
                
                if done: break
