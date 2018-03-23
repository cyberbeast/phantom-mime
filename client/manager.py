import os, sys, pdb
#  sys.path.insert(0, os.environ['PROJECT_PATH'])

import asyncio
from socketIO_client import SocketIO, BaseNamespace

from pong.game import Pong
#  from pong.rendering_engine import RenderingEngine
#  from pong.decision_engine import DecisionEngine

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

async def run_game_on_server(server_uri, port):
    sio_client = SocketIO(server_uri, port)
    pvp_channel = sio_client.define(BaseNamespace, '/pvp')

    pong_client = Pong(pvp_channel)

    #  register listeners
    pvp_channel.on('ws_game_init_resp', pong_client.on_setup_game)
    pvp_channel.on('ws_game_start', pong_client.on_start_game)
    pvp_channel.on('ws_keypress_notify', pong_client.on_keypress_notify)

    pvp_channel.emit('c_game_init')
    sio_client.wait()

if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(run_game_on_server('0.0.0.0', '8080'))
    #  run_game_locally()
