import numpy as np, pdb

def move_up(x, y): return  x, y - 1 
def move_down(x, y): return  x, y + 1
def move_left(x, y): return x - 1, y
def move_right(x, y): return x + 1, y

def _init_action_set():
    
    move_up_fn, move_down_fn = move_up, move_down
    move_left_fn, move_right_fn = move_left, move_right

    return [ move_up_fn, move_down_fn, move_left_fn, move_right_fn ]

class BasicGame:
    def __init__(self):
        self.action_set = _init_action_set()

    def is_game_finished(self, grid):
        _, _, height, width = grid.size()
        return grid.cpu().numpy()[:, : 0, height - 1] == 2 \
                or grid.cpu().numpy()[:, :, width-1, 0] == 1 

    def calc_reward(self, state, next_state):
        if self.is_game_finished(next_state):
            return 0
        elif np.array_equal(state.cpu().numpy(), next_state.cpu().numpy()):
            return -3
        else:            
            return -1
        

    def process_action(self, grid, action, turn):
        _, _, height, width = grid.size()
        state = grid.cpu().numpy()

        #  determine the new position of player based on turn and action
        _, _, y_old, x_old = np.where( state ==  turn )
        x_new, y_new = self.action_set[action](x_old, y_old)
        # print(x_old, y_old)
        # print('inside game logic')
        # print(turn, x_new, y_new)
        # print(grid)


        #  make sure the new position is valid (wrt game rules)
        if not (0 <= x_new < width and 0 <= y_new < height):
            return grid
        if grid.cpu().numpy()[:, :, y_new, x_new] != 0:
            return grid

        #  update the grid with the player's new position
        grid[:, :, y_old, x_old] = 0
        grid[:, :, y_new, x_new] = turn 
        # print(grid)
        return grid
