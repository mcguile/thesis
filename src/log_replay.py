import argparse
import pathlib


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Play Hive!')
    parser.add_argument('-f', type=str, required=True,
                        help='Log file name')
    parser.add_argument('-ai', help='Start from AI moves', action='store_true')
    args = parser.parse_args()
    if pathlib.Path(args.f).exists():
        from state import State
        from game_with_ui import GameUI
        g = State(time_limit=None, iter_limit=100)
        game = GameUI(g)
        game.play_game_from_log(log_file=args.f, start_from_ai_moves=args.ai)
    else:
        print('File does not exist')