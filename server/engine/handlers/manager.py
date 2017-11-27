import os, sys, argparse, pdb
sys.path.insert(0, os.environ['DQN_ROOT'])

import torch, numpy as np, redis, json, random
from pickle import loads, dumps
from pymongo import MongoClient

import logging

logger = logging.getLogger(__name__)

from learner.learning_engine import LearningEngine

client = MongoClient(os.environ['MONGO_HOST'])
r = redis.Redis(host='redis')
action_ls = ['38', '40', '37', '39']


def ping():
    return "pong"

def _fast_forward_game(learner, game_meta, moves, delimiter=':'):
    for i in range(len(moves), 0, -1):
        user_turn, user_action = map(int, moves[i-1].decode('utf-8').split(delimiter))

        #  get the current state of the game post user action
        _, _, _, _ = learner.env.step(int(action_ls.index(user_action)), user_turn[-1])

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
        remove_idx = random.randint(-1, len(rock_ls)-1)
        rock_ls.pop(remove_idx)
    
    return rock_ls

def init_learning_engine(fbid, game_key, mode, delimiter=':'):
    print('\nInitializing learning engine. Please wait..')
    #  get user data from mongodb
    user_data = client.admin.users.find_one({ 'id': fbid })
    
    #  break out if no user data found
    if user_data is None: return False

    #  check if session data is legit
    if r.exists(game_key + delimiter + 'game_meta') == 0: return False

    #  get game meta data from session
    game_meta = json.loads(r.get(game_key + delimiter + 'game_meta'))

    game_width, game_height = game_meta['grid_width'], game_meta['grid_height']
    obstacles = game_meta['obstacles']

    learner_name = 'the_rival' if mode == 'trainAI' else 'mime'

    #  init the learner
    rival = LearningEngine(learner_name)
    rival.init_game(game_width, game_height, obstacles)

    # fast forward game
    if r.exists(game_key + delimiter + 'moves') == 0:
        moves = r.lrange(game_key + delimiter + 'moves',0,-2)
        logger.info(moves, extra={ 'tags': ['dev_mssg:MOVES']})
        if len(moves) > 0:
            _fast_forward_game(rival, game_meta, moves)
    
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

def init_game(game_key, delimiter=':'): 
    #  get user status
    status = r.get(game_key).decode("utf-8")
    if status == 'READY':
        game_meta = r.get(game_key + delimiter + 'game_meta')
        if  game_meta is None:
            #  randomly generate obstacles
            game_width, game_height = int(os.environ['WIDTH']), int(os.environ['HEIGHT']) 
            game_meta = {}
            game_meta['grid_width'] = game_width
            game_meta['grid_height'] = game_height
            game_meta['obstacles'] = _generate_obstacles(game_width, game_height, 30)
            game_meta['player_pos'] = [ (game_height-1, 0), (0, game_width-1) ]
        
            # write session data to redis.
            r.set(game_key + delimiter + 'game_meta', json.dumps(game_meta))
        else:
            game_meta = json.loads(game_meta)

        print("LOOK HERE FOR: " + game_key)
        print(game_meta)

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

def launch_training(fbid, learner_name, n_iters=1000):
    # load the primary learning engine
    user_data = client.admin.users.find_one({ 'id': fbid })
    learner = loads(user_data[learner_name])
    learner.agent.load_weights(user_data[learner_name + '_weights'])
    
    # load appropriate opposing engine
    if learner_name == 'mime':
        opposing_engine= loads(user_data['the_rival'])
        opposing_engine.agent.load_weights(user_data['the_rival_weights']) 
        game_history = user_data['trainAI_games'][-1]
        moves = game_history['moves'][::-1]
        learner.train_mime(opposing_engine.agent, moves[1:], 500)
    else:
        # train the learning engine's agent
        learner.train_agent(learner.agent, n_iters, learner_name == 'the_rival')

    learner.env.reset()

    # dump the learnt weights to user data(mongo)
    user_data[learner_name + '_weights'] = learner.agent.save_weights()
    client.admin.users.update_one({ 'id': fbid }, { '$set': user_data })
    return True

def next_move(game_key, rival, delimiter=':', retry_limit=50):
    status = True
    
    #  get user's recent action and game turn from session data
    moves = r.lrange(game_key + delimiter + 'moves',0, -2)
    logger.info(moves, extra={ 'tags': ['dev_mssg:user_moves']})
    user_turn, user_action = moves[0].decode('utf-8').split(delimiter)

    #  get the current state of the game post user action
    print('\nUpdating game state by user action..')
    user_turn = user_turn[-1]
    state, _, _, _ = rival.env.step(int(action_ls.index(user_action)), int(user_turn))

    #  make agent choose an action
    print('\nUpdating game state by agent action...')
    turn = int(user_turn) + 1
    agent_action = rival.agent.select_action(state)
    next_state, _, _, _ = rival.env.step(agent_action[0, 0], turn)
    retries = 0

    #  repeat if chosen action is invalid
    # while np.array_equal(state.cpu().numpy(), next_state.cpu().numpy()):
    while torch.equal(state, next_state):
        print(next_state.cpu().numpy())
        print(state.cpu().numpy())
        print(torch.equal(state, next_state))
        print('\nUpdating game state by agent action (retry {})...'.format(retries))
        #  agent chooses randomly if too many invalid moves are chosen
        #  otherwise choose from learned weights
        agent_action = rival.agent.select_action(state, retries < retry_limit)
        # print(turn)
        next_state, _, done, _ = rival.env.step(agent_action[0,0], turn)
        retries += 1
        # break

    print(next_state.cpu().numpy())

    # moves.append()
    r.lpush(game_key + delimiter + 'moves', " ".join(map(str, ['Player'+str(turn), action_ls[agent_action[0, 0]] ])))

    return status 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--mode', default='train', help='mode to run the rival in')
    parser.add_argument('--nb_epochs', type=int, default=10, 
                            help='number of epochs to train agent for')

    args = parser.parse_args()
    
    #  pdb.set_trace()
    rival = init_learning_engine()
    next_move(rival, 'up', 1)
