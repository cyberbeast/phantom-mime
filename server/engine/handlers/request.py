import hug, redis,os
from handlers.manager import next_move, init_game, init_learning_engine, launch_training
from pickle import loads, dumps
from pymongo import MongoClient
from multiprocessing import Process

import logging
logger = logging.getLogger(__name__)

client = MongoClient(os.environ['MONGO_HOST'])
r = redis.Redis(host='redis')

@hug.get("/request")
def request(name:str="World"):
    return "Hello, {name}".format(name=name)

@hug.get("/nextMove")
def nextMove(key, mode):
    '''This API returns the next move for an AI agent based on the move made by a human player'''
    #  get learning engine from session(redis) data
    rival = loads(r.get(key + ':learning_engine'))
    try:
        response = next_move(key, rival)
        logger.info(response, extra={ 'tags': ['dev_mssg:SUCCESSFUL RESPONSE FROM REQUEST NEXT MOVE']})
    except Exception as e:
        logging.exception('UNSUCCESSFUL RESPONSE FROM REQUEST NEXT MOVE')
    r.set(key + ':learning_engine', dumps(rival))
    return response

@hug.get("/trainMime")
def trainMime(fbid):
    learner_name = 'mime'
    init_learning_engine(fbid, None, "trainMime")
    p = Process(target=launch_training, args=(fbid, learner_name))
    p.start()
    return True


@hug.get("/gameInit")
def gameInit(key, fbid, gameMode="PvP" ):
    logger.info("Reaching here")
    '''Possible Modes are: "PvP", "PvAI", "trainAI"'''
    response = init_game(key)
    errorMessage = "gameInit Failure: "
    
    if gameMode == 'trainAI':
        init_learning_engine_STATUS = init_learning_engine(fbid, key, gameMode)
        logger.info(init_learning_engine_STATUS, extra={ 'tags': ['dev_mssg:"init_learning_engine_STATUS :"']} )
        if init_learning_engine_STATUS:
            learner_name = 'the_rival' if gameMode == 'trainAI' else 'mime'
            try:
                launch_training_STATUS = launch_training(fbid, learner_name)
                if not launch_training_STATUS:
                    return errorMessage + "launch_training failure!!!"
                else:
                    # load learner from user data(mongo), load its learnt weights, dump it in session data(redis)
                    user_data = client.admin.users.find_one({ 'id': fbid })
                    rival = loads(user_data[learner_name])
                    rival.agent.load_weights(user_data[learner_name + '_weights'])
                    r.set(key + ':learning_engine', dumps(rival))
                logger.info(launch_training_STATUS, extra={ 'tags': ['dev_mssg:launch_training_STATUS']} )
            except Exception as e:
                logging.exception('LAUNCHING TRAINING BROKE!')
            
        else:
            return errorMessage + "init_learning engine failure!!!"

    return response