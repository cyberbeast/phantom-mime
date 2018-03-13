import pygame, sys, aiohttp, os, pdb
from pygame import *

WHITE = (255, 255, 255)
ORANGE = (255,140,0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

def calc_edge_pts(x, y, paddle_dims):
    paddle_width, paddle_height = paddle_dims
    return [ 
        (x - paddle_width // 2, y - paddle_height // 2),
        (x - paddle_width // 2, y + paddle_height // 2),
        (x + paddle_width // 2, y + paddle_height // 2),
        (x + paddle_width // 2, y - paddle_height // 2),
    ]

def propagate_keypress(ws, keypress_event, player_idx):
    keypress_data = {
        'event_type': keypress_event.type,
        'event_key': keypress_event.key,
        'player_idx': player_idx
    }
    await ws.send_str(json.dumps(keypress_data))

def on_keypress_notification(ws, decision_engine):
    #  assuming response was received properly
    keypress_resp = await ws.receive()
    keypress_data = keypress_resp.json()
    decision_engine.handle_keypress(**keypress_data)

async def init_game(ws):
    await ws.send_str('c_init')
    channel_resp = await ws.receive()
    if channel_resp.type == aiohttp.WSMsgType.TEXT:
        return channel_resp.json()
    elif channel_resp.type == aiohttp.WSMsgType.CLOSED:
        return 'channel closed' 
    elif channel_resp.type == aiohttp.WSMsgType.ERROR:
        return 'error in the channel'

class RenderingEngine:
    def __init__(self):
        self.ball_pos = [ 0, 0 ]
        self.ball_vel = [ 0, 0 ]
        self.paddle_velocities = [ 0, 0 ]
        self.scores = [ 0 , 0 ]

    def init_game(self, screen_width, screen_height, ball_radius, pad_width, pad_height):
        self.screen_dims = ( screen_width, screen_height )
        self.ball_radius = ball_radius
        self.paddle_dims = ( pad_width, pad_height )

        self.paddle_X_pos = ( (pad_width // 2) - 1, screen_width + 1 - pad_width // 2 )
        self.paddle_Y_pos = [ screen_height // 2, screen_height // 2 ]

        pygame.init()
        pygame.display.set_caption('Daylight Pong')

        self.canvas= pygame.display.set_mode((screen_width, screen_height), 0, 32)
        self.clock = pygame.time.Clock()

    def draw_canvas(self):
        self.canvas.fill(BLACK)
        screen_width, screen_height = self.screen_dims
        pad_width, pad_height = self.paddle_dims

        #  draw the board boundaries and middle line
        pygame.draw.line(self.canvas, WHITE, [screen_width // 2, 0], [screen_width // 2, screen_height], 1)
        pygame.draw.line(self.canvas, WHITE, [pad_width, 0], [pad_width, screen_height], 1)
        pygame.draw.line(self.canvas, WHITE, [screen_width - pad_width, 0], [screen_width - pad_width, screen_height], 1)
        pygame.draw.circle(self.canvas, WHITE, [screen_width // 2, screen_height // 2], 70, 1)

        #  repaint the game entities
        paddle_edge_pts = [ calc_edge_pts(x, y, self.paddle_dims) \
                            for x, y in zip(self.paddle_X_pos, self.paddle_Y_pos) ]
        pygame.draw.polygon(self.canvas, GREEN, paddle_edge_pts[0], 0)
        pygame.draw.polygon(self.canvas, GREEN, paddle_edge_pts[1], 0)

        pygame.draw.circle(self.canvas, ORANGE, self.ball_pos, 20, 0)

        #  repaint score texts
        myfont1 = pygame.font.SysFont("Comic Sans MS", 20)
        label1 = myfont1.render("Score " + str(self.scores[0]), 1, (255, 255, 0))
        self.canvas.blit(label1, (50, 20))

        myfont2 = pygame.font.SysFont("Comic Sans MS", 20)
        label2 = myfont2.render("Score " + str(self.scores[1]), 1, (255, 255, 0))
        self.canvas.blit(label2, (470, 20))

class DecisionEngine:    
    def __init__(self):
        self.rendering_engine = RenderingEngine()

    def init_game(self, paddle_vel_incr, fps, player_idx, rendering_meta, ws=None):
        self.paddle_vel_incr = paddle_vel_incr
        self.fps = fps
        self.player_idx = player_idx
        self.rendering_engine.init_game(**rendering_meta)
        self.websocket = ws

    def handle_keypress(self, event_type, event_key, player_idx):
        vel_dir = 0 if event_type == KEYUP else -1 if event_key == K_UP else 1
        paddle_incr = self.paddle_vel_incr * vel_dir
        self.rendering_engine.paddle_velocities[player_idx] = paddle_incr

    def reset_ball_pos(self, move_right):
        screen_width, screen_height = self.rendering_engine.screen_dims
        self.rendering_engine.ball_pos = [ screen_width // 2, screen_height // 2 ]
        self.rendering_engine.ball_vel = [ 2 if move_right else -2, -2 ]

    def update_game_entities(self):
        screen_width, screen_height = self.rendering_engine.screen_dims
        pad_width, pad_height = self.rendering_engine.paddle_dims
        paddle_velocities, paddle_Y_pos = self.rendering_engine.paddle_velocities, \
                                            self.rendering_engine.paddle_Y_pos
        ball_pos, ball_vel = self.rendering_engine.ball_pos, \
                                self.rendering_engine.ball_vel
        ball_radius = self.rendering_engine.ball_radius
        scores = self.rendering_engine.scores

        #  update the paddle positions based on the current velocity
        paddle_Y_pos_vel = zip(paddle_Y_pos, paddle_velocities) 
        paddle_Y_range = [ pad_height // 2, screen_height - (pad_height // 2) ]
        paddle_Y_pos = [ (pos + vel) if paddle_Y_range[0] <= pos + vel <= paddle_Y_range[1] \
                                else pos for pos, vel in paddle_Y_pos_vel ]

        #  update the ball position based on its velocity and current positions
        ball_pos = [ pos + int(vel) for pos, vel in zip(ball_pos, ball_vel) ]

        #  ball trajectory reflection on hitting board edge  
        vert_ball_range = [ ball_radius, screen_height - ball_radius ]

        if not vert_ball_range[0] < ball_pos[1] < vert_ball_range[1]:
            ball_vel[1] = -ball_vel[1]

        #  handle ball trajectory on the x-axis
        hor_ball_range = [ pad_width + ball_radius, screen_width - ball_radius - pad_width ]
        paddle_ranges = [ (y_pos - pad_height, y_pos + pad_height) for y_pos in paddle_Y_pos ]

        #  check if ball is outside pong table limits
        if not hor_ball_range[0] < ball_pos[0] < hor_ball_range[1] - 1:
            #  check which half of the table the ball is in
            table_side = ball_pos[0] > (screen_width // 2)
            curr_paddle_range = paddle_ranges[ int(table_side) ]
            
            #  check if ball hit paddle otherwise reset ball position and update scores
            if curr_paddle_range[0] <= ball_pos[1] <= curr_paddle_range[1]:
                ball_vel = [ -1.1 * ball_vel[0], ball_vel[1] ]
            else:
                scores[ int(not table_side) ] += 1
                self.reset_ball_pos(not table_side)

                #  hack to make sure the ball reset code does not get overwritten by code below
                ball_pos = self.rendering_engine.ball_pos
                ball_vel = self.rendering_engine.ball_vel

        self.rendering_engine.ball_pos = ball_pos
        self.rendering_engine.ball_vel = ball_vel
        self.rendering_engine.paddle_Y_pos = paddle_Y_pos
        self.rendering_engine.scores = scores

    def start_game(self):
        coin_toss = True # TODO: randomize it

        self.reset_ball_pos(coin_toss)
        while True:
            self.rendering_engine.draw_canvas()
        
            #  listen for keypress on websocket channel
            await on_keypress_notification(self.ws)

            #  listen for local keypress events
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type in ( KEYDOWN, KEYUP ):
                    self.handle_keypress(event.type, event.key, self.player_idx)
                    propagate_keypress(self.ws, event, self.player_idx)

            self.update_game_entities()

            pygame.display.update()
            self.rendering_engine.clock.tick(self.fps)

class Pong:
    def __init__(self, server_endpoint):
        self.server_endpoint = server_endpoint
        self.decision_engine = Decision_Engine()
        self.rendering_engine = RenderingEngine()

    def start_game_session(self, channel_name):
        session = aiohttp.ClientSession() #  create session for game
        channel_uri = os.path.join(self.server_endpoint, channel_name)

        #  connect to pvp game channel
        with session.ws_connect(channel_uri) as ws:
            init_resp = init_game(ws)
            if init_resp not in ('channel_closed', 'error in the channel'):
                rendering_meta, decision_meta = init_resp.items()
                self.decision_engine.init_game(**decision_meta)
                decision_engine.start_game()
            else:
                print('Failed to start game!')
            
if __name__ == '__main__':
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
    
    rendering_engine = RenderingEngine()
    decision_engine = DecisionEngine()

    decision_engine.init_game(**decision_meta)
    decision_engine.start_game()
