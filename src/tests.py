import unittest
from state import State
from game_without_ui import GameNoUI
import random
import numpy as np
player_random = 'RANDOM'
player_mcts = 'MCTS'
player_swarm = 'SWARM'


def test_pso(vicinities, vicin_radius=3, num_games=1000):
    if vicinities:
        print(f'\nTesting swarming with Local Vicinity Best PSO...\nVicinity Radius = {vicin_radius}\n{num_games} Games')
    else:
        print(f'\nTesting swarming with Global Best PSO...\n{num_games} Games')
    rand_moves = 20
    w_wins, w_turns, b_wins, b_turns = 0, 0, 0, 0
    for i in range(1, num_games+1):
        if i % 200 == 0:
            print(f'{i} games simulated...')
        g = State(time_limit=None, iter_limit=100)
        np.random.seed(i)
        random.seed(i)
        game = GameNoUI(state=g,
                        player1=player_swarm, player2=player_random,
                        generate_full_board=True,
                        random_moves_after_generate=rand_moves,
                        vicinities=vicinities,
                        vicin_radius=vicin_radius,
                        full_swarm_move=True)
        winner = game.play_full_game()
        if winner == -1:
            if game.state.turn_count_white > (11 + rand_moves):
                # Accounting for random moves
                w_wins += 1
                w_turns += (game.state.turn_count_white - 11 - rand_moves)
        elif winner == 1:
            if game.state.turn_count_black > (11 + rand_moves):
                b_wins += 1
                b_turns += (game.state.turn_count_black - 11 - rand_moves)
    print(f'White won {w_wins} times with avg plies of {round(w_turns / w_wins)}')
    try:
        print(f'Black won {b_wins} times with plies of {round(b_turns / b_wins)}')
    except:
        print(f'Black won 0 times')


def test_comms(folder, intention_criteria, full_swarm, inf_moves, num_games, player1, player2):
    rand_moves = 20
    w_wins, w_turns, b_wins, b_turns = 0, 0, 0, 0
    print(f'{num_games} Games')
    for i in range(1, num_games+1):
        if i % 200 == 0:
            print(f'{i} games simulated...')
        g = State(time_limit=None, iter_limit=500)
        game = GameNoUI(state=g,
                        player1=player1, player2=player2,
                        generate_full_board=True,
                        random_moves_after_generate=rand_moves,
                        vicinities=True,
                        vicin_radius=3,
                        intention_criteria=intention_criteria,
                        full_swarm_move=full_swarm,
                        infinite_moves=inf_moves,
                        log_file=f'{folder}{i+40}_{player1}_{player2}_{intention_criteria}.txt')
        winner = game.play_full_game()
        if winner == -1:
            if game.state.turn_count_white > (11 + rand_moves):
                # Accounting for random moves
                print('White win')
                w_wins += 1
                w_turns += (game.state.turn_count_white - 11 - rand_moves)
        elif winner == 1:
            if game.state.turn_count_black > (11 + rand_moves):
                print('Black win')
                b_wins += 1
                b_turns += (game.state.turn_count_black - 11 - rand_moves)
        else:
            print('Draw')
    try:
        print(f'White won {w_wins} times with avg plies of {round(w_turns / w_wins)}')
    except:
        print(f'White won 0 times')
    try:
        print(f'Black won {b_wins} times with plies of {round(b_turns / b_wins)}')
    except:
        print(f'Black won 0 times')


class SwarmingTest(unittest.TestCase):

    # def test_global_pso(self):
    #     test_pso(vicinities=False)
    #
    # def test_vicinities_pos1(self):
    #     test_pso(vicinities=True, vicin_radius=1)
    #
    # def test_vicinities_pos2(self):
    #     test_pso(vicinities=True, vicin_radius=2)
    #
    # def test_vicinities_pso3(self):
    #     test_pso(vicinities=True, vicin_radius=3)
    #
    # def test_swarm0_vel(self):
    #     print('\nTesting velocity with DT')
    #     test_comms(folder='logs/velocity/', intention_criteria=0, full_swarm=False, inf_moves=True, num_games=100,
    #                player1=player_swarm, player2=player_random)
    #
    # def test_swarm1_acc(self):
    #     print('\nTesting accuracy with DT')
    #     test_comms(folder='logs/accuracy/', intention_criteria=1, full_swarm=False, inf_moves=True, num_games=100,
    #                player1=player_swarm, player2=player_random)
    #
    # def test_swarm2_fitness(self):
    #     print('\nTesting fitness with DT')
    #     test_comms(folder='logs/fitness/', intention_criteria=2, full_swarm=False, inf_moves=True, num_games=100,
    #                player1=player_swarm, player2=player_random)

    # def test_swarm3_vel_and_acc(self):
    #     print('\nTesting velocity + accuracy with DT')
    #     test_comms(folder='logs/vel_and_acc/', intention_criteria=3, full_swarm=False, inf_moves=True, num_games=100,
    #                player1=player_swarm, player2=player_random)
    # def test_swarm4_vel_or_acc(self):
    #     print('\nTesting velocity or accuracy with DT')
    #     test_comms(folder='logs/vel_or_acc/', intention_criteria=4, full_swarm=False, inf_moves=True, num_games=100,
    #                player1=player_swarm, player2=player_random)
    # def test_swarm4_vel_or_acc(self):
    #     print('\nTesting velocity or accuracy with DT')
    #     test_comms(folder='logs/vel_or_acc/', intention_criteria=4, full_swarm=False, inf_moves=True, num_games=100,
    #                player1=player_swarm, player2=player_random)
    #
    # def test_swarm5_vel_or_dgt(self):
    #     print('\nTesting velocity or DGT with DT')
    #     test_comms(folder='logs/vel_or_dgt/', intention_criteria=5, full_swarm=False, inf_moves=True, num_games=100,
    #                player1=player_swarm, player2=player_random)

    def test_swarm_vs_mcts(self):
        print('\nTesting Swarm vs MCTS')
        test_comms(folder='logs/swarm_vs_mcts/', intention_criteria=5, full_swarm=False, inf_moves=False, num_games=100,
                   player1=player_swarm, player2=player_mcts)


if __name__ == '__main__':
    unittest.main()
