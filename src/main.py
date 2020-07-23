import argparse
import pathlib


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Play Hive!')
    parser.add_argument('-f', type=str, required=True,
                        help='Log file name')
    parser.add_argument('-ai', type=str,
                        help='Start at beginning of AI moves',default=True)

    args = parser.parse_args()
    if pathlib.Path(args.f).exists():
        if args.ai.lower() in ('yes', 'y', 't', 'true', '1'):
            ai = True
            from state import State
            from game_with_ui import GameUI
            g = State(time_limit=None, iter_limit=100)
            game = GameUI(g)
            game.play_game_from_log(args.f, ai)
        elif args.ai.lower() in ('no', 'n', 'f', 'false', '0'):
            ai = False
            from state import State
            from game_with_ui import GameUI
            g = State(time_limit=None, iter_limit=100)
            game = GameUI(g)
            game.play_game_from_log(args.f, ai)
        else:
            print('AI parameter not valid')
    else:
        print('File does not exist')