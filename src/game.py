from insects import *
from count_hives import HiveGraph
from state import State
from utils import *
import time
import random
import math

W = -1
B = 1


class Game:
    def __init__(self, time_limit, iter_limit):
        self.time_limit = time_limit
        self.iter_limit = iter_limit
        self.state = State()


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
                if type(state.board.board[row][col]) is not Blank and state.hexa_selected != state.board.board[row][
                    col]:
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
            if (r2, c2) == (r, c):
                continue
            state.hexa_selected.r, state.hexa_selected.c = r2, c2
            state.board.board[r1][c1] = Blank()
            for (r3, c3) in get_possible_moves_bee(state):
                if (r3, c3) == (r, c) or (r3, c3) == (r1, c1):
                    continue
                possible_moves.add((r3, c3))
    state.hexa_selected.r, state.hexa_selected.c = r, c
    state.board.board[r][c] = o
    # print(time.time()-t)
    return possible_moves


def get_possible_moves_ant(state):
    # TODO freedom to move broken
    t = time.time()
    if not move_away_wont_break_hive(state):
        return set()
    possible_moves = set()
    for r, _ in enumerate(state.board.board):
        for c, hexa in enumerate(state.board.board[r]):
            if (r, c) == (state.hexa_selected.r, state.hexa_selected.c):
                continue
            if type(state.board.board[r][c]) is not Blank:
                for n_r, n_c in get_cell_neighbours(r, c, state.board.height, state.board.width):
                    if type(state.board.board[n_r][n_c]) is Blank:
                        hexa_neighbours, surrounded_five_plus = get_hexa_neighbours(n_r, n_c, state)
                        if not surrounded_five_plus:
                            for (r_, c_) in hexa_neighbours:
                                if type(state.board.board[r_][
                                            c_]) is Blank:  # and not breaks_freedom_to_move(r_, c_, n_r, n_c, state):
                                    possible_moves.add((n_r, n_c))
                                    break
    # print(time.time()-t)
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
            if type(state.board.board[r][c]) is Blank and breaks_freedom_to_move(r, c, rf, cf, state):
                continue
            if type(state.board.board[r][c]) is Blank:
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


def player_able_to_move(state):
    for row in range(state.board.height):
        for col, hexa in enumerate(state.board.board[row]):
            if hexa.player == state.players_turn:
                state.hexa_selected = hexa
                if len(get_possible_moves_from_board(state)) > 0:
                    return True
    return False


def set_player_turn(state):
    # if state.players_turn == W and state.start_tiles.board_count_w > 0 or \
    #         state.players_turn == B and state.start_tiles.board_count_b > 0:
    #     return
    if state.board.board_count < 2:
        return
    elif not player_able_to_move(state):
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


# def get_reward(state):
#     count_n_w = 0
#     count_n_b = 0
#     for n in get_cell_neighbours(*state.bee_pos_white, state.board.height, state.board.width):
#         hexa = state.board.board[n[0]][n[1]]
#         if type(hexa) is not Blank:
#             count_n_w += 1
#     for n in get_cell_neighbours(*state.bee_pos_black, state.board.height, state.board.width):
#         hexa = state.board.board[n[0]][n[1]]
#         if type(hexa) is not Blank:
#             count_n_b += 1
#     return (1/6) * count_n_w - (1/6) * count_n_b


def get_reward(state):
    count = 0
    for n in get_cell_neighbours(*state.bee_pos_black, state.board.height, state.board.width):
        hexa = state.board.board[n[0]][n[1]]
        if type(hexa) is not Blank:
            count += 1
    return (-1 / 6) * count  # Negative for white to win


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
                make_move(state, row, col, fromm)
                return


def get_rack_inidices(player):
    if player == -1:
        return 0, 3
    else:
        return 3, 6


def generate_random_full_board(state, seed=None):
    print('Generating random board state...')
    if seed:
        random.seed(seed)
    random.shuffle(state.white_pieces_start)
    random.shuffle(state.black_pieces_start)
    row, col = state.white_pieces_start[-1]
    state.hexa_selected = state.start_tiles.board[row][col]
    make_move(state=state, to_row=8, to_col=8, fromm_board=state.start_tiles)
    row, col = state.black_pieces_start[-1]
    state.hexa_selected = state.start_tiles.board[row][col]
    make_move(state=state, to_row=9, to_col=8, fromm_board=state.start_tiles)
    state.first_move_white = False
    state.first_move_black = False
    while state.board.board_count < 22:
        make_random_move_from_rack(state)
    print('Random board state generated.')


def make_random_move_from_board(state):
    moves = dict()
    for row in range(state.board.height):
        for col, hexa in enumerate(state.board.board[row]):
            if type(hexa) is not Blank and hexa.player == state.players_turn:
                state.hexa_selected = hexa
                rf, cf = state.hexa_selected.r, state.hexa_selected.c
                poss_moves = list(get_possible_moves_from_board(state))
                if len(poss_moves) > 0:
                    moves[(rf, cf)] = poss_moves
    move_from = random.choice(list(moves.keys()))
    move = random.choice(moves[move_from])
    row, col = move[0], move[1]
    rf, cf = move_from
    state.hexa_selected = state.board.board[rf][cf]
    make_move(state=state, to_row=row, to_col=col, fromm_board=state.board)
    return f'{rf}, {cf} to {row}, {col}'


def make_random_move_from_rack(state):
    if state.players_turn == W and not state.bee_placed_white and state.turn_count_white == 3:
        state.hexa_selected = state.start_tiles.board[0][3]
        move = random.choice(list(get_possible_moves_from_rack(state)))
        row, col = move[0], move[1]
        make_move(state=state, to_row=row, to_col=col, fromm_board=state.start_tiles)
    elif state.players_turn == B and not state.bee_placed_black and state.turn_count_black == 3:
        state.hexa_selected = state.start_tiles.board[3][3]
        move = random.choice(list(get_possible_moves_from_rack(state)))
        row, col = move[0], move[1]
        make_move(state=state, to_row=row, to_col=col, fromm_board=state.start_tiles)
    else:
        row, col = state.white_pieces_start[-1] if state.players_turn == W else state.black_pieces_start[-1]
        state.hexa_selected = state.start_tiles.board[row][col]
        move = random.choice(list(get_possible_moves_from_rack(state)))
        row, col = move[0], move[1]
        make_move(state=state, to_row=row, to_col=col, fromm_board=state.start_tiles)


def make_random_move_from_anywhere(state):
    i = random.getrandbits(1)
    if i == 0 and \
            ((state.players_turn == -1 and len(state.white_pieces_start) > 0) or
             (state.players_turn == 1 and len(state.black_pieces_start) > 0)):
        try:
            make_random_move_from_rack(state)
        except IndexError:
            # Occurs if a player cannot legally move from rack but still has rack pieces
            make_random_move_from_board(state)
    else:
        make_random_move_from_board(state)


def make_first_move_each(state):
    random.shuffle(state.white_pieces_start)
    random.shuffle(state.black_pieces_start)
    row, col = state.white_pieces_start[-1]
    state.hexa_selected = state.start_tiles.board[row][col]
    make_move(state=state, to_row=8, to_col=8, fromm_board=state.start_tiles)
    row, col = state.black_pieces_start[-1]
    state.hexa_selected = state.start_tiles.board[row][col]
    make_move(state=state, to_row=9, to_col=8, fromm_board=state.start_tiles)
    state.first_move_white = False
    state.first_move_black = False


def make_mcts_move(state, action):
    if action.r_f < 0:
        action.r_f = abs(action.r_f) - 1
        state.hexa_selected = state.start_tiles.board[action.r_f][action.c_f]
        make_move(state, action.r_t, action.c_t, state.start_tiles)
    else:
        state.hexa_selected = state.board.board[action.r_f][action.c_f]
        make_move(state, action.r_t, action.c_t, state.board)


def convert_vel(vel, insect_type):
    new_vel = []
    v_threshold = 0.25
    for value in vel:
        v = floor(value) if value > 0 else math.ceil(value)
        if value - v > v_threshold:
            v += 1
        elif value - v < -v_threshold:
            v -= 1
        if insect_type is Bee or insect_type is Beetle:
            if v < 0:
                new_vel.append(-1)
            else:
                new_vel.append(1)
        else:
            new_vel.append(v)
    return new_vel


def nearest_move_after_vel(new_pos, possible_moves, goal):
    # maximum TWO positions in new_pos due to East-West/ West-East moves
    pos1 = new_pos.pop()
    pos2 = None if not new_pos else new_pos.pop()
    closest_dist_seen = float('inf')
    final_pos = None
    for move in possible_moves:
        d1 = distance_between_(pos1, move)
        if d1 < closest_dist_seen:
            closest_dist_seen = distance_between_(pos1, move)
            final_pos = move
        if pos2:
            d2 = distance_between_(pos2, move)
            if d2 < closest_dist_seen:
                closest_dist_seen = distance_between_(pos2, move)
                final_pos = move

    return final_pos
