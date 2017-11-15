def is_game_finished(grid):
    _, _, height, width = grid.size()
    return grid[:, : 0, height - 1] == 2 or grid[:, :, width-1, 0] == 1 

def calc_reward(grid):
    return 0

def process_action(grid, turn, action):
    _, _, height, width = grid.size()
    state = grid.data.numpy()
    _, _, y_old, x_old = np.where(state == turn)
    y_new, x_new = y_old[0], x_old[0]
    if action == 'up':
        y_new = y_new - 1 
    elif action == 'down':
        y_new = y_new + 1 
    elif action == 'left':
        x_new = x_new - 1 
    elif action == 'right':
        x_new = x_new + 1 
    assert 0 <= x_new < width and 0 <= y_new < height,\
        '\nAction puts player outside bounds of grid'
    assert grid[:, :, y_new, x_new] == 0, \
        '\nAction puts player on obstacle or other player'
    grid[:, :, x_new, y_new] = turn
    return grid
