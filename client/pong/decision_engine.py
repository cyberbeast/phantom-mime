import random, pygame, sys, pdb
from pygame import *

from .rendering_engine import RenderingEngine

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

    async def start_game(self):
        coin_toss = True # TODO: randomize it

        self.reset_ball_pos(coin_toss)
        while True:
            self.rendering_engine.draw_canvas()
        
            #  listen for local keypress events
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type in ( KEYDOWN, KEYUP ):
                    self.handle_keypress(event.type, event.key, self.player_idx)
                    await propagate_keypress(self.ws, event, self.player_idx)

            self.update_game_entities()

            pygame.display.update()
            self.rendering_engine.clock.tick(self.fps)
