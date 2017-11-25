import os, sys, argparse, pdb
sys.path.insert(0, os.environ['DQN_ROOT'])

import numpy as np, redis, json, random
from pickle import loads, dumps
from pymongo import MongoClient

from rival.learning_engine import LearningEngine

client = MongoClient(os.environ['MONGO_HOST'])
r = redis.Redis(host='redis')

def ping():
    return "pong"

def _fast_forward_game(learner, game_meta, moves):
    for i in range(0, len(moves), 2):
        user_action, user_turn = moves[i:i+1]

        #  get the current state of the game post user action
        _, _, _, _ = learner.env.step(action_ls.index(user_action), user_turn)

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

def init_learning_engine(fbid, game_key, mode='train', delimiter=':'):
    print('\nInitializing learning engine. Please wait..')
    #  get user data from mongodb
    user_data = client.admin.users.find_one({ 'id': fbid })
    
    #  break out if no user data found
    if user_data is None: return False

    #  get game meta data from session
    game_meta = json.loads(r.get(game_key + delimiter + 'game_meta'))

    #  TODO: check if session data is legit
    game_width, game_height = game_meta['grid_width'], game_meta['grid_height']
    obstacles = game_meta['obstacles']

    learner_name = 'the_rival' if mode == 'train' else 'mime'

    #  init the learner
    rival = LearningEngine(learner_name)
    rival.init_game(game_width, game_height, obstacles)

    #  TODO: fast forward game
    moves = r.get(game_key + delimiter + 'moves')
    _fast_forward_game(learner, game_meta, moves)

    #  load saved weights if any, store model initial weights otherwise
    if (learner_name + '_weights') in user_data:
        rival.agent.load_weights(user_data[learner_name + '_weights'])
    else:
        user_data[learner_name + '_weights'] = rival.agent.save_weights()

    #  save the learner in mongodb for use later
    user_data[learner_name] = dumps(rival)

    print('Learning engine initialization complete!\n')
    client.admin.users.update_one({ 'id': fbid }, { "$set": user_data })

    return True 

def next_move(game_key, fbid, mode='train', retry_limit=5):
    action_ls = ['up', 'down', 'left', 'right']
    
    #  get learning engine from user data
    user_data = client.find_one({ 'id': fbid })
    rival = user_data['the_rival'] if mode == 'train' else user_data['mime']

    while True:
        #  get user's recent action and game turn from session data
        moves = r.get(game_key + delimiter + 'moves')
        user_action, user_turn = moves[0:2]

        #  get the current state of the game post user action
        print('\nUpdating game state by user action..')
        state, _, _, _ = rival.env.step(action_ls.index(user_action), user_turn)
        
        #  make agent choose an action
        print('\nUpdating game state by agent action...')
        agent_action = rival.agent.select_action(state)
        next_state, _, _, _ = rival.env.step(agent_action[0, 0], (turn + 1) % 2)
        retries = 0

        #  repeat if chosen action is invalid
        while np.array_equal(state.cpu().numpy(), next_state.cpu().numpy()):
            print('\nUpdating game state by agent action (retry {})...'.format(retries))
            #  agent chooses randomly if too many invalid moves are chosen
            #  otherwise choose from learned weights
            agent_action = rival.agent.select_action(state, retries < retry_limit)
            next_state, _, done, _ = rival.env.step(agent_action[0, 0], (turn + 1) % 2)
            retries += 1

        moves.append([ action_ls[agent_action[0, 0]], (turn + 1) % 2 ])
        r.set(game_key + delimiter + 'moves')
        status = True

        yield status 

def init_game(game_key, delimiter=':'): 
    #  get user status
    status = r.get(game_key).decode("utf-8")
    if status == 'READY':
        #  randomly generate obstacles 
        game_meta = {}
        game_meta['grid_width'] = int(os.environ['WIDTH'])
        game_meta['grid_height'] = int(os.environ['HEIGHT'])
        game_meta['obstacles'] = _generate_obstacles(game_width, game_height, 10)
        game_meta['player_pos'] = [ (game_height-1, 0), (0, game_width-1) ]
        
        # write session data to redis.
        r.set(game_key + delimiter + 'game_meta', json.dumps(session_data))

        # send back game metadata as response
        response_data = {
            "boardSize": {
                "width": game_meta['grid_width'],
                "height": game_meta['grid_height']
            },
            "playerPositions": game_meta['player_pos'],
            "obstaclePositions": game_meta['obstacles']
        }
        return response_data

    return {
        "error": "INIT FAILURE"
    }

def launch_training(fbid, learner_name, n_iters=500):
    user_data = client.admin.users.find_one({ 'id': fbid })
    learner = user_data[learner_name]
    learner.agent.load_weights(user_data[learner_name + '_weights'])
    learner.train_agent(learner, n_iters, learner_name == 'the_rival')
    user_data[learner_name + '_weights'] = learner_name.agent.save_weights()
    client.admin.users.update_one({ 'id': fbid }, { '$set': user_data })
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--mode', default='train', help='mode to run the rival in')
    parser.add_argument('--nb_epochs', type=int, default=10, 
                            help='number of epochs to train agent for')

    args = parser.parse_args()
    
    #  pdb.set_trace()
    rival = init_learning_engine()
    next_move(rival, 'up', 1)
