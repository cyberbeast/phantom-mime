import socketio

num_players = 0
game_meta = {
    'paddle_vel_incr': 8,
    'fps': 6,
    'rendering_meta': {  
        'screen_width': 600, 
        'screen_height': 400,
        'ball_radius': 20,
        'pad_width': 8,
        'pad_height': 80
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
        game_meta['player_idx'] = num_players % 2 
        print('Game meta for player {} is {}'.format(game_meta['player_idx'], game_meta))

        num_players += 1

        await self.emit('ws_game_init_resp', {'game_meta': game_meta}, room=sid) 

        if num_players >= 2:
            print('Ready players One!')
            await self.emit('ws_game_start')

    async def on_c_keypress_propagate(self, sid, environ):
        print('Received a keypress: {} notif from {}'.format(environ, sid))
        await self.emit('ws_keypress_notify')
