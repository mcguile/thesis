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

hexa_selected = None
offset_x, offset_y = 0, 0

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
    y = 0
    rack_surf = rack_top_surf if top else rack_bottom_surf
    rack_surf.fill((0, 0, 0, 0))
    for r, _ in enumerate(rack.board):
        x = 120
        y += 20
        for hexa in rack.board[r]:
            rack_surf.blit(hexa.image, (x, y))
            size = hexa.image.get_rect().size
            hexa.rect = pygame.Rect((x, y), size)
            x += 150


def draw_placed_tiles():
    x_o, y_o = 0, 0
    drag_surf.fill((0, 0, 0, 0))
    for r, _ in enumerate(board.board):
        x, y = x_o, y_o
        for c, hexa in enumerate(board.board[r]):
            drag_surf.blit(hexa.image, (x, y))
            size = hexa.image.get_rect().size
            hexa.rect = pygame.Rect((x, y), size)
            y += 30 if c % 2 == 0 else -30
            x += 52
        y_o += 61


def get_possible_moves_from_rack(player):
    possible_moves = []
    for r, _ in enumerate(board.board):
        for c, hexa in enumerate(board.board[r]):
            neighbours = get_cell_neighbours(r, c)
            valid_placement = True
            found_own_tile = False
            for x, y in neighbours:
                if board.board[x][y].player == player:
                    found_own_tile = True
                    # print((r,c), f'found {player} at', (x,y))
                elif board.board[x][y].player == opp(player) or board.board[r][c].player == opp(player):
                    # print((r,c),f'found {opp(player)} at', (x,y))
                    valid_placement = False
            if found_own_tile and valid_placement:
                board.board[r][c].image = pygame.image.load(f'../img_assets/possible.png')
                possible_moves.append((r, c))
                # print(f'placing possible at {(r,c)}')
    return possible_moves


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
    setup_racks(bottom_rack, top=False)
    get_possible_moves_from_rack(W)
    draw_placed_tiles()


def event_handler_select_tile(event, dragging):
    global hexa_selected
    img_selected = pygame.image.load('../img_assets/selected.png')
    if event.type == pygame.MOUSEBUTTONDOWN and not dragging:
        _, y = event.pos
        if y < RACK_HEIGHT:
            for row in range(top_rack.width):
                for hexa in top_rack.board[row]:
                    if hexa.rect.collidepoint(event.pos) and type(hexa) != Blank:
                        if hexa_selected:
                            hexa_selected.image = pygame.image.load(hexa_selected.image_loc)
                        hexa.image.blit(img_selected, (0, 0))
                        hexa_selected = hexa
        elif y > HEIGHT - RACK_HEIGHT:
            for row in range(bottom_rack.width):
                for hexa in bottom_rack.board[row]:
                    x, y = event.pos
                    y = y - HEIGHT + RACK_HEIGHT
                    if hexa.rect.collidepoint((x, y)) and type(hexa) != Blank:
                        if hexa_selected:
                            hexa_selected.image = pygame.image.load(hexa_selected.image_loc)
                        hexa.image.blit(img_selected, (0, 0))
                        hexa_selected = hexa
        else:
            for row in range(board.width):
                for hexa in board.board[row]:
                    if hexa.rect.collidepoint(event.pos) and type(hexa) != Blank:
                        if hexa_selected:
                            hexa_selected.image = pygame.image.load(hexa_selected.image_loc)
                        hexa.image.blit(img_selected, (0, 0))
                        hexa_selected = hexa


def event_handler_board_drag(event, dragging):
    global offset_x
    global offset_y
    event_handler_select_tile(event, dragging)

    if event.type == pygame.MOUSEBUTTONDOWN and not dragging and drag_surf_rect.collidepoint(event.pos):
        dragging = True
        mouse_x, mouse_y = event.pos
        offset_x = drag_surf_rect.x - mouse_x
        offset_y = drag_surf_rect.y - mouse_y
    elif event.type == pygame.MOUSEMOTION and dragging:
        mouse_x, mouse_y = event.pos
        drag_surf_rect.x = mouse_x + offset_x
        drag_surf_rect.y = mouse_y + offset_y
    elif event.type == pygame.MOUSEBUTTONUP and dragging:
        offset_x, offset_y = 0, 0
        dragging = False
    return dragging


def run_game():
    dragging = False
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            else:
                #dragging = event_handler_board_drag(event, dragging)
                event_handler_select_tile(event, dragging)

        draw_board()
        pygame.display.update()
        clock.tick(30)


run_game()
# print(get_possible_moves_from_rack(B))
