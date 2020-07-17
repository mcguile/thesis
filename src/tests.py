import unittest
from game import *
from state import State
from game_without_ui import GameNoUI
player_random = 'RANDOM'
player_mcts = 'MCTS'
player_swarm = 'SWARM'


def test_pso(vicinities, vicin_radius=3):
    if vicinities:
        print(f'\nTesting swarming with Local Vicinity Best PSO...\nVicinity Radius = {vicin_radius}')
    else:
        print(f'\nTesting swarming with Global Best PSO...')
    rand_moves = 20
    w_wins, w_turns, b_wins, b_turns = 0, 0, 0, 0
    for i in range(1, 1001):
        if i % 200 == 0:
            print(f'{i} games simulated...')
        g = State(time_limit=None, iter_limit=100)
        game = GameNoUI(state=g,
                        player1=player_swarm, player2=player_random,
                        generate_full_board=True,
                        seed=i,
                        random_moves_after_generate=rand_moves,
                        vicinities=vicinities,
                        vicin_radius=vicin_radius)
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



class SwarmingTest(unittest.TestCase):

    def test_global_pso(self):
        test_pso(vicinities=False)

    def test_vicinities_pos1(self):
        test_pso(vicinities=True, vicin_radius=1)

    def test_vicinities_pos2(self):
        test_pso(vicinities=True, vicin_radius=2)

    def test_vicinities_pso3(self):
        test_pso(vicinities=True, vicin_radius=3)

if __name__ == '__main__':
    unittest.main()
