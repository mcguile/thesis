from insects import *
from count_hives import HiveGraph
from utils import *
import time
import random
import math
import numpy as np
from swarm import fitness
from copy import deepcopy

W = -1
B = 1


def opp(player):
    return B if player == W else W


def get_hexa_neighbours(r, c, state):
    neighbours = set()
    non_blank_neighbours = 0
    min_r, max_r, min_c, max_c = get_minmax_rowcol(r, c, state.board.height, state.board.width)
    for row in range(min_r, max_r + 1):
        for col in range(min_c, max_c + 1):
            if col == c and row == r:
                continue
            elif (c % 2 == 0) and ((col == c + 1 and row == r + 1) or (row == r + 1 and col == c - 1)):
                continue
            elif (c % 2 == 1) and ((col == c - 1 and row == r - 1) or (row == r - 1 and col == c + 1)):
                continue
            else:
                if type(state.board.board[row][col]) is not Blank and state.hexa_selected != state.board.board[row][col]:
                    non_blank_neighbours += 1
                neighbours.add((row, col))
    return neighbours, non_blank_neighbours > 4


def in_bounds(r, c, state):
    try:
        _ = state.board.board[r][c]
        return True
    except IndexError:
        return False


def hex_is_not_blank(r, c, state):
    return in_bounds(r, c, state) and type(state.board.board[r][c]) is not Blank


def breaks_freedom_to_move(r, c, R, C, state):
    # R, C are FROM; r, c are TO
    if r == R - 1 and c == C:
        # North
        return hex_is_not_blank(R - 1, C - 1, state) and hex_is_not_blank(R - 1, C + 1, state) if C % 2 == 0 else \
            hex_is_not_blank(R, C - 1, state) and hex_is_not_blank(R, C + 1, state)
    elif r == R + 1 and c == C:
        # South
        return hex_is_not_blank(R, C - 1, state) and hex_is_not_blank(R, C + 1, state) if C % 2 == 0 else \
            hex_is_not_blank(R + 1, C - 1, state) and hex_is_not_blank(R + 1, C + 1, state)

    if C % 2 == 0:
        if r == R - 1 and c == C - 1:
            # North-West even column
            return hex_is_not_blank(R - 1, C, state) and hex_is_not_blank(R, C - 1, state)
        if r == R and c == C - 1:
            # South-West even column
            return hex_is_not_blank(R + 1, C, state) and hex_is_not_blank(R - 1, C - 1, state)
        if r == R - 1 and c == C + 1:
            # North-East even column
            return hex_is_not_blank(R - 1, C, state) and hex_is_not_blank(R, C + 1, state)
        else:
            # South-East even column
            return hex_is_not_blank(R + 1, C, state) and hex_is_not_blank(R - 1, C + 1, state)
    else:
        if r == R and c == C - 1:
            # North-West odd column
            return hex_is_not_blank(R - 1, C, state) and hex_is_not_blank(R + 1, C - 1, state)
        if r == R + 1 and c == C - 1:
            # South-West odd column
            return hex_is_not_blank(R + 1, C, state) and hex_is_not_blank(R, C - 1, state)
        if r == R and c == C + 1:
            # North-East odd column
            return hex_is_not_blank(R + 1, C + 1, state) and hex_is_not_blank(R - 1, C, state)
        else:
            # South-East odd column
            return hex_is_not_blank(R, C + 1, state) and hex_is_not_blank(R + 1, C, state)


def all_neighbours_but_selected_are_blank(neighbours, blocked, state):
    """
    Returns true if all neighbours of (r,c) are blank excluding the currently selected
    hexagon which is also a neighbour of (r,c).
    """
    for row, col in neighbours:
        if type(state.board.board[row][col]) is not Blank and (row, col) not in blocked:
            return False
    return True


def move_away_wont_break_hive(state):
    if type(state.hexa_selected) is Stack:
        return False
    neighbours = get_cell_neighbours(state.hexa_selected.r, state.hexa_selected.c, state.board.height,
                                     state.board.width)
    count_nonblank_neighbours = 0
    for r, c in neighbours:
        if type(state.board.board[r][c]) is not Blank:
            count_nonblank_neighbours += 1
    if count_nonblank_neighbours <= 1:
        return True
    else:
        tmp = state.board.board[state.hexa_selected.r][state.hexa_selected.c]
        state.board.board[state.hexa_selected.r][state.hexa_selected.c] = Blank()
        one_hive = HiveGraph(state.board).one_hive()
        state.board.board[state.hexa_selected.r][state.hexa_selected.c] = tmp
        return one_hive


def get_possible_moves_bee(state):
    # t = time.time()
    possible_moves = set()
    neighbours_of_selected, cant_move = get_hexa_neighbours(state.hexa_selected.r, state.hexa_selected.c, state)
    if not cant_move:
        if move_away_wont_break_hive(state):
            for (r, c) in neighbours_of_selected:
                if type(state.board.board[r][c]) is Blank:
                    if breaks_freedom_to_move(r, c, state.hexa_selected.r, state.hexa_selected.c, state):
                        continue
                    neighbours_of_neighbour, _ = get_hexa_neighbours(r, c, state)
                    for (r_, c_) in neighbours_of_neighbour:
                        if type(state.board.board[r_][c_]) is not Blank and \
                                (r_, c_) != (state.hexa_selected.r, state.hexa_selected.c) and \
                                (r_, c_) not in possible_moves and \
                                (r_, c_) in neighbours_of_selected:
                            possible_moves.add((r, c))
    # print(time.time()-t)
    return possible_moves


def get_possible_moves_spider(state):
    # do Bee move three times
    # t = time.time()
    possible_moves = set()
    o = state.hexa_selected
    r, c = state.hexa_selected.r, state.hexa_selected.c
    for (r1, c1) in get_possible_moves_bee(state):
        state.hexa_selected.r, state.hexa_selected.c = r1, c1
        state.board.board[r][c] = Blank()
        for (r2, c2) in get_possible_moves_bee(state):
            if (r2, c2) != (r, c):
                state.hexa_selected.r, state.hexa_selected.c = r2, c2
                state.board.board[r1][c1] = Blank()
                for (r3, c3) in get_possible_moves_bee(state):
                    if (r3, c3) != (r, c) and (r3, c3) != (r1, c1):
                        possible_moves.add((r3, c3))
    state.hexa_selected.r, state.hexa_selected.c = r, c
    state.board.board[r][c] = o
    # print(time.time()-t)
    return possible_moves


def get_possible_moves_ant(state):
    # t = time.time()
    if not move_away_wont_break_hive(state):
        return set()
    possible_moves = set()
    rf, cf = state.hexa_selected.r, state.hexa_selected.c
    o = state.hexa_selected
    state.board.board[rf][cf] = Blank()
    moves = get_possible_moves_bee(state)

    def recur(bee_moves):
        for (r, c) in bee_moves:
            if (r, c) not in possible_moves:
                possible_moves.add((r, c))
                state.hexa_selected.r, state.hexa_selected.c = r, c
                bee_moves = get_possible_moves_bee(state)
                recur(bee_moves)

    recur(moves)
    state.hexa_selected.r, state.hexa_selected.c = rf, cf
    state.board.board[rf][cf] = o
    possible_moves.discard((rf, cf))
    return possible_moves


def get_possible_moves_beetle(state):
    # t = time.time()
    possible_moves = set()
    neighbours_of_selected, _ = get_hexa_neighbours(state.hexa_selected.r, state.hexa_selected.c, state)
    if type(state.hexa_selected) is Stack:
        return neighbours_of_selected
    rf, cf = state.hexa_selected.r, state.hexa_selected.c
    if move_away_wont_break_hive(state):
        for (r, c) in neighbours_of_selected:
            if type(state.board.board[r][c]) is Blank:
                if breaks_freedom_to_move(r, c, state.hexa_selected.r, state.hexa_selected.c, state):
                    continue
                neighbours_of_neighbour, _ = get_hexa_neighbours(r, c, state)
                for (r_, c_) in neighbours_of_neighbour:
                    if type(state.board.board[r_][c_]) is not Blank and \
                            (r_, c_) != (state.hexa_selected.r, state.hexa_selected.c) and \
                            (r_, c_) in neighbours_of_selected:
                        possible_moves.add((r, c))
            else:
                possible_moves.add((r, c))
    # print(time.time()-t)
    return possible_moves


def get_possible_moves_grasshopper(state):
    # t = time.time()
    possible_moves = set()
    r, c = state.hexa_selected.r, state.hexa_selected.c
    n, s, ne, se, sw, nw = get_hexas_straight_line((r, c), state.board.width, state.board.height)
    if move_away_wont_break_hive(state):
        for direction in [n, s, ne, se, sw, nw]:
            found_bug_to_jump = False
            for r, c in direction:
                if 0 <= r < state.board.height and 0 <= c < state.board.width:
                    if not found_bug_to_jump:
                        if type(state.board.board[r][c]) is Blank:
                            break
                        else:
                            found_bug_to_jump = True
                            continue
                    neighbours_of_neighbour = get_cell_neighbours(r, c, state.board.height, state.board.width)
                    if type(state.board.board[r][c]) is Blank and \
                            not all_neighbours_but_selected_are_blank(neighbours_of_neighbour,
                                                                      [(state.hexa_selected.r, state.hexa_selected.c)],
                                                                      state):
                        possible_moves.add((r, c))
                        break
    # print(time.time()-t)
    return possible_moves


def get_possible_moves_from_board(state):
    if (state.players_turn == W and not state.bee_placed_white) or \
            (state.players_turn == B and not state.bee_placed_black) or \
            state.hexa_selected.player != state.players_turn:
        return set()
    else:
        t = type(state.hexa_selected)
        if t == Bee:
            return get_possible_moves_bee(state)
        elif t == Spider:
            return get_possible_moves_spider(state)
        elif t == Ant:
            return get_possible_moves_ant(state)
        elif t == Beetle or t == Stack:
            return get_possible_moves_beetle(state)
        else:
            return get_possible_moves_grasshopper(state)


def make_move(state, to_row, to_col, fromm_board):
    f_row, f_col = state.hexa_selected.r, state.hexa_selected.c
    if state.players_turn == W:
        if type(fromm_board.board[f_row][f_col]) is not Stack:
            state.white_positions.discard((f_row, f_col))
        state.white_positions.add((to_row, to_col))
    else:
        if type(fromm_board.board[f_row][f_col]) is not Stack:
            state.black_positions.discard((f_row, f_col))
        state.black_positions.add((to_row, to_col))

    if fromm_board == state.start_tiles:
        if f_row >= 3:
            state.black_pieces_start.remove((f_row, f_col))
        else:
            state.white_pieces_start.remove((f_row, f_col))
        if state.players_turn == W:
            state.start_tiles.board_count_w -= 1
        else:
            state.start_tiles.board_count_b -= 1
        state.board.board_count += 1
    dest_t = type(state.board.board[to_row][to_col])
    if dest_t is not Blank:
        # Must be a beetle making move
        # Check if selected is just a beetle or a stack
        if type(state.hexa_selected) is Stack:
            beetle = state.hexa_selected.remove_piece()
            if len(state.hexa_selected.stack) == 1:
                fromm_board.board[f_row][f_col] = state.hexa_selected.stack[0]
            else:
                fromm_board.board[f_row][f_col] = state.hexa_selected
            state.hexa_selected = beetle
        else:
            fromm_board.board[f_row][f_col] = Blank()
        # Create stack or append to the stack
        if dest_t is Stack:
            state.board.board[to_row][to_col].add_piece(state.hexa_selected)
        else:
            state.board.board[to_row][to_col] = Stack(first_piece=state.board.board[to_row][to_col],
                                                      stacked_piece=state.hexa_selected,
                                                      row=to_row, col=to_col)
    else:
        if type(fromm_board.board[f_row][f_col]) is not Stack:
            fromm_board.board[f_row][f_col] = Blank()
        else:
            beetle = state.hexa_selected.remove_piece()
            if len(state.hexa_selected.stack) == 1:
                fromm_board.board[f_row][f_col] = state.hexa_selected.stack[0]
            else:
                fromm_board.board[f_row][f_col] = state.hexa_selected
            state.hexa_selected = beetle
        state.board.board[to_row][to_col] = state.hexa_selected
        if type(state.hexa_selected) == Bee:
            if state.players_turn == W:
                state.bee_placed_white = True
                state.bee_pos_white = [to_row, to_col]
            else:
                state.bee_placed_black = True
                state.bee_pos_black = [to_row, to_col]
    state.hexa_selected.r, state.hexa_selected.c = to_row, to_col
    increment_turn_count(state)
    state.players_turn = opp(state.players_turn)
    set_player_turn(state)
    state.hexa_selected = None
    state.possible_moves = set()


def can_move_from_board(state):
    for row in range(state.board.height):
        for col, hexa in enumerate(state.board.board[row]):
            if hexa.player == state.players_turn:
                state.hexa_selected = hexa
                if len(get_possible_moves_from_board(state)) > 0:
                    return True
    return False


def can_move_from_rack(state):
    start, stop = get_rack_inidices(state.players_turn)
    for row in range(start, stop):
        for col, hexa in enumerate(state.start_tiles.board[row]):
            if hexa.player == state.players_turn:
                state.hexa_selected = hexa
            for r, _ in enumerate(state.board.board):
                for c, hexa in enumerate(state.board.board[r]):
                    neighbours = get_cell_neighbours(r, c, state.board.height, state.board.width)
                    valid_placement = True
                    found_own_tile = False
                    for x, y in neighbours:
                        if state.board.board[x][y].player == state.players_turn:
                            found_own_tile = True
                        elif state.board.board[x][y].player == opp(state.players_turn) or type(
                                state.board.board[r][c]) != Blank:
                            valid_placement = False
                    if found_own_tile and valid_placement:
                        return True
    return False


def set_player_turn(state):
    if state.board.board_count < 2 or can_move_from_board(state) or can_move_from_rack(state):
        return
    else:
        state.players_turn = opp(state.players_turn)


def move_white_first(state, first_move, event):
    r, c = state.board.height // 2, state.board.width // 2
    if first_move:
        for row in range(state.start_tiles.height // 2):
            for col, hexa in enumerate(state.start_tiles.board[row]):
                if hexa.rect.collidepoint(event.pos) and type(hexa) is not Blank:
                    state.hexa_selected = hexa
                    make_move(state, r, c, state.start_tiles)
                    state.hexa_selected = None
                    return False
    return first_move


def black_has_moved(state):
    start, stop = state.start_tiles.height // 2, state.start_tiles.height
    count = 0
    for row in range(start, stop):
        for col, hexa in enumerate(state.start_tiles.board[row]):
            if type(hexa) is not Blank:
                count += 1
    return count < 11


def is_bee_placed(state, player):
    if player == W:
        return state.bee_placed_white
    else:
        return state.bee_placed_black


def isGameOver(state):
    return has_won(state, W) or has_won(state, B)


def count_around_own_queen(state):
    count = 6
    bee_pos = state.bee_pos_white if state.players_turn == W else state.bee_pos_black
    for n in get_cell_neighbours(*bee_pos, state.board.height, state.board.width):
        hexa = state.board.board[n[0]][n[1]]
        if type(hexa) is Blank:
            count -= 1
    return count


def get_reward(state):
    count_around_white = 6
    count_around_black = 6
    for n in get_cell_neighbours(*state.bee_pos_white, state.board.height, state.board.width):
        hexa = state.board.board[n[0]][n[1]]
        if type(hexa) is Blank:
            count_around_white -= 1
    for n in get_cell_neighbours(*state.bee_pos_black, state.board.height, state.board.width):
        hexa = state.board.board[n[0]][n[1]]
        if type(hexa) is Blank:
            count_around_black -= 1
    if count_around_white == 6:
        return 1
    elif count_around_black == 6:
        return -1
    else:
        return 0


def has_won(state, player):
    if state.turn_count_black < 5 or state.board.board_count < 7:
        return False
    won = True
    bee_pos = state.bee_pos_white if player == B else state.bee_pos_black
    for n in get_cell_neighbours(*bee_pos, state.board.height, state.board.width):
        hexa = state.board.board[n[0]][n[1]]
        if type(hexa) is Blank:
            won = False
    return won


def increment_turn_count(state):
    if state.players_turn == W:
        state.turn_count_white += 1
    else:
        state.turn_count_black += 1


def get_possible_moves_from_rack(state):
    if state.players_turn == W and not state.bee_placed_white and state.turn_count_white == 3:
        state.hexa_selected = state.start_tiles.board[0][3]
    elif state.players_turn == B and not state.bee_placed_black and state.turn_count_black == 3:
        state.hexa_selected = state.start_tiles.board[3][3]
    possible_moves = set()
    for r, _ in enumerate(state.board.board):
        for c, hexa in enumerate(state.board.board[r]):
            neighbours = get_cell_neighbours(r, c, state.board.height, state.board.width)
            valid_placement = True
            found_own_tile = False
            for x, y in neighbours:
                if state.board.board[x][y].player == state.players_turn:
                    found_own_tile = True
                elif state.board.board[x][y].player == opp(state.players_turn) or type(
                        state.board.board[r][c]) != Blank:
                    valid_placement = False
            if found_own_tile and valid_placement:
                possible_moves.add((r, c))
    return possible_moves


def get_possible_first_moves_black(state):
    return set(get_cell_neighbours(state.board.width // 2, state.board.height // 2,
                                   state.board.height, state.board.width))


def move_to_board(state, event, fromm):
    for row in range(state.board.height):
        for col, hexa in enumerate(state.board.board[row]):
            if hexa.rect.collidepoint(event.pos) and (row, col) in state.possible_moves:
                rf, cf = state.hexa_selected.r, state.hexa_selected.c
                ret = f'r r {state.players_turn} {rf},{cf} {row},{col}'
                make_move(state, row, col, fromm)
                return ret



def get_rack_inidices(player):
    if player == -1:
        return 0, 3
    else:
        return 3, 6


def generate_random_full_board(state):
    # print('Generating random board state...')
    random.shuffle(state.white_pieces_start)
    random.shuffle(state.black_pieces_start)
    row, col = state.white_pieces_start[-1]
    state.hexa_selected = state.start_tiles.board[row][col]
    ret = f'r r {state.players_turn} {row},{col} (8,8)'
    make_move(state=state, to_row=8, to_col=8, fromm_board=state.start_tiles)
    row, col = state.black_pieces_start[-1]
    state.hexa_selected = state.start_tiles.board[row][col]
    ret += f'\nr r {state.players_turn} {row},{col} (9,8)'
    make_move(state=state, to_row=9, to_col=8, fromm_board=state.start_tiles)
    state.first_move_white = False
    state.first_move_black = False
    while state.board.board_count < 22:
        ret += '\n' + make_random_move_from_rack(state)
    # print('Random board state generated.')
    return ret


def make_random_move_from_board(state):
    moves = dict()
    for row in range(state.board.height):
        for col, hexa in enumerate(state.board.board[row]):
            if type(hexa) is not Blank and hexa.player == state.players_turn:
                state.hexa_selected = hexa
                poss_moves = list(get_possible_moves_from_board(state))
                if len(poss_moves) > 0:
                    moves[(row, col)] = poss_moves
    move_from = random.choice(list(moves.keys()))
    move = random.choice(moves[move_from])
    row, col = move[0], move[1]
    rf, cf = move_from
    state.hexa_selected = state.board.board[rf][cf]
    ret = f'r b {state.players_turn} {rf},{cf} {row},{col}'
    make_move(state=state, to_row=row, to_col=col, fromm_board=state.board)
    return ret


def make_random_move_from_rack(state):
    if state.players_turn == W:
        if state.turn_count_white == 3 and not state.bee_placed_white:
            rf, cf = 0, 3
        else:
            rf, cf = state.white_pieces_start[-1]
    else:
        if state.turn_count_black == 3 and not state.bee_placed_black:
            rf, cf = 3, 3
        else:
            rf, cf = state.black_pieces_start[-1]
    state.hexa_selected = state.start_tiles.board[rf][cf]
    move = random.choice(list(get_possible_moves_from_rack(state)))
    row, col = move[0], move[1]
    ret = f'r r {state.players_turn} {rf},{cf} {row},{col}'
    make_move(state=state, to_row=row, to_col=col, fromm_board=state.start_tiles)
    return ret


def make_random_move_from_anywhere(state):
    ret = None
    if state.players_turn == W and not state.bee_placed_white and state.turn_count_white == 3:
        state.hexa_selected = state.start_tiles.board[0][3]
        move = random.choice(list(get_possible_moves_from_rack(state)))
        row, col = move[0], move[1]
        ret = f'r r {state.players_turn} (0,3) {row},{col}'
        make_move(state=state, to_row=row, to_col=col, fromm_board=state.start_tiles)
    elif state.players_turn == B and not state.bee_placed_black and state.turn_count_black == 3:
        state.hexa_selected = state.start_tiles.board[3][3]
        move = random.choice(list(get_possible_moves_from_rack(state)))
        row, col = move[0], move[1]
        ret = f'r r {state.players_turn} (3,3) {row},{col}'
        make_move(state=state, to_row=row, to_col=col, fromm_board=state.start_tiles)
    elif (state.players_turn == W and not state.bee_placed_white) or (state.players_turn == B and not state.bee_placed_black):
        ret = make_random_move_from_rack(state)
    else:
        i = random.getrandbits(1)
        if i == 0 and \
                ((state.players_turn == W and len(state.white_pieces_start) > 0) or
                 (state.players_turn == B and len(state.black_pieces_start) > 0)):
            try:
                move = make_random_move_from_rack(state)
            except IndexError:
                # Occurs if a player cannot legally move from rack but still has rack pieces
                try:
                    ret = make_random_move_from_board(state)
                except IndexError:
                    state.players_turn = opp(state.players_turn)
        else:
            try:
                ret = make_random_move_from_board(state)
            except IndexError:
                state.players_turn = opp(state.players_turn)
    return ret


def make_first_move_each(state):
    random.shuffle(state.white_pieces_start)
    random.shuffle(state.black_pieces_start)
    r1, c1 = state.white_pieces_start[-1]
    state.hexa_selected = state.start_tiles.board[r1][c1]
    make_move(state=state, to_row=8, to_col=8, fromm_board=state.start_tiles)
    r2, c2 = state.black_pieces_start[-1]
    state.hexa_selected = state.start_tiles.board[r2][c2]
    make_move(state=state, to_row=9, to_col=8, fromm_board=state.start_tiles)
    state.first_move_white = False
    state.first_move_black = False
    return f'f r -1 {r1},{c1} (8,8)\nf r 1 {r2},{c2} (9,8)'


def make_mcts_move(state, action):
    if action.r_f < 0:
        action.r_f = abs(action.r_f) - 1
        state.hexa_selected = state.start_tiles.board[action.r_f][action.c_f]
        ret = f'm r {state.players_turn} {action.r_f},{action.c_f} {action.r_t},{action.c_t}'
        make_move(state, action.r_t, action.c_t, state.start_tiles)
    else:
        state.hexa_selected = state.board.board[action.r_f][action.c_f]
        ret = f'm b {state.players_turn} {action.r_f},{action.c_f} {action.r_t},{action.c_t}'
        make_move(state, action.r_t, action.c_t, state.board)
    return ret


def convert_vel(vel):
    new_vel = []
    v_threshold = 0.25
    for value in vel:
        v = floor(value) if value > 0 else math.ceil(value)
        if value - v > v_threshold:
            v += 1
        elif value - v < -v_threshold:
            v -= 1
        new_vel.append(v)
    return np.array(new_vel)


def nearest_move_after_vel(desired_pos, possible_moves, goal):
    # maximum TWO positions in new_pos due to East-West/ West-East moves
    new_pos = list(desired_pos)
    pos1 = new_pos[-1]
    pos2 = None if len(new_pos) == 1 else new_pos[0]
    closest_dist_seen = float('inf')
    final_pos = None
    for move in possible_moves:
        d1 = distance_between_(pos1, move)
        if d1 < closest_dist_seen:
            closest_dist_seen = distance_between_(pos1, move)
            final_pos = move
        elif d1 == closest_dist_seen:
            final_pos = move if distance_between_(move, goal) < distance_between_(final_pos, goal) else final_pos
        if pos2:
            d2 = distance_between_(pos2, move)
            if d2 < closest_dist_seen:
                closest_dist_seen = distance_between_(pos2, move)
                final_pos = move
            elif d2 == closest_dist_seen:
                final_pos = move if distance_between_(move, goal) < distance_between_(final_pos, goal) else final_pos
    return final_pos


def move_nearest_to_goal(state, movable_positions, infinite_moves=False):
    player_turn = state.players_turn
    final_move = []
    possible_moves_dict = dict()
    shortest_dist = float('inf')
    goal = state.bee_pos_white if state.players_turn == B else state.bee_pos_black
    for row, col in movable_positions:
        hexa = state.board.board[row][col]
        if hexa.player == state.players_turn:
            state.hexa_selected = hexa
            possible_moves = get_possible_moves_from_board(state)
            if possible_moves:
                possible_moves_dict[(row, col)] = list(possible_moves)
            for move in possible_moves:
                d = distance_between_(move, goal)
                if d <= shortest_dist and distance_between_((row, col), goal) > d:
                    if d == shortest_dist:
                        final_move.append([(row, col), move])
                    else:
                        final_move = [[(row, col), move]]
                    shortest_dist = d
    if final_move:
        if len(final_move) == 1:
            from_row, from_col = final_move[0][0][0], final_move[0][0][1]
            to_row, to_col = final_move[0][1][0], final_move[0][1][1]
        else:
            worst_fitness = 0
            from_row, from_col = None, None
            to_row, to_col = None, None
            for from_pos, to_pos in final_move:
                if distance_between_(from_pos, goal) > worst_fitness:
                    worst_fitness = distance_between_(from_pos, goal)
                    from_row, from_col = from_pos
                    to_row, to_col = to_pos
    else:
        if possible_moves_dict.keys():
            move_from = random.choice(list(possible_moves_dict.keys()))
            move = random.choice(possible_moves_dict[move_from])
            to_row, to_col = move[0], move[1]
            from_row, from_col = move_from
        else:
            if infinite_moves:
                state.players_turn = player_turn
            return 'pass'
    state.hexa_selected = state.board.board[from_row][from_col]
    ret = f's b {state.players_turn} {from_row},{from_col} {to_row},{to_col}'
    make_move(state, to_row, to_col, state.board)
    if infinite_moves:
        state.players_turn = player_turn
    return ret


def make_swarm_move(state, space, intention_criteria=0, full_swarm_move=False, infinite_moves=False):
    player_turn = state.players_turn
    space.set_pbest()
    space.set_gbest()
    playable_positions = set()
    for row in range(state.board.height):
        for col, hexa in enumerate(state.board.board[row]):
            if hexa.player == state.players_turn:
                playable_positions.add((row,col))
    for particle, from_pos, new_vel in space.get_velocities():
        f_r, f_c = from_pos
        new_vel = convert_vel(new_vel)
        particle.vel = new_vel
        particle.intention = 0
        if (new_vel[0] != 0 or new_vel[1] != 0) and (f_r, f_c) in playable_positions:
            state.hexa_selected = state.board.board[f_r][f_c]
            set_of_new_pos = transform_cell_pos_from_velocity(new_vel, from_pos)
            possible_moves = get_possible_moves_from_board(state)
            if possible_moves:
                r, c = nearest_move_after_vel(set_of_new_pos, possible_moves, space.target)
                particle.desired_pos_nearest = (r, c)
                set_intention(state, space, particle, set_of_new_pos, (r, c), intention_criteria)
                # Below is only for testing of PSO - not used in actual game play
                if full_swarm_move:
                    make_move(state, r, c, state.board)
                    particle.pos = np.array([r, c])
                    if infinite_moves:
                        state.players_turn = player_turn
                    if isGameOver(state):
                        return
                # End test code
            else:
                particle.desired_pos_nearest = None
    if not full_swarm_move:
        best_in_vicins = space.get_best_in_vicinities()
        best_particle = space.get_best_particle_equal_score(best_in_vicins)
        if best_particle and best_particle.desired_pos_nearest:
            r, c = best_particle.desired_pos_nearest
            f_r, f_c = best_particle.pos
            state.hexa_selected = state.board.board[f_r][f_c]
            ret = f's b {state.players_turn} {f_r},{f_c} {r},{c}'
            make_move(state, r, c, state.board)
            best_particle.pos = np.array([r, c])
        else:
            state.turn_count_white += 1
            ret = 'pass'
        if infinite_moves:
            state.players_turn = player_turn
        return ret


def set_intention(state, space, particle, set_of_new_pos, selected_pos, intention_criteria):
    desired_pos = list(set_of_new_pos)
    if len(desired_pos) > 1:
        if distance_between_(desired_pos[0], selected_pos) <= distance_between_(desired_pos[1], selected_pos):
            desired_pos = desired_pos[0]
        else:
            desired_pos = desired_pos[1]
    else:
        desired_pos = desired_pos[0]
    accuracy_intent = max(0, 5-distance_between_(desired_pos, selected_pos))
    velocity_intent = distance_between_(desired_pos, particle.pos)
    danger_intent = 0
    bee_pos = state.bee_pos_white if state.players_turn == W else state.bee_pos_black
    if distance_between_(particle.pos, bee_pos) == 1:
        c = count_around_own_queen(state)
        if c == 4:
            if particle.pos[0] == bee_pos[0] and particle.pos[1] == bee_pos[1]:
                danger_intent = 4
            else:
                danger_intent = 3
        elif c == 5:
            if particle.pos[0] == bee_pos[0] and particle.pos[1] == bee_pos[1]:
                danger_intent = 8
            else:
                danger_intent = 6
    if intention_criteria == 0:
        particle.intention = velocity_intent + danger_intent
    elif intention_criteria == 1:
        particle.intention = accuracy_intent + danger_intent
    elif intention_criteria == 2:
        particle.intention = particle.pbest_value + danger_intent
    elif intention_criteria == 3:
        particle.intention = velocity_intent + accuracy_intent + danger_intent
    elif intention_criteria == 4:
        f = particle.pbest_value
        if f <= 2:
            particle.intention = accuracy_intent + danger_intent
        else:
            particle.intention = velocity_intent + danger_intent
    elif intention_criteria == 5:
        f = fitness(particle, space.target)
        if space.vicin_radius >= f > 1:
            # set intention based on if it can get into space around queen
            r, c = particle.pos
            state.hexa_selected = state.board.board[r][c]
            poss_moves = get_possible_moves_from_board(state)
            bee_r, bee_c = state.bee_pos_white if state.players_turn == 1 else state.bee_pos_black
            neighs, _ = get_hexa_neighbours(bee_r, bee_c, state)
            common = poss_moves.intersection(neighs)
            # for r, c in deepcopy(common):
            #     if type(state.board.board[r][c]) is not Blank:
            #         common.remove((r, c))
            if common:
                particle.desired_pos_nearest = common.pop()
                particle.intention = 5
            else:
                particle.intention = velocity_intent + danger_intent
        else:
            particle.intention = velocity_intent + danger_intent
