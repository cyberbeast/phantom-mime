import hug
from handlers.manager import next_move, init_game, init_learning_engine
import logging
import redis

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
r = redis.Redis(host='redis')
@hug.get("/request")
def request(name:str="World"):
    return "Hello, {name}".format(name=name)

@hug.get("/nextmove")
def nextmove():
    '''This API returns the next move for an AI agent based on the move made by a human player'''
    return 'nextMove'

@hug.get("/gameInit")
def gameInit(key):
    # print("KEY IS: " + key)
    response = init_game(key)
    # print("\n\n\nBELOW THIS...")
    # print(response)
    return response