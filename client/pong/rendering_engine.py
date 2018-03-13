import random, pygame, sys, pdb
from pygame import *

WHITE = (255, 255, 255)
ORANGE = (255,140,0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

class RenderingEngine:
    def __init__(self, screen_width, screen_height, ball_radius, pad_width, pad_height):
        self.screen_dims = ( screen_width, screen_height )
        self.ball_radius = ball_radius
        self.paddle_dims = ( pad_width, pad_height )
        self.ball_pos = [ 0, 0 ]
        self.ball_vel = [ 0, 0 ]
        self.paddle_X_pos = ( (pad_width // 2) - 1, screen_width + 1 - pad_width // 2 )
        self.paddle_Y_pos = [ screen_height // 2, screen_height // 2 ]
        self.paddle_velocities = [ 0, 0 ]
        self.scores = [ 0 , 0 ]

        pygame.init()
        fps = pygame.time.Clock()

        self.window = pygame.display.set_mode((screen_width, screen_height), 0, 32)
        pygame.display.set_caption('Daylight Pong')

    def __draw_canvas(self, canvas):
        canvas.fill(BLACK)
        screen_width, screen_height = self.screen_dims
        pad_width, pad_height = self.paddle_dims

        #  draw the board boundaries and middle line
        pygame.draw.line(canvas, WHITE, [screen_width // 2, 0], [screen_width // 2, screen_height], 1)
        pygame.draw.line(canvas, WHITE, [pad_width, 0], [pad_width, screen_height], 1)
        pygame.draw.line(canvas, WHITE, [screen_width - pad_width, 0], [screen_width - pad_width, screen_height], 1)
        pygame.draw.circle(canvas, WHITE, [screen_width // 2, screen_height // 2], 70, 1)

        #  repaint the game entities
        paddle_edge_pts = [ calc_edge_pts(x, y, self.paddle_dims) \
                            for x, y in zip(self.paddle_X_pos, self.paddle_Y_pos) ]
        pygame.draw.polygon(canvas, GREEN, paddle_edge_pts[0], 0)
        pygame.draw.polygon(canvas, GREEN, paddle_edge_pts[1], 0)

        pygame.draw.circle(canvas, ORANGE, self.ball_pos, 20, 0)

        #  repaint score texts
        myfont1 = pygame.font.SysFont("Comic Sans MS", 20)
        label1 = myfont1.render("Score " + str(self.scores[0]), 1, (255, 255, 0))
        canvas.blit(label1, (50, 20))

        myfont2 = pygame.font.SysFont("Comic Sans MS", 20)
        label2 = myfont2.render("Score " + str(self.scores[1]), 1, (255, 255, 0))
        canvas.blit(label2, (470, 20))

        #  END OF RENDERING SECTION

        #  update the paddle positions based on the current velocity
        paddle_Y_pos_vel = zip(self.paddle_Y_pos, self.paddle_velocities) 
        paddle_Y_range = [ pad_height // 2, screen_height - (pad_height // 2) ]
        self.paddle_Y_pos = [ (pos + vel) if paddle_Y_range[0] <= pos + vel <= paddle_Y_range[1] \
                                else pos for pos, vel in paddle_Y_pos_vel ]

        #  update the ball position based on its velocity and current positions
        self.ball_pos = [ pos + int(vel) for pos, vel in zip(self.ball_pos, self.ball_vel) ]

        #  ball trajectory reflection on hitting board edge  
        vert_ball_range = [ self.ball_radius, screen_height - self.ball_radius ]

        if not vert_ball_range[0] < self.ball_pos[1] < vert_ball_range[1]:
            self.ball_vel[1] = -self.ball_vel[1]

        #  handle ball trajectory on the x-axis
        hor_ball_range = [ pad_width + self.ball_radius, \
                            screen_width - self.ball_radius - pad_width ]
        paddle_ranges = [ (y_pos - pad_height, y_pos + pad_height) \
                                for y_pos in self.paddle_Y_pos ]

        #  check if ball is outside pong table limits
        if not hor_ball_range[0] < self.ball_pos[0] < hor_ball_range[1] - 1:
            #  check which half of the table the ball is in
            curr_turn = self.ball_pos[0] > (screen_width // 2)
            curr_paddle_range = paddle_ranges[ int(curr_turn) ]
            
            #  check if ball hit paddle otherwise reset ball position and update scores
            if curr_paddle_range[0] <= self.ball_pos[1] <= curr_paddle_range[1]:
                self.ball_vel = [ -1.1 * self.ball_vel[0], self.ball_vel[1] ]
            else:
                self.scores[ int(not curr_turn) ] += 1
                self.__init_ball_move(not curr_turn)
