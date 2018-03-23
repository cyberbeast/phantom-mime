import aiohttp, os, pdb

from .rendering_engine import RenderingEngine
from .decision_engine import DecisionEngine

class Pong:
    def __init__(self, socket):
        self.decision_engine = DecisionEngine(socket)
        self.rendering_engine = RenderingEngine()

    def on_setup_game(self, *args):
        print('\nSetting up the game. Please wait..')
        game_meta = args[0]['game_meta']
        self.decision_engine.init_game(**game_meta)

    def on_start_game(self, *args):
        print('\nStarting Game..')
        self.decision_engine.start_game()

    def on_keypress_notification(self, *args):
        print('Keypress data: {}, received'.format(args['keypress_data']))
        keypress_data = args['keypress_data']
        self.decision_engine.handle_keypress(**keypress_data)
