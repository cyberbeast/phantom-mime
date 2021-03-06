import logging, matplotlib, io, base64, pdb
matplotlib.use('Agg')


import matplotlib.pyplot as plt, seaborn as sns
from itertools import count

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
            #  placeholder: replace with more suitable model for mime if there exists 
            self.agent.init_model('qnet')

    def init_game(self, width, height, obstacles):
        self.env = GameEnv(width, height, obstacles)
        self.env.reset()

    def train_mime(self, opponent, move_history, nb_episodes, delimiter=':'):
        action_ls = [ '38', '40', '37', '39' ]

        for episode_idx in range(nb_episodes):
            # logger.info(episode_idx, extra={ 'tags': ['dev_mssg: episode_idx'] })
            self.env.reset()
            #  get initial game state by enacting first user move
            user_action = move_history[0].split(delimiter)[-1]
            state, reward, done, _ = self.env.step(action_ls.index(user_action), 1)

            max_plies = 30
            #  play the game
            for step_idx in count(1):

                # break out of game if too many turns and no one has won
                if step_idx > max_plies: break

                expected_action = move_history[step_idx].split(delimiter)[-1]
                expected_action = action_ls.index(expected_action)
                # logger.info(step_idx, extra={ 'tags': ['dev_mssg: step_idx'] })
                if step_idx % 2 != 0:
                    next_state, _, done, _ = self.env.step(expected_action, (step_idx % 2) + 1)
                else:
                    #  select an action and then perform it
                    action = self.agent.select_action(state)
                    next_state, reward, done, _ = self.env.step(action[0,0], 
                                                    (step_idx % 2) + 1, expected_action)

                    # Perform one step of the optimization (on the target network)
                    self.agent.optimize()

                    # Store the transition in memory
                    self.agent.memory.remember(state, action, next_state, reward)

                # Move to the next state
                state = next_state
                
                if done: break

    def train_agent(self, opponent, nb_episodes, plot_performance=False):
        avg_reward_ls = []

        for episode_idx in range(nb_episodes):
            # logger.info(episode_idx, extra={ 'tags': ['dev_mssg: episode_idx'] })
            self.env.reset()
            state, reward, done, _ = self.env.step(0, 1)

            total_reward, num_plies, max_plies = 0.0, 0, 30
            #  play the game
            for step_idx in count(1):
                num_plies = step_idx

                # break out of game if too many turns and no one has won
                if step_idx > max_plies: break

                # logger.info(step_idx, extra={ 'tags': ['dev_mssg: step_idx'] })
                #  set current player based on turn
                current_agent = self.agent if step_idx % 2 == 0 else opponent

                #  select an action and then perform it
                action = current_agent.select_action(state)
                next_state, reward, done, _ = self.env.step(action[0,0], (step_idx % 2) + 1)
                
                total_reward += reward

                # Store the transition in memory
                current_agent.memory.remember(state, action, next_state, reward)

                # Move to the next state
                state = next_state

                # Perform one step of the optimization (on the target network)
                current_agent.optimize()
                
                if done: break

            avg_reward_ls.append(total_reward / num_plies)

        #  TODO: plot training performance
        if plot_performance:
            img = io.BytesIO()
            _, ax = plt.subplots()
            sns.tsplot(time=list(range(nb_episodes)), data=avg_reward_ls, condition='Training Loss', legend='True', ax=ax)
            ax.set_xlabel('Games')
            ay.set_ylabel('Average Reward')
            plt.savefig(img, format='png')
            img.seek(0)
            return base64.b64encode(img.getvalue()).decode()
        else:
            return None
