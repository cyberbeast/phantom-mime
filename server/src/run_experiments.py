from __future__ import print_function

import os, sys, pdb
sys.path.insert(0, os.environ['DQN_ROOT'])
print(sys.path)

from itertools import count

from src.agents.dqn_agent import DQNAgent
from src.models.basic_model import QNet 
from src.games.basic_game import GameEnv

def train_agent(agent, env, nb_episodes=10):
    for episode_idx in range(nb_episodes):
        env.reset()
        state, reward, done, _ = env.step(0)

        #  play the game
        for step_idx in count():
            #  select an action and then perform it
            pdb.set_trace()
            action = agent.select_action(state)
            next_state, reward, done, _ = env.step(action[0,0])

            # Store the transition in memory
            agent.memory.remember(state, action, next_state, reward)

            # Move to the next state
            state = next_state

            # Perform one step of the optimization (on the target network)
            agent.optimize()

            if done: break

if __name__ == '__main__':

    model = QNet()
    components = {'player': [(0,199), (199,0)], 'obstacles': [(2,3), (42, 67), (99, 102)]}
    game_env = GameEnv(200, 200, components)
    agent = DQNAgent(model, 100, 2, 0.3, 0.4)
    train_agent(agent,game_env)
