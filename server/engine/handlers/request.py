import hug
from handlers.manager import next_move, init_learning_engine

@hug.get("/request")
def request(name:str="World"):
    return "Hello, {name}".format(name=name)

@hug.get("/nextmove")
def nextmove():
    '''This API returns the next move for an AI agent based on the move made by a human player'''
    return ping()
