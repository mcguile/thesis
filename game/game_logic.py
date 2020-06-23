from insects import *
from count_hives import HiveGraph
from copy import deepcopy
from utils import *
import time

W = -1
B = 1


def opp(player):
    return B if player == W else W


def breaks_freedom_to_move_rule(r, c, state):
    """
    Does the hex attempted to be moved to have 5 or more pieces around it?
    'Freedom to move' rule.
    :return: boolean
    """
    neighbours = get_cell_neighbours(r, c, state.board.height, state.board.width)
    count_pieces = 0
    for r, c in neighbours:
        if type(state.board.board[r][c]) != Blank:
            count_pieces += 1
    return count_pieces >= 5


def move_away_wont_break_hive(s):
    state = deepcopy(s)
    if type(state.hexa_selected) is Stack:
        return False
    else:
        state.board.board[state.hexa_selected.r][state.hexa_selected.c] = Blank()
        hives1stcheck = HiveGraph(state.board).count_hives()
        return hives1stcheck


def get_possible_moves_bee(state):
    t = time.time()
    possible_moves = set()
    neighbours_of_selected = get_cell_neighbours(state.hexa_selected.r, state.hexa_selected.c, state.board.height,
                                                 state.board.width)
    # if move_away_wont_break_hive(state):
    for r, c in neighbours_of_selected:
        if type(state.board.board[r][c]) is Blank:
            neighbours_of_neighbour = get_cell_neighbours(r, c, state.board.height, state.board.width)
            if not all_neighbours_but_selected_are_blank(neighbours_of_neighbour,
                                                         [(state.hexa_selected.r, state.hexa_selected.c)], state):
                possible_moves.add((r, c))
    print(time.time()-t)
    return possible_moves


def all_neighbours_but_selected_are_blank(neighbours, blocked, state):
    """
    Returns true if all neighbours of (r,c) are blank excluding the currently selected
    hexagon which is also a neighbour of (r,c).
    """
    for row, col in neighbours:
        if type(state.board.board[row][col]) is not Blank and (row, col) not in blocked:
            return False
    return True


def get_possible_moves_spider(state):
    t = time.time()
    # Spider must move three spaces and only three spaces.
    # Logic is to iterate nested three times for each hexagon
    # in a set of neighbours that are blank and dont break the hive.
    possible_moves = set()
    n1_of_spider = get_cell_neighbours(state.hexa_selected.r, state.hexa_selected.c, state.board.height,
                                       state.board.width)
    for r1, c1 in n1_of_spider:
        n2_of_spider = get_cell_neighbours(r1, c1, state.board.height, state.board.width)
        from_lst = [(state.hexa_selected.r, state.hexa_selected.c)]
        if type(state.board.board[r1][c1]) is Blank and not breaks_freedom_to_move_rule(r1, c1, state) and \
                not all_neighbours_but_selected_are_blank(n2_of_spider, from_lst, state):
            for r2, c2 in n2_of_spider:
                if r2 == r1 and c2 == c1:
                    continue
                n3_of_spider = get_cell_neighbours(r2, c2, state.board.height, state.board.width)
                from_lst.append((r1, c1))
                if type(state.board.board[r2][c2]) is Blank and not breaks_freedom_to_move_rule(r2, c2, state) and \
                        not all_neighbours_but_selected_are_blank(n3_of_spider, from_lst, state):
                    for r3, c3 in n3_of_spider:
                        if r3 == r2 and c3 == c2 or r3 == r1 and c3 == c1:
                            continue
                        n4_of_spider = get_cell_neighbours(r3, c3, state.board.height, state.board.width)
                        from_lst.append((r2, c2))
                        if type(state.board.board[r3][c3]) is Blank and not breaks_freedom_to_move_rule(r3, c3, state) and \
                                not all_neighbours_but_selected_are_blank(n4_of_spider, from_lst, state):
                            possible_moves.add((r3, c3))
    print(time.time()-t)
    return possible_moves


def get_possible_moves_ant(state):
    t = time.time()
    possible_moves = set()
    if not move_away_wont_break_hive(state):
        return possible_moves
    for r, _ in enumerate(state.board.board):
        for c, hexa in enumerate(state.board.board[r]):
            if (r, c) == (state.hexa_selected.r, state.hexa_selected.c):
                continue
            if type(state.board.board[r][c]) is not Blank:
                for n_r, n_c in get_cell_neighbours(r, c, state.board.height, state.board.width):
                    if type(state.board.board[n_r][n_c]) is Blank and \
                            not breaks_freedom_to_move_rule(n_r, n_c, state):
                        possible_moves.add((n_r, n_c))
    print(time.time()-t)
    return possible_moves


def get_possible_moves_beetle(state):
    t = time.time()
    possible_moves = set()
    neighbours_of_selected = get_cell_neighbours(state.hexa_selected.r, state.hexa_selected.c, state.board.height,
                                                 state.board.width)
    if move_away_wont_break_hive(state):
        for r, c in neighbours_of_selected:
            neighbours_of_neighbour = get_cell_neighbours(r, c, state.board.height, state.board.width)
            if not all_neighbours_but_selected_are_blank(neighbours_of_neighbour, [(state.hexa_selected.r, state.hexa_selected.c)], state):
                possible_moves.add((r, c))
    print(time.time()-t)
    return possible_moves


def get_possible_moves_grasshopper(state):
    t = time.time()
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
                                                                 [(state.hexa_selected.r, state.hexa_selected.c)], state):
                        possible_moves.add((r, c))
                        break
    print(time.time()-t)
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
    if fromm_board == state.start_tiles:
        state.board.board_count += 1
    state.prev_state = deepcopy(state)
    f_row, f_col = state.hexa_selected.r, state.hexa_selected.c
    dest_t = type(state.board.board[to_row][to_col])
    if dest_t is not Blank:
        # Must be a beetle
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
        state.board.board[to_row][to_col].r, state.board.board[to_row][to_col].c = to_row, to_col
        if type(state.hexa_selected) == Bee:
            if state.players_turn == W:
                state.bee_placed_white = True
                state.bee_pos_white = [to_row, to_col]
            else:
                state.bee_placed_black = True
                state.bee_pos_black = [to_row, to_col]
    increment_turn_count(state)
    state.players_turn = opp(state.players_turn)
    set_player_turn(state)
    state.hexa_selected = None
    state.possible_moves = set()


def player_able_to_move(state):
    s = deepcopy(state)
    for row in range(s.board.height):
        for col, hexa in enumerate(s.board.board[row]):
            if hexa.player == s.players_turn:
                s.hexa_selected = hexa
                if len(get_possible_moves_from_board(s)) > 0:
                    return True
    return False


def set_player_turn(state):
    for row in range(state.start_tiles.height):
        for col, hexa in enumerate(state.start_tiles.board[row]):
            if hexa.player == state.players_turn:
                return
    player_can_move = player_able_to_move(state)
    if not player_can_move:
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
