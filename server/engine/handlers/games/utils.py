import numpy as np, pdb

def is_game_finished(grid):
    _, _, height, width = grid.size()
    return grid.numpy()[:, : 0, height - 1] == 2 or grid.numpy()[:, :, width-1, 0] == 1 

def calc_reward(grid):
    return 0

def _init_action_set():
    move_up = lambda x, y: ( x, y - 1 )
    move_down = lambda x, y: ( x, y + 1 )
    move_left = lambda x, y: ( x - 1, y )
    move_right = lambda x, y: ( x + 1, y )
    
    return [ move_up, move_down, move_left, move_right ]

def process_action(grid, action, turn):
    _, _, height, width = grid.size()
    action_set = _init_action_set()

    state = grid.numpy()

    #  determine the new position of player based on turn and action
    _, _, y_old, x_old = np.where( state == ( turn + 1 ) )
    x_new, y_new = action_set[action](x_old, y_old)

    #  make sure the new position is valid (wrt game rules)
    assert 0 <= x_new < width and 0 <= y_new < height,\
        '\nAction puts player outside bounds of grid'
    assert grid.numpy()[:, :, y_new, x_new] == 0, \
        '\nAction puts player on obstacle or other player'

    #  update the grid with the player's new position
    grid[:, :, x_new, y_new] = turn + 1
    return grid
