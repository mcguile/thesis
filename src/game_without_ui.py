from game import *
from mcts import MCTS
from state import State
import ray

ray.init()

player_random = 'RANDOM'
player_mcts = 'MCTS'
player_swarm = 'SWARM'


def play_full_game(game, player1, player2):
    make_first_move_each(game.state)
    mcts_ = MCTS(time_limit=game.time_limit, iter_limit=game.iter_limit)
    while not isGameOver(game.state):
        if game.state.players_turn == -1:
            if player1 == player_random:
                make_random_move_from_anywhere(game.state)
            elif player1 == player_mcts:
                action = mcts_.multiprocess_search(game.state)
                make_mcts_move(game.state, action)
            else:
                pass
        elif game.state.players_turn == 1:
            if player2 == player_random:
                make_random_move_from_anywhere(game.state)
            elif player2 == player_mcts:
                action = mcts_.multiprocess_search(game.state)
                make_mcts_move(game.state, action)
            else:
                pass
    if has_won(game.state, -1):
        print(f"White wins after {game.state.turn_count_white} turns")
    else:
        print(f"Black wins after {game.state.turn_count_black} turns")


g = State(time_limit=None, iter_limit=100)
play_full_game(g, player1=player_random, player2=player_random)