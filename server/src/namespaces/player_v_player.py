import socketio

num_players = 0
game_meta = {
    'decision_meta': {
        'paddle_vel_incr': 8,
        'fps': 60,
        'player_idx': 0,
        'rendering_meta': {  
            'screen_width': 600, 
            'screen_height': 400,
            'ball_radius': 20,
            'pad_width': 8,
            'pad_height': 80
        }
    }
}

class PVPNamespace(socketio.AsyncNamespace):
    def on_connect(self, sid, environ):
        print('{} connected'.format(sid))

    def on_disconnect(self, sid):
        print('{} disconnected'.format(sid))

    async def on_c_game_init(self, sid):
        global num_players

        print('\n{} is requesting to play'.format(sid))
        num_players += 1
        print('\n{} users requesting to play'.format(num_players))

        await self.emit('ws_game_init_resp', game_meta, skip_sid=sid) 

        if num_players >= 2:
            print('Ready players One!')
            await self.emit('ws_game_start')

    async def on_c_keypress_propagate(self, sid, environ):
        print("{} pressed key {}".format(sid, environ['key']))
        await self.emit('ws_keypress_notify', environ, skip_sid=sid)
