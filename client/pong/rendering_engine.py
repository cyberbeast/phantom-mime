import pygame, pdb

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
