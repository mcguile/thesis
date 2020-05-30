import pygame
import sys
from pygame.locals import *
from insects import *
from board import *

W = 'white'
B = 'black'

debug = True
WIDTH = 1000
HEIGHT = 1000
RACK_HEIGHT = 160

clock = pygame.time.Clock()

# Setup the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
pygame.display.set_caption('Hive!')
bg = pygame.image.load('../img_assets/wood.png')
img_selected = pygame.image.load('../img_assets/selected.png')
rack_top_surf = pygame.Surface((WIDTH, RACK_HEIGHT), pygame.SRCALPHA, 32).convert_alpha()
rack_bottom_surf = pygame.Surface((WIDTH, RACK_HEIGHT), pygame.SRCALPHA, 32).convert_alpha()
drag_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA, 32).convert_alpha()
drag_surf_rect = drag_surf.get_rect()
drag_surf_rect.x += 23
hexa_size = pygame.image.load('../img_assets/blank.png').get_rect().size
hexa_width, _ = hexa_size
players_turn = W

board = Board(16, 16)
top_rack = Board(3, 5)
bottom_rack = Board(3, 5)

top_rack.board[0][0] = Ant(W)
top_rack.board[1][0] = Ant(W)
top_rack.board[2][0] = Ant(W)
top_rack.board[0][1] = Beetle(W)
top_rack.board[1][1] = Beetle(W)
top_rack.board[0][2] = Grasshopper(W)
top_rack.board[1][2] = Grasshopper(W)
top_rack.board[2][2] = Grasshopper(W)
top_rack.board[0][3] = Bee(W)
top_rack.board[0][4] = Spider(W)
top_rack.board[1][4] = Spider(W)

bottom_rack.board[0][0] = Ant(B)
bottom_rack.board[1][0] = Ant(B)
bottom_rack.board[2][0] = Ant(B)
bottom_rack.board[0][1] = Beetle(B)
bottom_rack.board[1][1] = Beetle(B)
bottom_rack.board[0][2] = Grasshopper(B)
bottom_rack.board[1][2] = Grasshopper(B)
bottom_rack.board[2][2] = Grasshopper(B)
bottom_rack.board[0][3] = Bee(B)
bottom_rack.board[0][4] = Spider(B)
bottom_rack.board[1][4] = Spider(B)


def setup_racks(rack, top=True):
    y = 0 if top else 20
    rack_surf = rack_top_surf if top else rack_bottom_surf
    rack_surf.fill((0, 0, 0, 0))
    for r, _ in enumerate(rack.board):
        x = int(WIDTH / 6) - hexa_width / 2
        y += 20
        for hexa in rack.board[r]:
            rack_surf.blit(hexa.image, (x, y))
            hexa.rect = pygame.Rect((x, y), hexa_size)
            x += int(WIDTH / 6)


def draw_placed_tiles(possible_moves):
    x_o, y_o = drag_surf_rect.x, drag_surf_rect.y
    drag_surf.fill((0, 0, 0, 0))
    for r, _ in enumerate(board.board):
        x, y = x_o, y_o
        for c, hexa in enumerate(board.board[r]):
            if type(hexa) is Blank:
                if (r, c) in possible_moves:
                    hexa.image = hexa.image_playable
                else:
                    hexa.image = hexa.image_o
            drag_surf.blit(hexa.image, (x, y))
            hexa.rect = pygame.Rect((x, y), hexa_size)
            y += 30 if c % 2 == 0 else -30
            x += 52
        y_o += 60


def get_possible_moves(player):
    possible_moves = set()
    for r, _ in enumerate(board.board):
        for c, hexa in enumerate(board.board[r]):
            neighbours = get_cell_neighbours(r, c)
            valid_placement = True
            found_own_tile = False
            for x, y in neighbours:
                if board.board[x][y].player == player:
                    found_own_tile = True
                elif board.board[x][y].player == opp(player) or type(board.board[r][c]) != Blank:
                    valid_placement = False
            if found_own_tile and valid_placement:
                possible_moves.add((r, c))
    return possible_moves


def get_possible_first_moves_black():
    return set(get_cell_neighbours(board.width // 2, board.height // 2))


def get_cell_neighbours(r, c):
    neighbours = []
    min_r, max_r, min_c, max_c = get_shape_minmax_rowcol(r, c)
    for row in range(min_r, max_r + 1):
        for col in range(min_c, max_c + 1):
            if col == c and row == r:
                continue
            elif (c % 2 == 0) and ((col == c + 1 and row == r + 1) or (row == r + 1 and col == c - 1)):
                continue
            elif (c % 2 == 1) and ((col == c - 1 and row == r - 1) or (row == r - 1 and col == c + 1)):
                continue
            else:
                neighbours.append((row, col))
    return neighbours


def get_shape_minmax_rowcol(r, c):
    min_r = max(r - 1, 0)
    max_r = min(r + 1, board.height - 1)
    min_c = max(c - 1, 0)
    max_c = min(c + 1, board.width - 1)
    return min_r, max_r, min_c, max_c


def opp(player):
    return B if player == W else W


def draw_board(possible_moves):
    screen.fill((0, 0, 0))
    screen.blit(pygame.transform.scale(bg, (WIDTH, HEIGHT)), (0, 0))
    screen.blit(drag_surf, drag_surf_rect)
    screen.blit(rack_top_surf, (0, 0))
    screen.blit(rack_bottom_surf, (0, HEIGHT - RACK_HEIGHT))
    setup_racks(top_rack)
    setup_racks(bottom_rack, top=False)
    draw_placed_tiles(possible_moves)


def valid_move():
    # possible_moves = get_possible_moves_from_rack(players_turn)

    return True


def move_to_board(event, last_event_pos, hexa_sel, hexa_sel_pos, possible_moves):
    global players_turn
    if pygame.Rect(last_event_pos, hexa_size).collidepoint(event.pos):
        hexa_sel.image = pygame.image.load(hexa_sel.image_loc)
        return None, possible_moves
    for row in range(board.width):
        for col, hexa in enumerate(board.board[row]):
            if hexa.rect.collidepoint(event.pos) and (row, col) in possible_moves:
                hexa_sel_pos[0].board[hexa_sel_pos[1][0]][hexa_sel_pos[1][1]] = Blank()
                board.board[row][col] = hexa_sel
                board.board[row][col].image = pygame.image.load(board.board[row][col].image_loc)
                players_turn = opp(players_turn)
                return None, set()
    return hexa_sel, possible_moves


def iter_top_rack(event, hexa_sel, hexa_sel_pos):
    for row in range(top_rack.width):
        for col, hexa in enumerate(top_rack.board[row]):
            if hexa.rect.collidepoint(event.pos) and type(hexa) != Blank and hexa.player == players_turn:
                if hexa_sel:
                    hexa_sel.image = pygame.image.load(hexa_sel.image_loc)
                hexa.image.blit(img_selected, (0, 0))
                hexa_sel = hexa
                hexa_selected_pos = (top_rack, (row, col))
                return hexa_sel, hexa_selected_pos
    return hexa_sel, hexa_sel_pos


def iter_bottom_rack(event, hexa_sel, hexa_sel_pos):
    mouse_x, mouse_y = event.pos
    for row in range(bottom_rack.width):
        for col, hexa in enumerate(bottom_rack.board[row]):
            hexa.rect.y = hexa.rect.y + HEIGHT - RACK_HEIGHT
            if hexa.rect.collidepoint((mouse_x, mouse_y)) and type(hexa) != Blank and hexa.player == players_turn:
                if hexa_sel:
                    hexa_sel.image = pygame.image.load(hexa_sel.image_loc)
                hexa.image.blit(img_selected, (0, 0))
                hexa_sel = hexa
                hexa_sel_pos = (bottom_rack, (row, col))
                return hexa_sel, hexa_sel_pos
    return hexa_sel, hexa_sel_pos


def iter_board(event, hexa_sel, hexa_sel_pos):
    for row in range(board.width):
        for col, hexa in enumerate(board.board[row]):
            if hexa.rect.collidepoint(event.pos) and type(hexa) != Blank and hexa.player == players_turn:
                if hexa_sel:
                    hexa_sel.image = pygame.image.load(hexa_sel.image_loc)
                hexa.image.blit(img_selected, (0, 0))
                hexa_sel = hexa
                hexa_sel_pos = (board, (row, col))
                return hexa_sel, hexa_sel_pos
    return hexa_sel, hexa_sel_pos


def move_white_first(first_move, hexa_sel, hexa_sel_pos):
    global players_turn
    r, c = board.width // 2, board.height // 2
    if first_move:
        hexa_sel_pos[0].board[hexa_sel_pos[1][0]][hexa_sel_pos[1][1]] = Blank()
        board.board[r][c] = hexa_sel
        board.board[r][c].image = pygame.image.load(board.board[r][c].image_loc)
        players_turn = B
        return False, None
    return first_move, hexa_sel


def run_game():
    first_move_white = True
    first_move_black = True
    hexa_selected = None
    hexa_selected_pos = (None, (0, 0))
    last_event_pos = (0, 0)
    possible_moves = set()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONUP:
                if hexa_selected:
                    hexa_selected, possible_moves = move_to_board(event, last_event_pos, hexa_selected,
                                                                      hexa_selected_pos, possible_moves)
                else:
                    mouse_x, mouse_y = event.pos
                    if mouse_y < RACK_HEIGHT:
                        hexa_selected, hexa_selected_pos = iter_top_rack(event, hexa_selected, hexa_selected_pos)
                        first_move_white, hexa_selected = move_white_first(first_move_white, hexa_selected, hexa_selected_pos)
                    elif mouse_y > HEIGHT - RACK_HEIGHT:
                        hexa_selected, hexa_selected_pos = iter_bottom_rack(event, hexa_selected, hexa_selected_pos)
                    else:
                        hexa_selected, hexa_selected_pos = iter_board(event, hexa_selected, hexa_selected_pos)

                    if hexa_selected:
                        if not first_move_white and first_move_black:
                            possible_moves = get_possible_first_moves_black()
                            first_move_black = False
                        else:
                            possible_moves = get_possible_moves(players_turn)
                last_event_pos = event.pos

        draw_board(possible_moves)
        pygame.display.update()
        clock.tick(30)


run_game()
# print(get_possible_moves_from_rack(B))
