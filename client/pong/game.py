import aiohttp, os, pdb

async def propagate_keypress(ws, keypress_event, player_idx):
    keypress_data = {
        'event_type': keypress_event.type,
        'event_key': keypress_event.key,
        'player_idx': player_idx
    }
    await ws.send_str(json.dumps(keypress_data))

def on_keypress_notification(keypress_data, decision_engine):
    #  assuming response was received properly
    decision_engine.handle_keypress(**keypress_data)

async def init_game(ws):
    await ws.send_str('c_init')

class Pong:
    def __init__(self, server_endpoint):
        self.server_endpoint = server_endpoint
        self.decision_engine = Decision_Engine()
        self.rendering_engine = RenderingEngine()

    async def start_game_session(self, channel_name):
        session = aiohttp.ClientSession() #  create session for game
        channel_uri = os.path.join(self.server_endpoint, channel_name)

        #  connect to pvp game channel
        with session.ws_connect(channel_uri) as ws:

            #  send init_game signal and then iterate over socket messages
            await init_game(ws)
            async for mssg in ws:

                #  unpack socket message
                mssg_tag, mssg_payload = mssg.json().items()
                if mssg_tag == 'ws_start_game':
                    #  unpack message payload
                    rendering_meta, decision_meta = mssg_payload.items()
                    decision_meta['rendering_meta'] = rendering_meta
                    decision_meta['ws'] = ws

                    self.decision_engine.init_game(**decision_meta)
                    await decision_engine.start_game()
                    
                elif mssg_tag == 'ws_keypress_notify':
                    on_keypress_notification(mssg_payload, self.decision_engine)

                elif mssg_tag in ('channel_closed', 'error in the channel'):
                    print('Failed to start game!')
                    break
