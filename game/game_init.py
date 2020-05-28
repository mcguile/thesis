import pygame
import sys
from pygame.locals import *
from insects import *
from board import *

W = 'white'
B = 'black'

debug = True
WIDTH = 900
HEIGHT = 900
RACK_HEIGHT = 160

clock = pygame.time.Clock()

# Setup the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
pygame.display.set_caption('Hive!')
bg = pygame.image.load('../img_assets/wood.png')
rack_top_surf = pygame.Surface((WIDTH, RACK_HEIGHT), pygame.SRCALPHA, 32).convert_alpha()
rack_bottom_surf = pygame.Surface((WIDTH, RACK_HEIGHT), pygame.SRCALPHA, 32).convert_alpha()
drag_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA, 32).convert_alpha()
drag_surf_rect = drag_surf.get_rect()
player_move = 'white'

board = Board(40, 40)

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

board.board[5][6] = Spider(W)
board.board[5][7] = Spider(B)
board.board[6][5] = Bee(W)
board.board[6][6] = Bee(B)
board.board[6][7] = Beetle(W)
board.board[7][6] = Grasshopper(B)
board.board[7][7] = Ant(W)


def setup_racks(rack, top=True):
    y = 0  # if start == 0 else RACK_HEIGHT - 60
    for r, _ in enumerate(rack.board):
        x = 120
        y += 20  # if start == 0 else -20
        for _, hexa in enumerate(rack.board[r]):
            rack_surf = rack_top_surf if top else rack_bottom_surf
            rack_surf.blit(hexa.image, (x, y))
            x += 150


def draw_placed_tiles():
    x_o, y_o = 0, 0
    for r, _ in enumerate(board.board):
        x, y = x_o, y_o
        for c, hexa in enumerate(board.board[r]):
            drag_surf.blit(hexa.image, (x, y))
            y += 30 if c % 2 == 0 else -30
            x += 52
        y_o += 61


# def draw_possible_moves():
#     x_o, y_o = 0, 0
#     for r, _ in enumerate(board.board[3:-3]):
#         x, y = x_o, y_o
#         for c, hexa in enumerate(board.board[r + 3]):
#
#             drag_surf.blit(hexa.image, (x, y))
#             y += 30 if c % 2 == 0 else -30
#             x += 52
#         y_o += 61


def get_possible_moves_from_rack(player):
    global debug
    possible_moves = []
    f_x, f_y, v_x, v_y = None, None, None, None
    for r, _ in enumerate(board.board):
        for c, hexa in enumerate(board.board[r]):
            neighbours = get_cell_neighbours(r, c)
            valid_placement = True
            found_own_tile = False
            for x, y in neighbours:
                if board.board[x][y].player == player:
                    found_own_tile = True
                    f_x, f_y = x, y
                elif board.board[x][y].player == opp(player):
                    valid_placement = False
                    v_x, v_y = x, y
            # if debug and found_own_tile:
            #     print((r, c), (f_x, f_y), (v_x, v_y))
            if found_own_tile and valid_placement:
                board.board[r][c].image = pygame.image.load(f'../img_assets/possible.png')
    debug = False


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


def draw_board():
    screen.fill((0, 0, 0))
    screen.blit(bg, (0, 0))
    screen.blit(drag_surf, drag_surf_rect)
    screen.blit(rack_top_surf, (0, 0))
    screen.blit(rack_bottom_surf, (0, HEIGHT - RACK_HEIGHT))
    setup_racks(top_rack)
    setup_racks(bottom_rack, False)
    get_possible_moves_from_rack(W)
    draw_placed_tiles()


def get_human_move():
    dragging = False
    offset_x, offset_y = 0, 0
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and not dragging and drag_surf_rect.collidepoint(event.pos):
                dragging = True
                x, y = event.pos
                offset_x, offset_y = drag_surf_rect.centerx - x, drag_surf_rect.centery - y
            if event.type == pygame.MOUSEMOTION and dragging:
                mouse_x, mouse_y = event.pos
                drag_surf_rect.centerx = mouse_x + offset_x
                drag_surf_rect.centery = mouse_y + offset_y
            elif event.type == pygame.MOUSEBUTTONUP and dragging:
                dragging = False

        draw_board()
        pygame.display.update()
        clock.tick(30)


def run_game():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            else:
                get_human_move()


run_game()
# print(get_cell_neighbours(5,6))