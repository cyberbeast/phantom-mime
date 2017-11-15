import os, sys, argparse, pdb
sys.path.insert(0, os.environ['DQN_ROOT'])

import numpy as np

from learner.learning_engine import LearningEngine

def generate_obstacles(x_max, y_max, obstacles_lim):
    np.random.seed(int(os.environ['RANDOM_SEED']))
    num_obstacles = np.random.randint(obstacles_lim)
    obstacle_x = np.random.randint(x_max, size=num_obstacles-1) 
    obstacle_y = np.random.randint(y_max, size=num_obstacles-1) 
    obstacles = set([ (i, j) for i, j in zip(obstacle_x, obstacle_y) ])
    return list(obstacles)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--width', type=int, help='width of game board')
    parser.add_argument('--height', type=int, help='height of game board')
    parser.add_argument('--model', default='qnet', help='type of model to use in learning')
    parser.add_argument('--nb_epochs', type=int, default=10, 
                            help='number of epochs to train agent for')

    args = parser.parse_args()
    
    #  randomly generate obstacles ( upto square root of number of cells )
    obstacles = generate_obstacles(args.width-1, args.height-1, 
                                    ( args.width * args.height ) // 2)

    learner = LearningEngine(args.model)
    learner.init_game(args.width, args.height, obstacles)
    learner.train_agent(args.nb_epochs)
