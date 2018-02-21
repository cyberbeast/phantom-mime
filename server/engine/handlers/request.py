import hug, redis,os
from handlers.manager import next_move, init_game, init_learning_engine, launch_training
from pickle import loads, dumps
from pymongo import MongoClient
from multiprocessing import Process

import logging
logger = logging.getLogger(__name__)

client = MongoClient(os.environ['MONGO_HOST'])
r = redis.Redis(host='redis')

'''
    LOG FORMAT for docker debugging:
    logger.info(value, extra={ 'tags': ['debug_mssg_type:"debug_mssg"']} )
'''

@hug.get("/request")
def request(name="World"):
    return "Hello, {name}".format(name=name)

@hug.get("/nextMove")
def nextMove(key, mode):
    '''This API endpoint returns the next move for an AI agent based on the move made by a human player'''
    #  get learning engine from session(redis) data
    rival = loads(r.get(key + ':learning_engine'))

    try:
        response = next_move(key, rival)
        #  logger.info(response, extra={ 'tags': ['dev_mssg:SUCCESSFUL RESPONSE FROM REQUEST NEXT MOVE']})
    except Exception as e:
        logging.exception('UNSUCCESSFUL RESPONSE FROM REQUEST NEXT MOVE')

    #  r.set(key + ':learning_engine', dumps(rival))
    return response

@hug.get("/trainMime")
def trainMime(fbid):
    '''This API endpoint launches a training session for the learning engine responsible for profiling the user's gameplay'''
    learner_name = 'mime'
    init_learning_engine(fbid, None, learner_name) 
    p = Process(target=launch_training, args=(fbid, learner_name))
    p.start()
    return True

@hug.get("/initMime")
def initMime(key, fbid, mode):
    '''This API endpoint initializes the learning engine responsible for profiling the user's gameplay behaviour'''
    init_learning_engine_STATUS = init_learning_engine(fbid, key, mode)
    #  logger.info(init_learning_engine_STATUS, extra={ 'tags': ['dev_mssg:"init_learning_engine_STATUS :"']} )
    
    if init_learning_engine_STATUS:
        learner_name = 'the_rival' if mode == 'trainAI' else 'mime'
        user_data = client.admin.users.find_one({ 'id': fbid })
        rival = loads(user_data[learner_name])
        rival.agent.load_weights(user_data[learner_name + '_weights'])
        r.set(key + ':learning_engine', dumps(rival))
        return True
    else:
        return False


@hug.get("/gameInit")
def gameInit(key, fbid, gameMode="PvP" ):
    '''This API endpoint initializes a game board and other requisite components depending on the mode.
    Possible Modes are: "PvP", "PvAI", "trainAI"'''
    response = init_game(key)
    errorMessage = "gameInit Failure: {}"
    learner_name = 'the_rival' if gameMode == 'trainAI' else 'mime'

    if gameMode == 'trainAI':
        status, mssg = init_learning_engine(fbid, key, learner_name)
        if status:
            status, mssg = launch_training(fbid, learner_name)
            if status:
                # load learner from user data(mongo), load its learnt weights, 
                #  dump it in session data(redis)
                user_data = client.admin.users.find_one({ 'id': fbid })
                rival = loads(user_data[learner_name])
                rival.agent.load_weights(user_data[learner_name + '_weights'])
                r.set(key + ':learning_engine', dumps(rival))
            else:
                return errorMessage.format(mssg) 
        else:
            return errorMessage.format(mssg) 

    return response
