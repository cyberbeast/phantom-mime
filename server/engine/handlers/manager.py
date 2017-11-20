import os, sys, argparse, pdb
sys.path.insert(0, os.environ['DQN_ROOT'])

import numpy as np, redis

from learner.learning_engine import LearningEngine

def ping():
    return "pong"

def generate_obstacles(x_max, y_max, obstacles_lim):
    np.random.seed(int(os.environ['RANDOM_SEED']))
    num_obstacles = np.random.randint(obstacles_lim)
    obstacle_x = np.random.randint(x_max, size=num_obstacles-1) 
    obstacle_y = np.random.randint(y_max, size=num_obstacles-1) 
    obstacles = set([ (i, j) for i, j in zip(obstacle_x, obstacle_y) ])
    return list(obstacles)

def next_move(user_key, retry_limit=5):
    action_ls = ['up', 'down', 'left', 'right']
    
    #  initialize connection to redis
    r = redis.Redis(host='redis')

    #  get the learner object from the user's store
    init_user_state = r.get(user_key)
    learner = init_user_state['learning_engine']

    while True:
        #  get updated action and turn from user store
        curr_user_state = r.get(user_key)
        user_action, turn = curr_user_state['action'], curr_user_state['turn']

        #  get the current state of the game post user action
        print('\nUpdating game state by user action..')
        state, _, _, _ = learner.env.step(action_ls.index(user_action), turn)
        
        #  make agent choose an action; repeat if chosen action is invalid
        print('\nUpdating game state by agent action...')
        agent_action = learner.agent.select_action(state)
        next_state, _, _, _ = learner.env.step(agent_action[0, 0], (turn + 1) % 2)
        retries = 0
        while np.array_equal(state.cpu().numpy(), next_state.cpu().numpy()):
            print('\nUpdating game state by agent action (retry {})...'.format(retries))
            #  agent chooses randomly if too many invalid moves are chosen
            #  otherwise choose from learned weights
            agent_action = learner.agent.select_action(state, retries < retry_limit)
            next_state, _, done, _ = learner.env.step(agent_action[0, 0], (turn + 1) % 2)
            retries += 1

        yield action_ls[agent_action[0, 0]]

def init_learning_engine(user_key):
    print('\nInitializing learning engine. Please wait..')
    learner = LearningEngine(os.environ['MODEL_NAME'])

    #  randomly generate obstacles ( upto square root of number of cells )
    game_width, game_height = int(os.environ['WIDTH']), int(os.environ['HEIGHT'])
    obstacles = generate_obstacles(game_width-1, game_height-1, 
                                ( game_width * game_height ) // 2)
    
    player_pos = [ (game_height - 1, 0), (0, game_width - 1) ]
    learner.init_game(game_width, game_height, obstacles)

    print('Learning engine initialization complete!\n')

    game_meta = { 'grid_height': game_height, 'grid_width': game_width, \
                    'player_pos': player_pos ,  'obstacles': obstacles }
    r = redis.Redis(host='redis')
    user_state = r.get(user_key)
    user_state['game_meta'] = game_meta
    user_state['learning_engine'] = learner
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--mode', default='train', help='mode to run the learner in')
    parser.add_argument('--nb_epochs', type=int, default=10, 
                            help='number of epochs to train agent for')

    args = parser.parse_args()
    
    #  pdb.set_trace()
    learner = init_learning_engine()
    next_move(learner, 'up', 1)
