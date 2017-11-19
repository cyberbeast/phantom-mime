import os, sys, argparse, pdb
sys.path.insert(0, os.environ['DQN_ROOT'])

import numpy as np

from learner.learning_engine import LearningEngine

def generate_obstacles(x_max, y_max, obstacles_lim):
    np.random.seed(int(os.environ['RANDOM_SEED']))
    num_obstacles = np.random.randint(obstacles_lim)
    obstacle_x = np.random.randint(x_max, size=num_obstacles-1) 
    obstacle_y = np.random.randint(y_max, size=num_obstacles-1) 
    obstacles = set([ (i, j) for i, j in zip(obstacle_x, obstacle_y) ])
    return list(obstacles)

def next_move(learner, user_action, turn, retry_limit=5):
    action_ls = ['up', 'down', 'left', 'right']
    print('\nUpdating game state by user action..')
    state, reward, done, _ = learner.env.step(action_ls.index(user_action), turn)
    
    print('\nUpdating game state by agent action...')
    agent_action = learner.agent.select_action(state)
    next_state, _, done, _ = learner.env.step(agent_action[0, 0], (turn + 1) % 2)
    retries = 0
    pdb.set_trace()
    while np.array_equal(state.cpu().numpy(), next_state.cpu().numpy()):
        print('\nUpdating game state by agent action (retry {})...'.format(retries))
        agent_action = learner.agent.select_action(state, retries < retry_limit)
        next_state, _, done, _ = learner.env.step(agent_action[0, 0], (turn + 1) % 2)
        retries += 1

    return action_ls[agent_action[0, 0]]

def init_learning_engine():
    print('\nInitializing learning engine. Please wait..')
    learner = LearningEngine(os.environ['MODEL_NAME'])

    #  randomly generate obstacles ( upto square root of number of cells )
    game_width, game_height = int(os.environ['WIDTH']), int(os.environ['HEIGHT'])
    obstacles = generate_obstacles(game_width-1, game_height-1, 
                                ( game_width * game_height ) // 2)
    
    learner.init_game(game_width, game_height, obstacles)

    print('Learning engine initialization complete!\n')
    return learner
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--mode', default='train', help='mode to run the learner in')
    parser.add_argument('--nb_epochs', type=int, default=10, 
                            help='number of epochs to train agent for')

    args = parser.parse_args()
    
    #  pdb.set_trace()
    learner = init_learning_engine()
    next_move(learner, 'up', 1)
