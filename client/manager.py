import os, sys, pdb
sys.path.insert(0, os.environ['PROJECT_PATH'])

from pong.game import Pong
#  from pong.rendering_engine import RenderingEngine
from pong.decision_engine import DecisionEngine

def run_game_locally():
    rendering_meta = { 
        'screen_width': 600, 
        'screen_height': 400,
        'ball_radius': 20,
        'pad_width': 8,
        'pad_height': 80
    }
    decision_meta = {
        'paddle_vel_incr': 8,
        'fps': 60,
        'player_idx': 0,
        'rendering_meta': rendering_meta
    }
    
    decision_engine = DecisionEngine()

    decision_engine.init_game(**decision_meta)
    decision_engine.start_game()

def run_game_on_server(server_uri, channel_name):
    pong_client = Pong(server_uri)

    event_loop = asyncio.get_event_loop()
    loop.run_until_complete(pong_client.start_game_session(channel_name))

if __name__ == '__main__':
    run_game_locally()
    #  run_game_on_server('', '') 
