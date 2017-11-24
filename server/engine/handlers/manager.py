import os, sys, argparse, pdb
sys.path.insert(0, os.environ['DQN_ROOT'])

import numpy as np, redis, json, random
from pickle import loads, dumps
from pymongo import MongoClient

from learner.learning_engine import LearningEngine

client = MongoClient(os.environ['MONGO_HOST'])

def ping():
    return "pong"

def _generate_obstacles(mx, my, max_removed):
    maze = [[0 for x in range(mx)] for y in range(my)]
    dx = [0, 1, 0, -1]; dy = [-1, 0, 1, 0] # 4 directions to move in the maze
    # start the maze from a random cell
    stack = [(0,mx-1),(my-1, 0)]

    while len(stack) > 0:
        (cx, cy) = stack[-1]
        maze[cy][cx] = 1
        # find a new cell to add
        nlst = [] # list of available neighbors
        for i in range(4):
            nx = cx + dx[i]; ny = cy + dy[i]
            if nx >= 0 and nx < mx and ny >= 0 and ny < my:
                if maze[ny][nx] == 0:
                    # of occupied neighbors must be 1
                    ctr = 0
                    for j in range(4):
                        ex = nx + dx[j]; ey = ny + dy[j]
                        if ex >= 0 and ex < mx and ey >= 0 and ey < my:
                            if maze[ey][ex] == 1: ctr += 1
                    if ctr == 1: nlst.append(i)
        # if 1 or more neighbors available then randomly select one and move
        if len(nlst) > 0:
            ir = nlst[random.randint(0, len(nlst) - 1)]
            cx += dx[ir]; cy += dy[ir]
            stack.append((cx, cy))
        else: stack.pop()

    grid = np.array(maze)

    rocks_y, rocks_x = list(map(lambda x: x.tolist(), np.where(grid == 0)))
    rock_ls = list(zip(rocks_y, rocks_x))

    num_remove = np.random.randint(max_removed)
    print('\nRemoving {} obstacles from total {} obstacles'.format(num_remove, len(rock_ls)))
    for i in range(num_remove):
        remove_idx = random.randint(0, len(rock_ls))
        rock_ls.pop(remove_idx)
    
            
    return rock_ls

def next_move(user_key, retry_limit=5):
    action_ls = ['up', 'down', 'left', 'right']
    
    #  initialize connection to redis
    r = redis.Redis(host='redis')

    #  get the learner object from the user's store
    init_user_state = r.get(user_key)
    learner = loads(init_user_state['learning_engine'])

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

def init_learning_engine(user_key, fbid):
    print('\nInitializing learning engine. Please wait..')
    learner = LearningEngine(os.environ['MODEL_NAME'])

    #  randomly generate obstacles ( upto square root of number of cells )
    game_width, game_height = int(os.environ['WIDTH']), int(os.environ['HEIGHT'])
    obstacles = _generate_obstacles(game_width, game_height, 10)
    player_pos = [ (game_height-1, 0), (0, game_width-1) ]
    learner.init_game(game_width, game_height, obstacles)

    print('Learning engine initialization complete!\n')

    game_meta = { 'grid_height': game_height, 'grid_width': game_width, \
                    'player_pos': player_pos ,  'obstacles': obstacles }
    r = redis.Redis(host='redis')
    status = r.get(user_key).decode("utf-8")
    if status == 'READY':
        client.admin.users.update_one({
            'id': fbid
        }, {
            "$set": {
                'learning_engine': dumps(learner)
            }
        })
        user_state = {}
        user_state['game_meta'] = game_meta
        # Write to redis.
        r.set(user_key, json.dumps(user_state))
        # Respond to request with dictionary.
        response_data = {
            "boardSize": {
                "width": game_meta['grid_width'],
                "height": game_meta['grid_height']
            },
            "playerPositions": game_meta['player_pos'],
            "obstaclePositions": game_meta['obstacles']
        }
        return response_data
    else:
        return {
            "error": "INIT FAILURE"
        }

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--mode', default='train', help='mode to run the learner in')
    parser.add_argument('--nb_epochs', type=int, default=10, 
                            help='number of epochs to train agent for')

    args = parser.parse_args()
    
    #  pdb.set_trace()
    learner = init_learning_engine()
    next_move(learner, 'up', 1)
